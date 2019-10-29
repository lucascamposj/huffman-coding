import sys
import os
import math
from operator import itemgetter
from bitstring import BitStream, BitArray, ConstBitStream
# from bitarray import BitArray

class Tree:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.frequency = 0
        self.code = BitArray()
        self.code_length = None
        
    def __str__(self):
        return str(self.data)

class Node(Tree):
    pass

class EmptyNode(Tree):
    pass

def code(root):
    if(root.left is not None):
        root.left.code  = root.code.copy()
        root.left.code.append('0b0')
        root.left.code_length = root.left.code.length
        code(root.left)
    if(root.right is not None):
        root.right.code = root.code.copy()
        root.right.code.append('0b1')
        root.right.code_length = root.right.code.length
        code(root.right)
    return

def main():

    if len(sys.argv) > 2:
        input_file_name     = sys.argv[1]
        output_file_name    = sys.argv[2]

        print("File Name:", input_file_name)
        input_file_length_in_bytes = os.path.getsize(sys.argv[1])
        print("File Size:", input_file_length_in_bytes, "Bytes\n")

        print("Reading File...")
        # Reading input file
        with open(sys.argv[1], "rb") as f:
            symbols = [None] * 256
            file_data = BitArray(bytes = f.read())

        for b in range(0, file_data.length, 8):
            byte = int(file_data[b:b+8].uint)

            if symbols[byte] == None:
                symbols[byte] = Node(b)
            symbols[byte].frequency += 1

        # Getting list only with symbols
        symbols_fitered = list(filter(None, symbols.copy()))
        symbols_ordered = sorted(symbols_fitered, key=lambda x: x.frequency, reverse=True)

        # Build Huffman tree
        print("Building Huffman Tree...")
        s = symbols_ordered.copy()
        while len(s) > 1:
            root = EmptyNode(None)
            node_left = s[-1]
            node_right = s[-2]
            del s[-2:]
            root.left = node_left
            root.right = node_right
            root.frequency = root.left.frequency + root.right.frequency
            new_symbol = root
            s.append(new_symbol)
            s = sorted(s, key=lambda x: x.frequency, reverse=True)

        # Build codes from Huffman Tree
        code(root) 

        # Get info from code
        max_code_length = symbols_ordered[-1].code_length
        max_code_bits = int(math.ceil(math.log(max_code_length + 1, 2)))

        # Adding padding bits to overhead
        overhead = BitArray(uint = max_code_length, length = 8)
        overhead.append('0b000')

        # Adding symbols codes to overhead
        for symbol in symbols:
            if(symbol is None):
                overhead.append('0b0')
            else:
                overhead.append('0b1')
                overhead.append(BitArray(uint= symbol.code_length,length = max_code_bits))
                overhead.append(symbol.code)

        # Count padding
        length_total = overhead.length
        for s in symbols_ordered:
            length_total += s.frequency * s.code_length
        
        # Overwrite padding quantity
        padding = 8 - length_total % 8
        if padding < 8:
            pad = BitArray(uint = padding, length = 3)
            overhead.overwrite(pad, 8)

        # Apply padding
        if padding != 0:
            overhead.append(BitArray(uint = 0, length = padding))
        overhead_len  = overhead.length

        print("Writing File...")
        # Building final compressed data
        final_data = overhead
        for b in range(0, file_data.length, 8):
            byte_int = int(file_data[b:b+8].uint)
            final_data.append(symbols[byte_int].code)
        final_data_len = final_data.length

        # Write compressed data to output file
        with open(output_file_name, "wb") as w:
            final_data.tofile(w)

        # Statistics from compression
        entropy         = 0
        avg_code_len    = final_data_len/input_file_length_in_bytes
        symbols_quantity = input_file_length_in_bytes
        for s in symbols_ordered:
            p = s.frequency / symbols_quantity
            entropy         += p * math.log(p, 2) # entropy
        entropy       = -1 * entropy

        print("\n--------Statistics--------")
        print("Entropy:              %.3f Bits/symbol" % entropy)
        print("Average Code Length:  %.3f Bits/symbol" % avg_code_len)
        print("Compressed data size:", (final_data_len - overhead_len)/8, "Bytes")
        print("Overhead:            ", overhead_len/8, "Bytes")


        print("\nFile Name:           ", output_file_name)
        print("Compressed file size:", int(final_data_len/8), "Bytes")
    else:
        print("Enter input and output file names")

if __name__ == "__main__":
    main()