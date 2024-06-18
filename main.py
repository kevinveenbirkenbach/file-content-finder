import argparse
from searcher import Searcher

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for a string in various file types, including PDF, text, image, xls, doc, sqlite, and odp files.")
    parser.add_argument("search_string", help="The string to search for.")
    parser.add_argument(
        "-t", "--types",
        nargs="*",
        help="Optional list of file types to search in (e.g., *.txt, *.md, *.jpg, *.xls, *.odp, *.doc, *.sqlite). If not provided, all files will be searched.",
        default=[]
    )
    parser.add_argument(
        "-p", "--path",
        help="The path to search in. If not provided, the current directory will be used.",
        default="."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print the executed commands."
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="Only list files containing the search string, without additional information."
    )
    parser.add_argument(
        "-i", "--ignore",
        action="store_true",
        help="Ignore errors and continue searching."
    )
    parser.add_argument(
        "-s", "--skip",
        nargs="*",
        help="Optional list of file extensions to skip (e.g., .zip, .tar, .gz).",
        default=[]
    )
    parser.add_argument(
        "-a", "--add",
        action="store_true",
        help="Extend the default list of skipped files."
    )
    parser.add_argument(
        "-b", "--binary-files",
        action="store_true",
        help="Treat binary files as text for searching."
    )

    args = parser.parse_args()

    default_skip = [
        '.db',
        '.db-wal',
        '.gpg',
        '.gz',
        '.iso',
        '.ldb',
        '.lnk',
        '.log',
        '.mp4',
        '.old',
        '.pod',
        '.sqlite', 
        '.tar', 
        '.zip',
        '.xcf',
        '.doc'
    ]

    if args.add:
        skip_patterns = default_skip + [pattern.lower() for pattern in args.skip]
    else:
        skip_patterns = [pattern.lower() for pattern in args.skip]

    searcher = Searcher(args.search_string, args.types, args.path, args.verbose, args.list, args.ignore, skip_patterns, args.binary_files)
    searcher.search_files()
