import sys
import os
import math
from operator import itemgetter
from bitstring import BitArray

def main():

    if len(sys.argv) > 2:
        input_file_name     = sys.argv[1]
        output_file_name    = sys.argv[2]

        print("File Name:", input_file_name)
        input_file_length_in_bytes = os.path.getsize(input_file_name)
        print("File Size:", input_file_length_in_bytes, "Bytes")
        
        print("\nReading File...")
        with open(input_file_name, "rb") as f:
            file_data = BitArray(bytes = f.read()) # Storing file data in memory

        # Reading overhead
        max_code_length = int(file_data[:8].uint)
        max_code_bits   = int(math.ceil(math.log(max_code_length + 1, 2)))
        padding_size    = int(file_data[8:11].uint)

        print("\nReading Symbol Codes...")
        # Reading symbols codes
        symbols_data    = file_data[11:]
        symbols = {}
        pos = 0
        for s in range(256):
            # Check if symbols has code
            if symbols_data[pos] == True:
                pos += 1
                posj = pos + max_code_bits
                # Reading code
                code_size = int(symbols_data[pos:posj].uint)
                code = symbols_data[posj:(posj + code_size)]
                pos = posj + code_size

                # Storing code in symbols dict
                if code_size not in symbols:
                    symbols[code_size] = {}
                symbols[code_size][code.bin] =  BitArray(uint = s, length = 8)
            else: 
                pos += 1

        # Skipping padding
        pos += padding_size

        print("\nReading and Writing Compressed Data...")
        # Reading compressed data
        data = symbols_data[pos:]
        final_data = BitArray()
        i = 0
        with open(output_file_name, "wb") as w:
            while i < data.length:
                buffer = BitArray(data[i:(i + max_code_length)]) 
                
                for size in symbols:
                    if size <= 1:
                        code = BitArray(uint = buffer[0], length=1)
                    else:
                        code = buffer[:size]
                    # Check if code exists at symbols dict
                    if code.bin in symbols[size]:
                        symbols[size][code.bin].tofile(w) # Save symbol
                        break
                i += size

        output_file_length_in_bytes = os.path.getsize(output_file_name)

        print("\nFile Name:           ", output_file_name)
        print("Compressed file size:", output_file_length_in_bytes, "Bytes")

if __name__ == "__main__":
    main()