from PIL import Image

patterns = ["stripes", "checkerboard", "blocks", 'waves']


def generate_pattern(width, height, colors, pattern, verbose=False):
    img = []
    if pattern == "stripes":
        bloque_height = height // len(colors)
        for i in range(height):
            color = colors[i // bloque_height % len(colors)]
            img.extend([color] * width)

    elif pattern == "checkerboard":
        for y in range(height):
            for x in range(width):
                color = colors[(x // 8 + y // 8) % len(colors)]
                img.append(color)

    elif pattern == "blocks":
        block_size = 64
        for y in range(height):
            for x in range(width):
                color = colors[((x // block_size) + (y // block_size)) % len(colors)]
                img.append(color)
                
    elif pattern == "waves":
        freq = 64
        for y in range(height):
            for x in range(width):
                color = colors[(x + y) // freq % len(colors)]
                img.append(color)
    
    else:
        raise ValueError('Unrecognized pattern, existing patterns are: "stripes", "checkerboard", "blocks" and "waves"')
    if verbose:
        print(f"Pattern selected: {pattern}")
    return img


def create_gif(lua_file: str, output_file: str, verbose: bool = False, pattern: str = "stripes"):
    with open(lua_file, 'r') as lua_f:  # open .lua file
        lua_code = lua_f.read()
    
    width = 2365
    height = 2338
    colors =[
        (255, 0, 0),    # rojo
        (0, 255, 0),    # verde
        (0, 0, 255),    # azul
        (255, 255, 0),  # amarillo
    ]
    # Generate color index pattern
    colors_index = list(range(len(colors)))
    pixels = generate_pattern(width, height, colors_index, pattern, verbose)
    
    # Create color_palett
    color_palett = []
    for (r, g, b) in colors:
        color_palett.extend([r, g, b])
    # start_code: Closes the string opened by the height and width fields, and allows arbitrary code to be stored
    start_code='''"
'''
    # end_code: Starts a multi-line comment with the rest of the image
    end_code = '''
--[['''
    payload = start_code + lua_code + end_code
    # Convert to bytes using UTF-8 encoding and then to a list of integers
    payload = list(payload.encode('utf-8'))
    color_palett += payload
    if len (color_palett) > 768:
        print("Error: The color palette and payload together exceed 768 bytes.")
        return
    if verbose:
        print('Empty space padded:', 768 - len(color_palett), 'bytes.')
    color_palett += [0] * (768 - len(color_palett)) # Pad up to 256 * 3 bytes

    img = Image.new('P', (width, height)) # Create type P image using color_palett (mode 'P' = indexed)
    img.putdata(pixels) # LZW compressed color index
    img.putpalette(color_palett)
    img.save(output_file, format='GIF', optimize=True)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write("]]")