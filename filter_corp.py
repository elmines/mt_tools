import argparse

condition_dict = {
    "length-descending": (lambda x, y:  -(len(x) + len(y)) / 2) ,
    "tokens-descending": (lambda x, y: -(len(x.split(" ")) + len(y.split(" "))) / 2) ,
}    


def str2key(string):
    if string not in condition_dict:
        raise ValueError("Option %s does not exist" % string)
    return condition_dict[string]

def create_parser():
    parser = argparse.ArgumentParser(description="Sort and filter lines from corpora according to certain conditions")

    parser.add_argument("--input", required=True, nargs=2, metavar="<path>", help="Paths to original source and target corpora")


    parser.add_argument("--output", required=True, nargs=2, metavar="<path>", help="Paths to filtered source and target corpora")

    help_string = "Possible conditions:"
    for k in condition_dict.keys():
        help_string += " %s" % k
    parser.add_argument("--sort-keys", nargs="+", metavar="condition", type=str2key, help=help_string)

    parser.add_argument("--limit", default=None, metavar="n", type=int, help="Maximum number of sequences to keep")

    return parser

def write_std(string):
   sys.stdout.write(string)

def write_file(outfile, string):
   outfile.write(string)


    

def main(in_files, out_files, comparator=None, limit=None):
    """
    comparator - a comparator function taking two parameters-a source sentence and a target sentence"
    """

    with open(in_files[0], "r", encoding="utf-8") as r_source, open(in_files[1], "r", encoding="utf-8") as r_dest:
        source_lines = r_source.readlines()
        dest_lines = r_dest.readlines()

    print(source_lines[:50])

    if len(source_lines) != len(dest_lines):
        raise ValueError("Source and target files have unequal number of sequences")

    if not comparator: comparator = lambda source, target : 0
    
    if not limit or limit > len(source_lines): limit = len(source_lines)

    indices = sorted( range(len(source_lines)), key= lambda i: comparator(source_lines[i], dest_lines[i])  ) 


    sorted_source = [ source_lines[i] for i in indices ]
    sorted_dest = [ dest_lines[i] for i in indices ]

    #print(sorted_source[:50])
    #print(indices[:50])


    output_source = sorted_source[ :limit]
    output_dest = sorted_dest[ :limit]

    #print(output_source[:50])

    with open(out_files[0], "w", encoding="utf-8") as w:
        w.writelines(output_source)
    with open(out_files[1], "w", encoding="utf-8") as w:
        w.writelines(output_dest)


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    comparator = None
    #print(args.sort_keys[0] == condition_dict["length"] )
    #exit(0)
    if args.sort_keys:
        comparator = lambda source, target: tuple( sort_key(source, target) for sort_key in args.sort_keys )

    main( args.input, args.output, comparator=comparator, limit=args.limit)
