local char = string.char
local type = type
local sub = string.sub
local tconcat = table.concat

local basedictdecompress = {}
for i = 0, 255 do
    basedictdecompress[char(i, 0)] = char(i)
end

-- dictAddB() and decompress() from https://github.com/Rochet2/lualzw/tree/master
local function dictAddB(str, dict, a, b)
    if a >= 256 then
        a, b = 0, b+1
        if b >= 256 then
            dict = {}
            b = 1
        end
    end
    dict[char(a,b)] = str
    a = a+1
    return dict, a, b
end

local function decompress(input)
    if type(input) ~= "string" then
        return nil, "string expected, got "..type(input)
    end

    if #input < 1 then
        return nil, "invalid input - not a compressed string"
    end

    local control = sub(input, 1, 1)
    if control == "u" then
        return sub(input, 2)
    elseif control ~= "c" then
        return nil, "invalid input - not a compressed string"
    end
    input = sub(input, 2)
    local len = #input

    if len < 2 then
        return nil, "invalid input - not a compressed string"
    end

    local dict = {}
    local a, b = 0, 1

    local result = {}
    local n = 1
    local last = sub(input, 1, 2)
    result[n] = basedictdecompress[last] or dict[last]
    n = n+1
    for i = 3, len, 2 do
        local code = sub(input, i, i+1)
        local lastStr = basedictdecompress[last] or dict[last]
        if not lastStr then
            return nil, "could not find last from dict. Invalid input?"
        end
        local toAdd = basedictdecompress[code] or dict[code]
        if toAdd then
            result[n] = toAdd
            n = n+1
            dict, a, b = dictAddB(lastStr..sub(toAdd, 1, 1), dict, a, b)
        else
            local tmp = lastStr..sub(lastStr, 1, 1)
            result[n] = tmp
            n = n+1
            dict, a, b = dictAddB(tmp, dict, a, b)
        end
        last = code
    end
    return tconcat(result)
end

local file_path = arg[1]
if not file_path then
    print("Usage: lua bootstrap.lua <compressed.bin> [args...]")
    os.exit(1)
end

local script_args = {}
for i = 2, #arg do
    table.insert(script_args, arg[i])
end

local file, err = io.open(file_path, "rb")
if not file then
    print("Error opening file: " .. tostring(err))
    os.exit(1)
end
local compressed_data = file:read("*all")
file:close()

local decompressed_code, decomp_err = decompress(compressed_data)
if not decompressed_code then
    print("Decompression failed: " .. tostring(decomp_err))
    os.exit(1)
end

local load_chunk = loadstring or load
local chunk, compile_err = load_chunk(decompressed_code, "=" .. file_path)

if not chunk then
    print("Compilation error: " .. tostring(compile_err))
    os.exit(1)
end

local unpack = unpack or table.unpack
local success, run_err = pcall(chunk, unpack(script_args))
if not success then
    print("Runtime error: " .. tostring(run_err))
    os.exit(1)
end