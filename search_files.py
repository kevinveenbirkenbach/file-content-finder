import os
import subprocess
import sys
import argparse
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def verbose_print(verbose, *messages):
    if verbose:
        print(" ".join(messages))

def find_all_file_types(search_path):
    file_types = set()
    for root, _, files in os.walk(search_path):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext:
                file_types.add(f"*{ext}")
    return list(file_types)

def search_files(search_string, file_types, search_path, verbose):
    if not file_types:
        file_types = find_all_file_types(search_path)

    for file_type in file_types:
        if file_type == "*.pdf":
            search_pdfs(search_string, search_path, verbose)
        elif file_type in ["*.jpeg", "*.jpg", "*.png"]:
            search_images(search_string, file_type, search_path, verbose)
        else:
            search_text_files(search_string, file_type, search_path, verbose)

def verbose_output(verbose, find_cmd, grep_cmd, file_type):
    verbose_print(verbose,f"Searching in {file_type} files...")
    verbose_print(verbose,"Executing:", ' '.join(find_cmd))
    verbose_print(verbose,"Executing:", ' '.join(grep_cmd))

def execute_search(verbose, find_cmd, grep_cmd, file_type):
    verbose_output(verbose, find_cmd, grep_cmd, file_type)

    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    grep_proc = subprocess.Popen(grep_cmd, stdin=find_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    find_proc.stdout.close()  # Allow find_proc to receive a SIGPIPE if grep_proc exits
    out, err = grep_proc.communicate()
    
    if out:
        print(out.decode())
    if err:
        print(f"Errors occurred while searching {file_type} files:", err.decode())

def search_pdfs(search_string, search_path, verbose):
    file_type = "*.pdf"
    print("Searching in PDF files...")
    find_cmd = ['find', search_path, '-type', 'f', '-name', file_type, '-print0']
    grep_cmd = ['xargs', '-0', 'pdfgrep', '-H', search_string]
    execute_search(verbose, find_cmd, grep_cmd, file_type)

def search_text_files(search_string, file_type, search_path, verbose):
    print(f"Searching in {file_type} files...")
    find_cmd = ['find', search_path, '-type', 'f', '-name', file_type, '-print0']
    grep_cmd = ['xargs', '-0', 'grep', '-H', search_string]
    execute_search(verbose, find_cmd, grep_cmd, file_type)

def search_images(search_string, file_type, search_path, verbose):
    print(f"Searching in {file_type} files with OCR...")
    find_cmd = ['find', search_path, '-type', 'f', '-name', file_type, '-print0']
    verbose_print(verbose,"Executing:", ' '.join(find_cmd))

    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    out, err = find_proc.communicate()
    
    if out:
        for file_path in out.decode().split('\0'):
            if file_path:
                text = ""
                if file_path.endswith(".pdf"):
                    pages = convert_from_path(file_path)
                    for page in pages:
                        text += pytesseract.image_to_string(page)
                else:
                    text += pytesseract.image_to_string(Image.open(file_path))
                
                if search_string in text:
                    print(f"Found in {file_path}")
    if err:
        print(f"Errors occurred while searching {file_type} files:", err.decode())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for a string in various file types, including PDF, text, and image files.")
    parser.add_argument("search_string", help="The string to search for.")
    parser.add_argument(
        "-t", "--types",
        nargs="*",
        help="Optional list of file types to search in (e.g., *.txt *.md *.jpg). If not provided, all files will be searched.",
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

    args = parser.parse_args()
    
    search_files(args.search_string, args.types, args.path, args.verbose)
