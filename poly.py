import argparse
import sys
import os

sys.path.append('.')

try:
    import merge_pdf as merge_pdf
except ImportError:
    print('Error: Could not import local "merge_pdf.py" module. Please ensure it is in the same directory as this script.')
    sys.exit(1)

try:
    import merge_bitmap as merge_bitmap
except ImportError:
    print('Error: Could not import local "merge_bitmap.py" module. Please ensure it is in the same directory as this script.')
    sys.exit(1)

try:
    import create_bitmap as create_bitmap
except ImportError:
    print('Error: Could not import local "create_bitmap.py" module. Please ensure it is in the same directory as this script.')
    sys.exit(1)

try:
    import create_gif as create_gif
except ImportError:
    print('Error: Could not import local "create_gif.py" module. Please ensure it is in the same directory as this script.')
    sys.exit(1)

try:
    import merge_jpg as merge_jpg
except ImportError:
    print('Error: Could not import local "merge_jpg.py" module. Please ensure it is in the same directory as this script.')
    sys.exit(1)

try:
    import merge_zip as merge_zip
except ImportError:
    print('Error: Could not import local "merge_zip.py" module. Please ensure it is in the same directory as this script.')
    sys.exit(1)

combinations_list = {
    #--input, --keep, --output
    ('pdf', 'mp3'): ['pdf', 'mp3'],
    ('pdf', 'sh'): ['pdf', 'sh'],
    ('pdf', 'rb'): ['pdf', 'rb'],
    ('pdf', 'py'): ['pdf', 'py'],

    ('bmp', 'lua'): ['bmp', 'lua'],
    ('bmp', 'js'): ['bmp', 'js'],

    ('jpg', 'php'): ['jpg', 'php', 'jpeg', 'jfif'],

    ('jpg', 'pdf'): ['jpg', 'php', 'jpeg', 'jfif', 'pdf'],
    ('pdf', 'jpg'): ['jpg', 'php', 'jpeg', 'jfif', 'pdf'],

    ('zip', 'sh'): ['zip', 'sh'],
    ('jar', 'sh'): ['jar', 'sh'],

}

create_list = [
    #--input, --create
    ['lua', 'bmp'],
    ['js', 'bmp'],
    ['lua', 'gif'],
]




def add_parse_args(parser):
    parser.add_argument(
        "-i", "--input", "--in", type=str,
        help="Input file name. It will not be modified."
    )

    parser.add_argument(
        "-o", "--output", "--out", type=str, 
        help="Name of the output file to be generated."
    )

    parser.add_argument(
        "-k", "--keep", type=str,
        help="Name of the file to hide within the input file."
    ) 

    parser.add_argument(
        "-c", "--create", type=str,
        help="Name of the file to be created using only the contents of --input. Should not be used simultaneously with --out or --keep."
    )

    parser.add_argument(
        "-s", "--start", "--hide-start", action="store_true",
        help="Hide extra data at the beginning of the PDF, JAR or ZIP file. It may not always be usable."
    )
    parser.add_argument(
        "-m", "--middle", "--hide-middle", action="store_true",
        help="Hide extra data in the middle of the PDF or ZIP file. It may not always be usable."
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrites part of the BMP input file to hide the keep file better."
    )

    parser.add_argument(
        "-t", "--types", action="store_true",
        help="List of file types to combine."
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose mode to show process details."
    )

    parser.add_argument(
        "-p", "--pattern", type=str,
        help='''Used to define the image pattern when creating GIF/Lua Polyglots.
        Possible patterns: "stripes", "checkerboard", "blocks", and "waves".
        Default value: "stripes"'''
    ) 

    return parser.parse_args()

def get_extension(path: str) -> str:
    if "." in path:
        return path.split(".")[-1] 
    else:
        return ""


def types_list():
    print('--input, --keep, --output combinations:')
    print(f"{'Input':<10} {'Keep':<10} {'Outputs'}")
    print('-' * 40)

    for key, value in combinations_list.items():
        input_ext, keep_ext = key
        output_exts = ' .'.join(value)
        print(f".{input_ext:<10} .{keep_ext:<10} .{output_exts}")
    
    
    print('\n\n--input, --create combinations:')
    print(f"{'Input':<10} {'Create':<10}")
    print('-' * 40)
    for item in create_list:
        input_ext, create_ext = item
        print(f".{input_ext:<10} .{create_ext:<10}")



def create_polyglot(input: str, create: str, verbose: bool = False, pattern: str = "stripes"):
    if [get_extension(input), get_extension(create)] not in create_list:
        print(f"Error: The creation of {get_extension(input)} into {get_extension(create)} is not supported.")
        sys.exit(1)

    if get_extension(input) == 'lua' and get_extension(create) == 'bmp':
        create_bitmap.create_bitmap_lua(input, create, verbose)
    elif get_extension(input) == 'js' and get_extension(create) == 'bmp':
        create_bitmap.create_bitmap_javascript(input, create, verbose)
    elif get_extension(input) == 'lua' and get_extension(create) == 'gif':
        create_gif.create_gif(input, create, verbose, pattern)

    print(f"Polyglot file {create} created successfully.")



def validate_combination(input: str, keep: str, output: str):
    if (get_extension(input), get_extension(keep)) not in combinations_list.keys() or \
            get_extension(output) not in combinations_list[get_extension(input), get_extension(keep)]:
        print(f"Error: The combination of {get_extension(input)} and {get_extension(keep)} into {get_extension(output)} is not supported.")
        sys.exit(1)


def merge_files(input: str, keep: str, output: str,verbose: bool = False, start: bool = False, middle: bool = False, overwrite: bool = False, args=None):
    # args.input, args.keep, args.output, args.start
    validate_combination(input, keep, output)
    

    if verbose:
        print(f"Combining {input} and {keep} into {output}.")
        
    if get_extension(input) == 'pdf':
        if middle and get_extension(keep) == 'sh':
            merge_pdf.merge_pdf_sh_middle(input, keep, output, verbose)
        if get_extension(keep) == 'mp3':
            merge_pdf.merge_pdf_mp3(input, keep, output, verbose, start)
        elif get_extension(keep) == 'sh':
            merge_pdf.merge_pdf_sh(input, keep, output, verbose, start)
        elif get_extension(keep) == 'rb':
            merge_pdf.merge_pdf_ruby(input, keep, output, verbose, start)
        elif get_extension(keep) == 'py':
            merge_pdf.merge_pdf_py(input, keep, output, verbose, start)

        elif get_extension(keep) in ['jpg', 'jpeg', 'jfif']:
            merge_jpg.merge_jpg_pdf(input, keep, output, verbose)

    elif get_extension(input) == 'bmp':
        if get_extension(keep) == 'lua':
            if overwrite:
                merge_bitmap.merge_bitmap_lua_overwrite(input, keep, output, verbose)
            else:
                merge_bitmap.merge_bitmap_lua(input, keep, output, verbose)
        elif get_extension(keep) == 'js':
            if overwrite:
                merge_bitmap.merge_bitmap_js_overwrite(input, keep, output, verbose)
            else:
                merge_bitmap.merge_bitmap_js(input, keep, output, verbose)
    
    
    elif get_extension(input) in ['jpg', 'jpeg', 'jfif'] and get_extension(keep) == 'php':
        merge_jpg.merge_jpg_php(input, keep, output, verbose)    
   
    elif get_extension(input) in ['jpg', 'jpeg', 'jfif'] and get_extension(keep) == 'pdf':
        merge_jpg.merge_jpg_pdf(keep, input, output, verbose)
   



    elif get_extension(input) in ['jar', 'zip'] and get_extension(keep) == 'sh':
        pos = 'end'
        if start:
            pos = 'start'
        elif middle:
            pos = 'middle'
        if verbose:
            print(f"Merging {input} and {keep} into {output} at position {pos}.")
        merge_zip.merge_zip(input, keep, output, verbose, pos)


    print(f"Polyglot file {output} merged successfully.")


def file_exists(file_path):
    return os.path.isfile(file_path)

def directory_exists(file_path):
    directorio = os.path.dirname(file_path) # Get the directory from the path
    if not directorio:  # If empty, it means the file is in the current directory
        directorio = "."
    
    return os.path.isdir(directorio)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = "Polyglot file generator combining multiple formats."
    )
    args = add_parse_args(parser)

    # Counting arguments that were actually passed
    if sum(1 for arg in vars(args).values() if arg not in [None, False]) == 0:
        parser.print_help()
        sys.exit(0)
    elif args.types:
        types_list()
        sys.exit(0)
    elif (args.create and args.keep) or (args.create and args.output):
        print("Error: --create cannot be used simultaneously with --keep or --out. Use --help for more information.")
        sys.exit(1)


    if args.verbose:
        print("Verbose mode activated.")

        print('overwrite:', args.overwrite) 

    # create from 1 file
    if args.create:
        if not args.input:
            print("Error: --create must be used with --input. Use --help for more information.")
            sys.exit(1)
        elif not file_exists(args.input):
            print(f"Error: --input file {args.input} does not exist.")
            sys.exit(1)
        elif not directory_exists(args.create):
            print(f"Error: --create directory {args.create} does not exist.")
            sys.exit(1)
        else:

            # args.input, args.create
            create_polyglot(args.input, args.create, args.verbose, pattern =args.pattern or "stripes")
    
    # merge 2 files
    elif args.output:
        if not args.input or not args.keep:
            print("Error: --out must be used with --input and --keep. Use --help for more information.")
            sys.exit(1)
        else:
            if not file_exists(args.input):
                print(f"Error: --input file {args.input} does not exist.")
                sys.exit(1)
            if not file_exists(args.keep):
                print(f"Error: --keep file {args.keep} does not exist.")
                sys.exit(1)
            if not directory_exists(args.output):
                print(f"Error: --output directory {args.output} does not exist.")
                sys.exit(1)
            if args.start and args.middle:
                print("WARNING: --start and --middle cannot be used simultaneously. The --start option will be used and --middle will be ignored. Use --help for more information.")
                args.middle = False
            
            # args.input, args.keep, args.output, args.start, args.end args.middle
            merge_files(args.input, args.keep, args.output, args.verbose ,args.start, args.middle, args.overwrite, args)
