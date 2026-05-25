# lua-compressor
Python script that slightly strips the code from unnecessary elements and compresses using LZW. Compatible with ComputerCraft.

## Usage
To compress:
`python compressor.py input.lua compressed.bin`

To decompress and run:
`lua bootstrap.lua compressed.bin`

## Extra
This was made primarily to save space for programs in ComputerCraft minecraft mod (hence why the bootstrap is in lua) in less than a day, so bugs are expected.
