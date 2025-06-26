import struct
from pathlib import Path


    # al comienzo del archivo ZIP esconde el script bash
def merge_zip_start(zip_file: str, bash_file: str, output_file_path: str, verbose: bool = False):
    
    # Cargas los archivos
    with open(zip_file, 'rb') as zip_f:
        if verbose:
            print("Reading ZIP file...")
        zip_data = zip_f.read()

    with open(bash_file, 'rb') as sh_f:
        if verbose:
            print("Reading shell script file...")
        bash_code = sh_f.read()

    # Encabezado bash y comentario
    bash_header = ("#!/bin/bash\n")

    # Evita que bash lea el ZIP
    bash_end = "\nexit 0\n"

    if verbose:
        print("Creating polyglot file...")

    # Construir el archivo final
    polyglot_data = (
        bash_header.encode("utf-8") +
        bash_code +
        bash_end.encode("utf-8") +
        zip_data
    )

    # Guardar el archivo
    Path(output_file_path).write_bytes(polyglot_data)





# Inserta un script bash como comentario en el final del archivo ZIP
def merge_zip_middle(zip_file: str, bash_file: str, output_file_path: str, verbose: bool = False):
    zip_bytes = bytearray(Path(zip_file).read_bytes())
    bash_code = Path(bash_file).read_text()

    # Firmas ZIP
    CDFH_SIGNATURE = b"\x50\x4B\x01\x02"  # Central Directory File Header
    EOCD_SIGNATURE = b"\x50\x4B\x05\x06"  # End of Central Directory

    # Buscar todas las entradas del directorio central
    offset = 0
    found = False

    while offset < len(zip_bytes):
        if zip_bytes[offset:offset+4] == CDFH_SIGNATURE:
            found = True
            # Longitud del nombre, extra field, y comentario
            filename_len = struct.unpack_from("<H", zip_bytes, offset + 28)[0]
            extra_len = struct.unpack_from("<H", zip_bytes, offset + 30)[0]
            comment_len = struct.unpack_from("<H", zip_bytes, offset + 32)[0]

            total_len = 46 + filename_len + extra_len + comment_len

            # Insertar el bash en el comentario de esta entrada
            start_bash_comment = b"#!/bin/bash\n: <<'COMMENT'\n"
            end_bash_comment = b"\nCOMMENT\n"

            bash_comment = end_bash_comment + bash_code.encode("utf-8") 

            if verbose:
                print(f"Inserting Bash script as comment in ZIP entry at offset {offset}")
            
            if len(bash_comment) > 0xFFFF:
                raise ValueError("El script Bash es demasiado largo para un comentario de entrada ZIP.")

            # Actualizar el campo de longitud del comentario
            struct.pack_into("<H", zip_bytes, offset + 32, len(bash_comment))

            # Construir nueva entrada con comentario Bash
            nueva_entrada = (
                zip_bytes[offset:offset + 46 + filename_len + extra_len] +
                bash_comment  # nuevo comentario
            )

            # Calcular la diferencia de tamaño
            delta = len(bash_comment) - comment_len

            # Actualizar el campo "relative offset of local header" en todas las entradas siguientes
            next_offset = offset + total_len
            adjust_offset = offset
            while next_offset < len(zip_bytes):
                if zip_bytes[next_offset:next_offset+4] != CDFH_SIGNATURE:
                    break
                struct_offset = next_offset + 42
                original = struct.unpack_from("<I", zip_bytes, struct_offset)[0]
                struct.pack_into("<I", zip_bytes, struct_offset, original + len(start_bash_comment))
                next_offset += 46 + struct.unpack_from("<H", zip_bytes, next_offset + 28)[0] \
                                     + struct.unpack_from("<H", zip_bytes, next_offset + 30)[0] \
                                     + struct.unpack_from("<H", zip_bytes, next_offset + 32)[0]

            # Buscar y actualizar offset del directorio central en el EOCD
            eocd_offset = zip_bytes.rfind(EOCD_SIGNATURE)
            if eocd_offset != -1:
                cd_start_offset = struct.unpack_from("<I", zip_bytes, eocd_offset + 16)[0]
                struct.pack_into("<I", zip_bytes, eocd_offset + 16, cd_start_offset + len(start_bash_comment))

            # Reensamblar el archivo
            zip_bytes = (
                start_bash_comment +
                zip_bytes[:offset] +
                nueva_entrada +
                zip_bytes[offset + total_len:]
            )
            
            
            break

        offset += 1

    if not found:
        raise ValueError("No se encontró ninguna entrada de directorio central en el archivo ZIP.")

    if verbose:
        print('Saving the modified file...')
    # Guardar el archivo resultante
    Path(output_file_path).write_bytes(zip_bytes)





# Inserta un script bash como comentario en el final del archivo ZIP
def merge_zip_end(zip_path: str, bash_path: str, salida_path: str, verbose: bool = False):
    zip_bytes = bytearray(Path(zip_path).read_bytes())
    bash_code = Path(bash_path).read_text()

    EOCD_SIGNATURE = b"\x50\x4B\x05\x06"  # PK\x05\x06
    MAX_EOCD_SEARCH = 65536  # EOCD puede estar como máximo a 64 KiB del final

    if verbose:
        print("Inserting Bash script as comment at the end of the file...")

    # Buscar EOCD al final del archivo
    start_search = max(0, len(zip_bytes) - MAX_EOCD_SEARCH)
    eocd_offset = zip_bytes.rfind(EOCD_SIGNATURE, start_search)

    if eocd_offset == -1:
        raise ValueError("No se encontró el End of Central Directory (EOCD). No es un archivo ZIP válido.")
    else:
        if verbose:
            print(f"EOCD found at offset {eocd_offset}")

    # Leer tamaño actual del comentario ZIP
    comment_length_offset = eocd_offset + 20  # offset del campo "ZIP file comment length"
    old_comment_length = struct.unpack_from("<H", zip_bytes, comment_length_offset)[0]

    # Construir nuevo comentario (script bash)
    start_bash_comment = '''
#!/bin/bash\n
: <<'COMMENT'
'''.encode("utf-8")

    end_bash_comment = """
COMMENT
"""

    # bash_code + "\nexit 0\n"  # Asegurarse de que el script termine correctamente
    bash_comment = end_bash_comment.encode("utf-8") + bash_code.encode("utf-8")

    new_comment_length = len(bash_comment)

    if new_comment_length > 0xFFFF:
        raise ValueError("The comment is too long. The maximum allowed is 65535 bytes.")

    # Reemplazar el campo de longitud
    struct.pack_into("<H", zip_bytes, comment_length_offset, new_comment_length)
    if verbose:
        print(f"Old comment length: {old_comment_length}, New comment length: {new_comment_length}")

    # Reemplazar o agregar el comentario al final del EOCD
    zip_bytes = start_bash_comment + zip_bytes[:eocd_offset + 22] + bash_comment

    # Guardar el archivo resultante
    Path(salida_path).write_bytes(zip_bytes)


def merge_zip(zip_file_path: str, bash_file_path: str, output_file_path: str, verbose: bool = False, pos: str = 'end' ):
    if pos == 'start':
        merge_zip_start(zip_file_path, bash_file_path, output_file_path, verbose)
    elif pos == 'middle':
        merge_zip_middle(zip_file_path, bash_file_path, output_file_path, verbose)
    else:
        merge_zip_end(zip_file_path, bash_file_path, output_file_path, verbose)
