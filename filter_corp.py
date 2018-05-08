import argparse

comparator_dict = {
    "length-descending": (lambda x, y:  -(len(x) + len(y)) / 2) ,
    "tokens-descending": (lambda x, y: -(len(x.split(" ")) + len(y.split(" "))) / 2) ,
}    

"""
filter_dict = {
    "minimum-tokens": (lambda n: lambda sentence: len(sentence.split(" ") >= n)) ,
    "maximum-tokens": (lambda n: lambda sentence: len(sentence.split(" ") <= n)) 
}

filter_args_dict = {
    "minimum-tokens": 1,
    "maximum-tokens": 1
}
"""


def str2key(string):
    if string not in comparator_dict:
        raise ValueError("Option %s does not exist" % string)
    return comparator_dict[string]

def create_parser():
    parser = argparse.ArgumentParser(description="Sort and filter lines from corpora according to certain conditions")

    parser.add_argument("--input", required=True, nargs=2, metavar="<path>", help="Paths to original source and target corpora")


    parser.add_argument("--output", required=True, nargs=2, metavar="<path>", help="Paths to filtered source and target corpora")

    help_string = "Possible conditions:"
    for k in comparator_dict.keys():
        help_string += " %s" % k
    parser.add_argument("--sort-keys", nargs="+", metavar="condition", type=str2key, help=help_string)

    parser.add_argument("--min-tokens", default=None, metavar="n", type=int, help="Maximum number of tokens per sentence in source and target sentence")
    parser.add_argument("--max-tokens", default=None, metavar="n", type=int, help="Maximum number of tokens per sentence in source and target sentence")
    parser.add_argument("--unique", action="store_true", help="Filter out identical sentences")

    parser.add_argument("--limit", default=None, metavar="n", type=int, help="Maximum number of sequences to keep")

    return parser

def unique_seq(src_lines, dest_lines):

    unique_source = set()

    indices = [] 
    for i in range(len(src_lines)):
        if src_lines[i] not in unique_source:
            unique_source.add(src_lines[i])
            indices.append(i)
    
    return [src_lines[i] for i in indices], [dest_lines[i] for i in indices]

def main(in_files, out_files, comparator=None, min_tokens=None, max_tokens=None, unique=False, limit=None):
    """
    comparator - a comparator function taking two parameters-a source sentence and a target sentence"
    """

    with open(in_files[0], "r", encoding="utf-8") as r_source, open(in_files[1], "r", encoding="utf-8") as r_dest:
        source_lines = r_source.readlines()
        dest_lines = r_dest.readlines()
    if len(source_lines) != len(dest_lines):
        raise ValueError("Source and target files have unequal number of sequences")


    #Filtering
    conditions = []
    if min_tokens: conditions.append( lambda sentence: len(sentence.split(" ")) >= min_tokens)
    if max_tokens: conditions.append( lambda sentence: len(sentence.split(" ")) <= max_tokens)
    def sentence_filter(sentence):
        for condition in conditions:
            if not condition(sentence): return False
        return True

    filtered_indices = filter(lambda i: sentence_filter(source_lines[i]) and sentence_filter(dest_lines[i]), range(len(source_lines)))
    filtered_source = []
    filtered_dest = []
    for i in filtered_indices:
       filtered_source.append(source_lines[i])
       filtered_dest.append(dest_lines[i])

    if unique:
        (filtered_source, filtered_dest) = unique_seq(filtered_source, filtered_dest)

    #Sorting
    if comparator:
        sorted_indices = sorted( range(len(source_lines)), key= lambda i: comparator(source_lines[i], dest_lines[i])  ) 
        sorted_source = [ source_lines[i] for i in sorted_indices ]
        sorted_dest = [ dest_lines[i] for i in sorted_indices ]
    else:
        sorted_source = filtered_source
        sorted_dest = filtered_dest

    if not limit or limit > len(source_lines): limit = len(source_lines)
    output_source = sorted_source[ :limit]
    output_dest = sorted_dest[ :limit]

    with open(out_files[0], "w", encoding="utf-8") as w:
        w.writelines(output_source)
    with open(out_files[1], "w", encoding="utf-8") as w:
        w.writelines(output_dest)


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    comparator = None
    if args.sort_keys:
        comparator = lambda source, target: tuple( sort_key(source, target) for sort_key in args.sort_keys )

    main( args.input, args.output, comparator=comparator, min_tokens=args.min_tokens, max_tokens=args.max_tokens, unique=args.unique, limit=args.limit)
