import os
import subprocess
import sys
import argparse
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import xlrd
import fnmatch
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

def verbose_print(verbose, *messages):
    if verbose:
        print(" ".join(messages))

def find_all_file_types(search_path, skip_patterns):
    file_types = set()
    for root, _, files in os.walk(search_path):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext and not any(fnmatch.fnmatch(ext, pattern) for pattern in skip_patterns):
                file_types.add(f"*{ext}")
    return list(file_types)

def search_files(search_string, file_types, search_path, verbose, list_only, ignore_errors, skip_patterns, binary_files):
    if not file_types:
        file_types = find_all_file_types(search_path, skip_patterns)

    for file_type in file_types:
        verbose_print(verbose, f"Searching in {file_type} files...")
        if file_type == "*.pdf":
            search_pdfs(search_string, file_type, search_path, verbose, list_only, ignore_errors)
        elif file_type in ["*.jpeg", "*.jpg", "*.png"]:
            search_images(search_string, file_type, search_path, verbose, list_only, ignore_errors)
        elif file_type == "*.xls":
            search_xls_files(search_string, file_type, search_path, verbose, list_only, ignore_errors)
        elif file_type == "*.odp":
            search_odp_files(search_string, file_type, search_path, verbose, list_only, ignore_errors)
        else:
            search_text_files(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files)    

def error_handler(err, ignore_errors, file_type, file_path=None):
    if err:
        if file_path:
            print(f"Errors occurred while searching {file_type} files: {file_path}", file=sys.stderr)
        else:
            print(f"Errors occurred while searching {file_type} files:", err.decode(), file=sys.stderr)
        if not ignore_errors:
            sys.exit(1)

def execute_search(cmd, file_type, verbose, list_only, ignore_errors):
    verbose_print(verbose, "Executing:", ' '.join(cmd))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    
    if out:
        try:
            output = out.decode()
        except UnicodeDecodeError as e:
            error_handler(str(e), ignore_errors, file_type, cmd[-1])
            sys.exit(1)
        
        if list_only:
            results = output.strip().split('\n')
            files_found = set(result.split(':')[0] for result in results)
            for file in files_found:
                print(file)
        else:
            print(output)
    
    error_handler(err, ignore_errors, file_type)

def search_pdfs(search_string, file_type, search_path, verbose, list_only, ignore_errors):
    find_cmd = ['find', search_path, '-type', 'f', '-name', file_type, '-print0']

    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    out, err = find_proc.communicate()

    if out:
        file_paths = out.decode().split('\0')
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_pdf, file_path, search_string, verbose, list_only, ignore_errors): file_path for file_path in file_paths if file_path}
            for future in as_completed(futures):
                future.result()
    
    error_handler(err, ignore_errors, file_type)

def process_pdf(file_path, search_string, verbose, list_only, ignore_errors):
    grep_cmd = ['pdfgrep', '-H', search_string, file_path]
    execute_search(grep_cmd, "*.pdf", verbose, list_only, ignore_errors)

def search_text_files(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files):
    find_cmd = ['find', search_path, '-type', 'f', '-name', file_type, '-print0']
    
    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    out, err = find_proc.communicate()

    if out:
        file_paths = out.decode().split('\0')
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_text_file, file_path, search_string, verbose, list_only, ignore_errors, binary_files): file_path for file_path in file_paths if file_path}
            for future in as_completed(futures):
                future.result()
    
    error_handler(err, ignore_errors, file_type)

def process_text_file(file_path, search_string, verbose, list_only, ignore_errors, binary_files):
    grep_cmd = ['grep', '-H', search_string, file_path]
    if binary_files:
        grep_cmd.insert(2, '--binary-files=text')
    execute_search(grep_cmd, "*.txt", verbose, list_only, ignore_errors)

def process_image(file_path, search_string):
    text = ""
    if file_path.endswith(".pdf"):
        pages = convert_from_path(file_path)
        for page in pages:
            text += pytesseract.image_to_string(page)
    else:
        text += pytesseract.image_to_string(Image.open(file_path))
    
    if search_string in text:
        return file_path
    return None

def search_images(search_string, file_type, search_path, verbose, list_only, ignore_errors):
    find_cmd = ['find', search_path, '-type', 'f', '-name', file_type, '-print0']
    verbose_print(verbose, "Executing:", ' '.join(find_cmd))

    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    out, err = find_proc.communicate()

    if out:
        file_paths = out.decode().split('\0')
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_image, file_path, search_string): file_path for file_path in file_paths if file_path}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    if list_only:
                        print(result)
                    else:
                        print(f"Found in {result}")
    
    error_handler(err, ignore_errors, file_type)

def process_xls(file_path, search_string):
    try:
        workbook = xlrd.open_workbook(file_path)
        for sheet in workbook.sheets():
            for row_idx in range(sheet.nrows):
                for col_idx in range(sheet.ncols):
                    cell_value = sheet.cell(row_idx, col_idx).value
                    if search_string in str(cell_value):
                        return file_path
    except Exception as e:
        return str(e)
    return None

def search_xls_files(search_string, file_type, search_path, verbose, list_only, ignore_errors):
    find_cmd = ['find', search_path, '-type', 'f', '-name', file_type, '-print0']
    verbose_print(verbose, "Executing:", ' '.join(find_cmd))

    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    out, err = find_proc.communicate()

    if out:
        file_paths = out.decode().split('\0')
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_xls, file_path, search_string): file_path for file_path in file_paths if file_path}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    if isinstance(result, str) and "error" in result.lower():
                        error_handler(result, ignore_errors, file_type, file_path)
                    elif result:
                        if list_only:
                            print(result)
                        else:
                            print(f"Found in {result}")
    
    error_handler(err, ignore_errors, file_type)

def process_odp(file_path, search_string):
    try:
        with zipfile.ZipFile(file_path, 'r') as odp:
            for entry in odp.namelist():
                if entry.endswith('.xml'):
                    with odp.open(entry) as xml_file:
                        content = xml_file.read().decode('utf-8')
                        if search_string in content:
                            return file_path
    except Exception as e:
        return str(e)
    return None

def search_odp_files(search_string, file_type, search_path, verbose, list_only, ignore_errors):
    find_cmd = ['find', search_path, '-type', 'f', '-name', file_type, '-print0']
    verbose_print(verbose, "Executing:", ' '.join(find_cmd))

    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    out, err = find_proc.communicate()

    if out:
        file_paths = out.decode().split('\0')
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_odp, file_path, search_string): file_path for file_path in file_paths if file_path}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    if isinstance(result, str) and "error" in result.lower():
                        error_handler(result, ignore_errors, file_type, file_path)
                    elif result:
                        if list_only:
                            print(result)
                        else:
                            print(f"Found in {result}")
    
    error_handler(err, ignore_errors, file_type)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for a string in various file types, including PDF, text, image, xls, and odp files.")
    parser.add_argument("search_string", help="The string to search for.")
    parser.add_argument(
        "-t", "--types",
        nargs="*",
        help="Optional list of file types to search in (e.g., *.txt *.md *.jpg *.xls *.odp). If not provided, all files will be searched.",
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
        help="Optional list of file extensions to skip (e.g., .zip .tar .gz).",
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
        '.ldb',        # https://learn.microsoft.com/de-de/office/troubleshoot/access/ldb-file-description
        '.log',
        '.mp4',
        '.old',
        '.sqlite', 
        '.tar', 
        '.zip',
        '.xcf'
    ]

    if args.add:
        skip_patterns = default_skip + args.skip
    else:
        skip_patterns = args.skip
    
    search_files(args.search_string, args.types, args.path, args.verbose, args.list, args.ignore, skip_patterns, args.binary_files)
