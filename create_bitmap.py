import math

def create_bitmap_lua(lua_file: str, output_file: str, verbose: bool = False):
    with open(lua_file, 'r') as lua_f:  # open .lua file
        lua_code = lua_f.read()

    file_size_field = """[[--"""
    end_header = """
]] = 0
"""

    code_data = lua_code.encode('utf-8')
    while  ((len(code_data) + len(end_header.encode('utf-8'))) % 4) != 0:   # must be a multiple of 4
        end_header = end_header[:-1] + '1' + end_header[-1] #  insert character in penultimate position
  

    full_code_size = (len(code_data) + len(end_header.encode('utf-8')))

    # Dimensiones de la imagen
    width = math.ceil(math.sqrt(full_code_size/4))
    height = width
    
    bpp = 32  #  Number of bits per pixel (4 bytes)
    raw_image_size = int(height * width * bpp/8)
    padding_size = raw_image_size - full_code_size
    
    if verbose:
        print(f'Image width: {width}')
        print(f'Image height: {height}')
        print(f'Padding bytes: {padding_size}')
        print(f'Resulting file size: {raw_image_size} bytes')


    file_size_field_bytes = file_size_field.encode('utf-8')

    with open(output_file, "wb") as f:
        # ----- Write BMP Header -----   14 bytes
        f.write(b'BM')  # 2
        f.write(file_size_field_bytes[::-1])  # 4
                
        f.write((0).to_bytes(2, 'little'))      #  depends on the application that creates the image, if created manually can be 0
        f.write((0).to_bytes(2, 'little'))      #  depends on the application that creates the image, if created manually can be 0
        f.write((14 + 40).to_bytes(4, 'little'))    # Offset where the pixel array (bitmap data) can be found 

        # ----- DIB Header ----- 40 bytes
        f.write((40).to_bytes(4, 'little'))     # Number of bytes in the DIB header (from this point)
        f.write(width.to_bytes(4, 'little'))    # Width of the bitmap in pixels
        f.write(height.to_bytes(4, 'little'))   # Height of the bitmap in pixels. Positive for bottom to top pixel order.
    
        
        f.write((1).to_bytes(2, 'little'))  # Number of color planes being used
        f.write(bpp.to_bytes(2, 'little'))  # Number of bits per pixel
        f.write((0).to_bytes(4, 'little'))  # BI_BITFIELDS, no pixel array compression used
        f.write(raw_image_size.to_bytes(4, 'little'))    # IMPORTANT, SIZE OF THE RAW IMAGE
        f.write((2835).to_bytes(4, 'little'))   # Print resolution of the image, horizontal
        f.write((2835).to_bytes(4, 'little'))   # Print resolution of the image, vertical
        f.write((0).to_bytes(4, 'little'))  # Number of colors in the palette
        f.write((0).to_bytes(4, 'little'))  # 0 means all colors are important


        f.write(end_header.encode("utf-8")) # end of header data

        f.write(lua_code.encode("utf-8")) # Insert Lua code

        # Adding padding
        if padding_size > 3:
            f.write("\n--".encode("utf-8"))
            for _ in range(padding_size-3):
                f.write("0".encode("utf-8"))

        elif padding_size > 0:
            for _ in range(padding_size):
                f.write("\n".encode("utf-8"))





def create_bitmap_javascript(javascript_file: str, output_file: str, verbose: bool = False):

    with open(javascript_file, 'r') as javascript_f:  # Abrimos el archivo PDF
        codigo = javascript_f.read()

    file_size_field =  """  */"""
    end_header = """*/=0;\n"""
    code_data = codigo.encode('utf-8')


    # Calculations related to file size and padding

    while  ((len(code_data) + len(end_header.encode('utf-8'))) % 4) != 0:   # ha de ser multiple de 4
        end_header = end_header[:-2] + '1' + end_header[-2] + end_header[-1] #  insert character in -2 position
  
    full_code_size = (len(code_data) + len(end_header.encode('utf-8')))
    width = math.ceil(math.sqrt(full_code_size/4))
    height = width
    
    bpp = 32  #  Number of bits per pixel (4 bytes)
    raw_image_size = int(height * width * bpp/8)
    padding_size = raw_image_size - full_code_size
    
    if verbose:
        print(f'Image width: {width}')
        print(f'Image height: {height}')
        print(f'Padding bytes: {padding_size}')
        print(f'Resulting file size: {raw_image_size} bytes')

    file_size_field_bytes = file_size_field.encode('utf-8')

    with open(output_file, "wb") as f:
        # ----- Escribir Encabezado BMP -----   14 bytes
        f.write(b'BM')  # 2
        f.write(file_size_field_bytes[::-1])  # 4
                
        # f.write(file_size_field.to_bytes(4, 'little'))  
        f.write((0).to_bytes(2, 'little'))      #  depends on the application that creates the image, if created manually can be 0
        f.write((0).to_bytes(2, 'little'))      #  depends on the application that creates the image, if created manually can be 0
        f.write((14 + 40).to_bytes(4, 'little'))    # Offset where the pixel array (bitmap data) can be found 

        # ----- Encabezado DIB ----- 40 bytes
        f.write((40).to_bytes(4, 'little'))     # Number of bytes in the DIB header (from this point)
        f.write(width.to_bytes(4, 'little'))    # Width of the bitmap in pixels
        f.write(height.to_bytes(4, 'little'))   # Height of the bitmap in pixels. Positive for bottom to top pixel order.
        
        f.write((1).to_bytes(2, 'little'))  # Number of color planes being used
        f.write(bpp.to_bytes(2, 'little'))  # Number of bits per pixel
        f.write((0).to_bytes(4, 'little'))  # BI_BITFIELDS, no pixel array compression used
        f.write(raw_image_size.to_bytes(4, 'little'))    # IMPORTANT, SIZE OF THE RAW IMAGE
        f.write((2835).to_bytes(4, 'little'))   # Print resolution of the image, horizontal
        f.write((2835).to_bytes(4, 'little'))   # Print resolution of the image, vertical
        f.write((0).to_bytes(4, 'little'))  # Number of colors in the palette
        f.write((0).to_bytes(4, 'little'))  # 0 means all colors are important



        # ----- final de datos de header -----
        f.write(end_header.encode("utf-8"))

        # ----- Agregar Código javascript -----
        f.write(codigo.encode("utf-8"))

        # Adding padding
        if padding_size > 3:
            f.write("\n//".encode("utf-8"))
            for _ in range(padding_size-3):
                f.write("0".encode("utf-8"))
        elif padding_size > 0:
            for _ in range(padding_size):
                f.write("\n".encode("utf-8"))
    print(f"BMP+JavaScript polyglot file created: {output_file}")
