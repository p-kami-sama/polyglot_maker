import argparse
import sys
import os

sys.path.append('.')
try:
    import merge_pdf as merge_pdf
except ImportError:
    print("Error: Could not import local modules.")
    sys.exit(1)


combinations_list = {
    #--input, --keep, --output
    ('pdf','mp3'): ['pdf', 'mp3'],
    ('pdf','sh'): ['pdf', 'sh'],
    ('pdf','rb'): ['pdf', 'rb'],
    ('pdf','python'): ['pdf', 'python'],
}





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
        help="Hide extra data at the beginning of the file. It may not always be usable and is not compatible with --hide-end."
    )

    parser.add_argument(
        "-e", "--end", "--hide-end", action="store_true",
        help="Hide extra data at the end of the file. It may not always be usable and is not compatible with --hide-start."
    )
    parser.add_argument(
        "-t", "--types", action="store_true",
        help="List of file types to combine."
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose mode to show process details."
    )  

    return parser.parse_args()

def get_extension(path: str) -> str:
    if "." in path:
        return path.split(".")[-1] 
    else:
        return ""


def types_list():
    print('types_list: pendiente de implementar')

def create_polyglot():
    print('create_polyglot: pendiente de implementar')

def merge_files(input: str, keep: str, output: str,verbose: bool = False, start: bool = False, end: bool = True, args=None):
    # args.input, args.keep, args.output, args.start, args.end
    print('merge_files: pendiente de implementar')
    if  (get_extension(input), get_extension(keep)) not in combinations_list.keys() or \
        get_extension(output) not in combinations_list[get_extension(input), get_extension(keep)]:
        print(f"Error: The combination of {get_extension(input)} and {get_extension(keep)} into {get_extension(output)} is not supported.")
        sys.exit(1)
    
    else:
        if verbose:
            print(f"Combining {input} and {keep} into {output}.")
            
        if get_extension(input) == 'pdf' and get_extension(keep) == 'mp3':
            merge_pdf.merge_pdf_mp3(input, keep, output, verbose, start)
        elif get_extension(input) == 'pdf' and get_extension(keep) == 'sh':
            merge_pdf.merge_pdf_sh(input, keep, output, verbose, start)
        elif get_extension(input) == 'pdf' and get_extension(keep) == 'rb':
            merge_pdf.merge_pdf_ruby(input, keep, output, verbose, start)
        elif get_extension(input) == 'pdf' and get_extension(keep) == 'python':
            merge_pdf.merge_pdf_python(input, keep, output, verbose, start)

        print(f"Polyglot file {output} created successfully.")


def file_exists(file_path):
    return os.path.isfile(file_path)

def directory_exists(file_path):
    directorio = os.path.dirname(file_path) # Get the directory from the path
    if not directorio:  # If empty, it means the file is in the current directory
        directorio = "."
    
    return os.path.isdir(directorio)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Polyglot file generator combining multiple formats."
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
            create_polyglot()
    
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
            if args.start and args.end:
                print("Error: --hide-start and --hide-end cannot be used simultaneously. Use --help for more information.")
                sys.exit(1)
            
            # args.input, args.keep, args.output, args.start, args.end
            merge_files(args.input, args.keep, args.output, args.verbose ,args.start, args.end, args)







