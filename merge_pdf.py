import os
import random
import string
import re

def merge_pdf_mp3(pdf_file, mp3_file, output_file, verbose, append_at_the_beginning = False):
    if append_at_the_beginning:
        if os.path.getsize(mp3_file) > 1000:
            print("The audio file is too large to be appended at the beginning, it will be appended at the end. Files larger than 1000 bytes cannot be appended at the beginning.")
            append_at_the_beginning = False
        elif verbose:
            print("Appending audio file at the beginning...")
    if verbose and not append_at_the_beginning:
        print("Appending audio file at the end...")

    with open(pdf_file, 'rb') as pdf_f:  # Abrimos el archivo PDF
        pdf_data = pdf_f.read()
    
    with open(mp3_file, 'rb') as mp3_f: # Abrimos el archivo MP3
        hide_data = mp3_f.read()
    
    with open(output_file, 'wb') as output_f:   # Creamos el archivo de salida en modo binario
        if append_at_the_beginning:
            output_f.write(hide_data)
            output_f.write(pdf_data)
        else:
            output_f.write(pdf_data)
            output_f.write(hide_data)






def merge_pdf_sh(pdf_file, sh_file, output_file, verbose, append_at_the_beginning = False):
    if append_at_the_beginning:
        if os.path.getsize(sh_file) > 1000:
            print("The sh file is too large to be appended at the beginning, it will be appended at the end. Files larger than 1000 bytes cannot be appended at the beginning.")
            append_at_the_beginning = False
        elif verbose:
            print("Appending sh file at the beginning...")
    if verbose and not append_at_the_beginning:
        print("Appending sh file at the end...")


    with open(pdf_file, 'rb') as pdf_f:
        pdf_data = pdf_f.read()
    
    with open(sh_file, 'rb') as sh_f:
        hide_data = sh_f.read()
    
    with open(output_file, 'wb') as output_f:   # Creamos el archivo de salida en modo binario

        if append_at_the_beginning:
            output_f.write(hide_data)  # Escribir el script shell como bytes
            output_f.write(b"\nexit\n")  # Asegurarse de que haya una nueva línea después de %%EOF
            output_f.write(pdf_data)
        else:
            random_comment_word = ''.join(random.choices(string.ascii_letters, k=random.randint(8, 12)))
            output_f.write(f": << '{random_comment_word}'\n".encode())
            output_f.write(pdf_data)
            output_f.write(f"\n{random_comment_word}\n".encode())
            output_f.write(hide_data)  # Escribir el script shell como bytes
            output_f.write(b"\nexit\n")  # Asegurarse de que haya una nueva línea después de %%EOF

                    



def merge_pdf_ruby(pdf_file, ruby_file, output_file, verbose, append_at_the_beginning = False):
    if append_at_the_beginning:
        if os.path.getsize(ruby_file) > 1000:
            print("The ruby file is too large to be appended at the beginning, it will be appended at the end. Files larger than 1000 bytes cannot be appended at the beginning.")
            append_at_the_beginning = False
        elif verbose:
            print("Appending ruby file at the beginning...")
    if verbose and not append_at_the_beginning:
        print("Appending ruby file at the end...")

    with open(pdf_file, 'rb') as pdf_f:
        pdf_data = pdf_f.read()
    
    with open(ruby_file, 'rb') as mp3_f:
        hide_data = mp3_f.read()
    
    with open(output_file, 'wb') as output_f:
        if append_at_the_beginning:
            output_f.write(hide_data)
            output_f.write("\n=begin\n".encode())
            output_f.write(pdf_data)
            output_f.write("\n=end\n".encode())
        else:
            output_f.write("\n=begin\n".encode())
            output_f.write(pdf_data)
            output_f.write("\n=end\n".encode())
            output_f.write(hide_data)


def merge_pdf_py(pdf_file, python_file, output_file, verbose, append_at_the_beginning = False):
    if append_at_the_beginning:
        if os.path.getsize(python_file) > 1000:
            print("The python file is too large to be appended at the beginning, it will be appended at the end. Files larger than 1000 bytes cannot be appended at the beginning.")
            append_at_the_beginning = False
        elif verbose:
            print("Appending python file at the beginning...")
    if verbose and not append_at_the_beginning:
        print("Appending python file at the end...")

    with open(pdf_file, 'rb') as pdf_f:
        pdf_data = pdf_f.read()
        print(type(pdf_data))
    
        if b'\x00' in pdf_data:
            print("The PDF file has a null byte, so the Python code probably doesn't work. Please try another PDF.")
        elif verbose:
            print("No null byte found in the PDF file, continuing with the process.")
    
    with open(python_file, 'r') as hide_f:
        hide_data = hide_f.read()
    
    encoding = '''# coding: iso-8859-1 -*-'''

    with open(output_file, 'wb') as output_f:
        if append_at_the_beginning:
            output_f.write(encoding.encode("iso-8859-1"))
            output_f.write(b'\n')

            output_f.write(hide_data)
            output_f.write(b'\nr"""\n')
            output_f.write(pdf_data)
            output_f.write(b'"""\n')
        else:
            output_f.write(encoding.encode("iso-8859-1"))
            output_f.write(b'\nr"""\n')
            output_f.write(pdf_data)
            output_f.write(b'"""\n')
            output_f.write(hide_data.encode("iso-8859-1"))



def merge_pdf_sh_middle(pdf_file, sh_file, output_file, verbose: bool = False):

    with open(pdf_file, 'rb') as pdf_f:
        if verbose:
            print("Reading PDF file...")
        pdf_data = pdf_f.read()
    
    with open(sh_file, 'rb') as sh_f:
        if verbose:
            print("Reading shell script file...")
        hide_data = sh_f.read()


    # Buscar un punto adecuado entre los objetos del PDF
    # Patrón común que indica final de un objeto: "endobj" seguido de una nueva línea
    matches = list(re.finditer(rb'\nendobj[\r]?\n', pdf_data))
    if not matches:
        raise ValueError("PDF objects to insert the script not found. Ensure the PDF is valid and contains objects.")

    # Punto intermedio entre objetos para la inserción
    insert_pos = matches[len(matches) // 2].end()

    # Dividir el PDF en dos partes:
    pdf_part1 = pdf_data[:insert_pos]
    pdf_part2 = pdf_data[insert_pos:]

    # Generar una palabra aleatoria para usarse como comentario de Bash
    random_comment_word = ''.join(random.choices(string.ascii_letters, k=random.randint(8, 12)))

    if verbose:
        print(f"Inserting shell script at position {insert_pos} in the PDF file.")
    
    # Payload Bash: se encierra la primera parte del PDF en un comentario multilinea
    bash_payload = f": << '{random_comment_word}'\n".encode("utf-8")
    bash_payload += pdf_part1
    bash_payload += f"\n{random_comment_word}\n".encode("utf-8")

    bash_payload += hide_data  # Agregar el script Bash como bytes
    bash_payload += "\nexit\n".encode("utf-8")  # Finalizar el script Bash
    
    # Ensamblar el PDF final con Bash embebido
    with open(output_file, "wb") as f:
        f.write(bash_payload)
        f.write(pdf_part2)
