import os
import subprocess
import sys
import argparse

def verbose_print(verbose, message):
    if verbose:
        print(message)

def search_files(search_string, file_types, verbose):
    if not file_types:
        file_types = ['*']  # Search all files if no specific file types are given

    for file_type in file_types:
        if file_type == "*.pdf":
            search_pdfs(search_string, verbose)
        else:
            search_text_files(search_string, file_type, verbose)

def verbose(verbose, find_cmd, grep_cmd):
    if verbose:
        print(f"Searching in {file_type} files...")
        print("Executing:", ' '.join(find_cmd))
        print("Executing:", ' '.join(grep_cmd))

def execute_search(verbose, find_cmd, grep_cmd):
    verbose(verbose, find_cmd, grep_cmd)

    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    grep_proc = subprocess.Popen(grep_cmd, stdin=find_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    find_proc.stdout.close()  # Allow find_proc to receive a SIGPIPE if grep_proc exits
    out, err = grep_proc.communicate()
    
    if out:
        print(out.decode())
    if err:
        print(f"Errors occurred while searching {file_type} files:", err.decode())


def search_pdfs(search_string, verbose):
    print("Searching in PDF files...")
    find_cmd = ['find', '.', '-type', 'f', '-name', '*.pdf', '-print0']
    grep_cmd = ['xargs', '-0', 'pdfgrep', '-H', search_string]
    execute_search(verbose, find_cmd, grep_cmd)

def search_text_files(search_string, file_type, verbose):
    print(f"Searching in {file_type} files...")
    find_cmd = ['find', '.', '-type', 'f', '-name', file_type, '-print0']
    grep_cmd = ['xargs', '-0', 'grep', '-H', search_string]
    execute_search(verbose, find_cmd, grep_cmd)
    
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
