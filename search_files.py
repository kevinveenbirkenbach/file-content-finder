import os
import subprocess
import sys
import argparse

def search_files(search_string, file_types, verbose):
    if not file_types:
        file_types = ['*']  # Search all files if no specific file types are given

    for file_type in file_types:
        if file_type == "*.pdf":
            search_in_files(search_string, '*.pdf', 'pdfgrep', verbose)
        else:
            search_in_files(search_string, file_type, 'grep', verbose)

def search_in_files(search_string, file_type, grep_command, verbose):
    find_cmd = ['find', '.', '-type', 'f', '-name', file_type, '-print0']
    grep_cmd = ['xargs', '-0', grep_command, '-H', search_string]
    
    if verbose:
        print(f"Searching in {file_type} files...")
        print("Executing:", ' '.join(find_cmd))
        print("Executing:", ' '.join(grep_cmd))
    
    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    grep_proc = subprocess.Popen(grep_cmd, stdin=find_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    find_proc.stdout.close()  # Allow find_proc to receive a SIGPIPE if grep_proc exits
    out, err = grep_proc.communicate()
    
    if out:
        print(out.decode())
    if err:
        print(f"Errors occurred while searching {file_type} files:", err.decode())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for a string in PDF and text files.")
    parser.add_argument("search_string", help="The string to search for.")
    parser.add_argument(
        "-t", "--types",
        nargs="*",
        help="Optional list of file types to search in (e.g., *.txt *.md). If not provided, all files will be searched.",
        default=[]
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print the executed commands."
    )

    args = parser.parse_args()
    
    search_files(args.search_string, args.types, args.verbose)
