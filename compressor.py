import re
import string
import sys

class LuaMinifier:
    def __init__(self, code):
        self.code = code

    def remove_comments(self):
        self.code = re.sub(r'--\[\[.*?\]\]', '', self.code, flags=re.DOTALL)
        self.code = re.sub(r'--.*$', '', self.code, flags=re.MULTILINE)

    def compress_whitespace(self):
        self.code = re.sub(r'\s+', ' ', self.code)
        
        tokens = [r'\+', r'-', r'\*', r'/', r'=', r',', r'\(', r'\)', r'\{', r'\}', r'\[', r'\]', r';', r':']
        for token in tokens:
            self.code = re.sub(rf'\s*({token})\s*', r'\1', self.code)
        
        self.code = self.code.strip()

    def minify(self):
        self.remove_comments()
        self.compress_whitespace()
        return self.code

def dict_add_a(byte_sequence, dictionary, a, b):
    if a >= 256:
        a = 0
        b += 1
        if b >= 256:
            dictionary.clear()
            b = 1
    dictionary[byte_sequence] = chr(a) + chr(b)
    a += 1
    return dictionary, a, b

def lualzw_compress(input_bytes):
    length = len(input_bytes)
    if length <= 1:
        return b"u" + input_bytes

    basedictcompress = {bytes([i]): chr(i) + '\x00' for i in range(256)}
    dictionary = {}
    a, b = 0, 1

    result = ["c"]
    resultlen = 1
    word = b""

    for i in range(length):
        c = bytes([input_bytes[i]])
        wc = word + c
        if wc not in basedictcompress and wc not in dictionary:
            write = basedictcompress.get(word) or dictionary.get(word)
            
            if write is None and word:
                write = "".join(basedictcompress[bytes([b])] for b in word)
            elif write is None:
                raise Exception("algorithm error, could not fetch word")
                
            result.append(write)
            resultlen += len(write)
            
            if length <= resultlen:
                return b"u" + input_bytes
                
            dictionary, a, b = dict_add_a(wc, dictionary, a, b)
            word = c
        else:
            word = wc

    write = basedictcompress.get(word) or dictionary.get(word)
    if write is None and word:
        write = "".join(basedictcompress[bytes([b])] for b in word)
    elif write is None:
        raise Exception("algorithm error, could not fetch trailing word")
        
    result.append(write)
    resultlen += len(write)
    if length <= resultlen:
        return b"u" + input_bytes

    return "".join(result).encode('latin-1')


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compressor.py <input.lua> <output.bin>")
        exit(1)

    try:
        with open(sys.argv[1], "rb") as r: 
            source_lua = r.read().decode('utf-8', errors='ignore')
    except FileNotFoundError:
        print("Error: input file not found. Make sure it's in the same directory.")
        exit(1)

    minifier = LuaMinifier(source_lua)
    minified_lua = minifier.minify()

    minified_bytes = minified_lua.encode('utf-8')

    compressed_data = lualzw_compress(minified_bytes)

    with open(sys.argv[2], "wb") as w: 
        w.write(compressed_data)

    print(f"Complete!")
    print(f"  Source: {len(source_lua)} characters")
    print(f"  Output (c.bin): {len(compressed_data)} bytes saved as raw binary.")