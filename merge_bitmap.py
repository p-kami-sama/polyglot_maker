import math
import struct
import sys


# Extracts the bytes from the header
def read_bitmap_header(file_path: str):
    with open(file_path, 'rb') as f:
        c = f.read(14)  # read BMP Header
        f.seek(0)       # Reset file pointer to the beginning
      
        full_header_size = int.from_bytes(c[10:13], byteorder='little')
        header_bytes = f.read(full_header_size)  # Read all the header
        header_data = struct.unpack('<2sIHHIIIIHHIIIIII', header_bytes)
       
        return header_data, header_bytes



# Extract the bytes corresponding to the image that are displayed when opening the file
def extract_raw_image_from_bitmap(file_path: str):
    with open(file_path, 'rb') as f:
        f.seek(10)  # Offset where the image starts
        offset = struct.unpack('<I', f.read(4))[0]
        f.seek(offset)  # Go to the position where the image starts
        bmp_data = f.read()  # Read only the bits of the image
    return bmp_data



# Characters belonging to the end of a comment are replaced by one with a close value
def overwrite_end_image(bitman_raw_image: bytes, end_image: str ,end_image_substitute: str, verbose: bool = False):    
    if end_image.encode('utf-8') in bitman_raw_image:
        if verbose:
            print("Se encontró el carácter "+end_image+" en el la imagen bitmap, sustituyendo...")
            print("Número de ocurrencias:", bitman_raw_image.count( end_image.encode('utf-8')) )
        return bitman_raw_image.replace( end_image.encode('utf-8'), end_image_substitute.encode('utf-8') )
    else:
       return bitman_raw_image



# Create a space between the header and the image bytes to hide code
def merge_bitmap_lua(bitmap_file: str, lua_code_file: str, output_file: str, verbose: bool = False):
    with open(lua_code_file, 'r') as lua_f:   # open .lua file
        codigo = lua_f.read()

    file_size_field =  """[[--"""
    end_header = """
]]=0
"""
    start_image = """--[["""
    final_code = end_header + codigo + start_image

    end_image = """]]"""
    end_image_substitute = """]^"""
    
    while ((len(codigo) + len(end_header.encode('utf-8'))) % 4) != 0:   # must be a multiple of 4
        end_header +=  '0' #  insert character in last position
    code_data = final_code.encode('utf-8')

    full_code_size = len(code_data)

    file_size_field_bytes = file_size_field.encode('utf-8')

    cabecera_datos, cabecera_bytes = read_bitmap_header(bitmap_file)
    if verbose:
        print("Original BMP header:", cabecera_datos) 

    bitmap_raw_image = extract_raw_image_from_bitmap(bitmap_file)
    bitmap_raw_image = overwrite_end_image(bitmap_raw_image, end_image ,end_image_substitute, verbose)

    with open(output_file, "wb") as f:
        # ----- Write BMP Header -----   14 bytes
        f.write(b'BM')  # 2
        f.write(file_size_field_bytes[::-1])  # 4
                
        f.write((cabecera_datos[2]).to_bytes(2, 'little'))      #  depends on the application that creates the image, if created manually can be 0
        f.write((cabecera_datos[3]).to_bytes(2, 'little'))      #  depends on the application that creates the image, if created manually can be 0

        f.write((len(cabecera_bytes) + full_code_size).to_bytes(4, 'little'))    # Offset where the pixel array (bitmap data) can be found 

        f.write(cabecera_bytes[14:])  # Copy the rest of the header
       
        f.write(code_data)  # Insert Lua code

        f.write(bitmap_raw_image)  # Copy the original image
        f.write('01]]'.encode('utf-8')) # Add the end of the Lua code

    print(f"BMP+LUA polyglot file created: {output_file}")



# overwrite part of the image with the code
def merge_bitmap_lua_overwrite(bitmap_file: str, lua_code_file: str, output_file: str, verbose: bool = False):

    with open(lua_code_file, 'r') as lua_f:   # open .lua file
        codigo = lua_f.read()

    file_size_field =  """[[--"""
    end_header = """
]]=0
"""
    start_image = """--[["""
    end_image = """]]"""
    end_image_substitute = """]^"""

    required_space = len((end_header + codigo + start_image + end_image).encode('utf-8'))

    print("Required space:", required_space, 'bytes')

    file_size_field_bytes = file_size_field.encode('utf-8')

    cabecera_datos, cabecera_bytes = read_bitmap_header(bitmap_file)

    
    bitman_raw_image = extract_raw_image_from_bitmap(bitmap_file)

    if len(bitman_raw_image) < required_space:
        print("The size of the bitmap is smaller than the size of the code")
        print("The code cannot be inserted into the bitmap")
        print("Bitmap size:", len(bitman_raw_image), "bytes")
        print("Code size:", len(codigo), "bytes")
        print("other bytes needed to insert the code:", len(end_header.encode('utf-8')) + len(start_image.encode('utf-8')) + len(end_image), "bytes") 
        sys.exit(1)
    
    
    bitman_raw_image = overwrite_end_image(bitman_raw_image, end_image ,end_image_substitute, verbose)


    if verbose:
        print("Original BMP header:", cabecera_datos) 

    with open(output_file, "wb") as f:
        # ----- Write BMP Header -----   14 bytes
        f.write(b'BM')  # 2
        f.write(file_size_field_bytes[::-1])  # 4 bytes
        f.write(cabecera_bytes[6:])  # Copy the rest of the header
       
        overwrite_start = (end_header + codigo + start_image).encode('utf-8')
        overwrite_end = end_image.encode('utf-8')

        new_bitmap_raw_image = overwrite_start + bitman_raw_image[len(overwrite_start):]
        new_bitmap_raw_image = new_bitmap_raw_image[:(len(new_bitmap_raw_image)-len(overwrite_end))] + overwrite_end
       
        f.write(new_bitmap_raw_image)  # Insert Lua code