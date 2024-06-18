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
from functools import partial
import docx
import sqlite3

def verbose_print(verbose, *messages):
    if verbose:
        print(" ".join(messages))

def find_all_file_types(search_path, skip_patterns):
    file_types = set()
    for root, _, files in os.walk(search_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()  # Normalize to lower case
            if ext and not any(fnmatch.fnmatch(ext, pattern.lower()) for pattern in skip_patterns):
                file_types.add(f"*{ext}")
    return list(file_types)

def search_files(search_string, file_types, search_path, verbose, list_only, ignore_errors, skip_patterns, binary_files):
    if not search_path.endswith('/'):
        search_path += '/'
    
    if not file_types:
        file_types = find_all_file_types(search_path, skip_patterns)
    
    dispatch = {
        "*.pdf": search_pdfs,
        "*.jpeg": search_images,
        "*.jpg": search_images,
        "*.png": search_images,
        "*.xls": search_xls_files,
        "*.odp": search_odp_files,
        "*.doc": search_doc_files,
        "*.sqlite": search_sqlite_files,
    }

    for file_type in file_types:
        normalized_file_type = file_type.lower()
        verbose_print(verbose, f"Searching in {file_type} files with normalized type {normalized_file_type}...")
        search_function = dispatch.get(normalized_file_type, search_text_files)
        search_function(search_string, normalized_file_type, search_path, verbose, list_only, ignore_errors, binary_files)

class SearchExecutionError(Exception):
    def __init__(self, message, file_path):
        super().__init__(
            f"Error occurred during search execution in {file_path}: {message}"
        )

def error_handler(list_only, err, ignore_errors, file_path):
    if err:
        execution_exception = SearchExecutionError(err, file_path)
        if not list_only:
            print(f"Ignoring the following error: {execution_exception}")
        if not ignore_errors:
            raise execution_exception

def execute_search(cmd, verbose, list_only, ignore_errors, file_type=None):
    verbose_print(verbose, "Executing:", ' '.join(cmd))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    if out:
        try:
            output = out.decode()
        except UnicodeDecodeError as e:
            error_handler(list_only, str(e), ignore_errors, cmd[-1])
            return  # Ensure the function exits if error_handler is called

        if list_only:
            results = output.strip().split('\n')
            files_found = set(result.split(':')[0] for result in results)
            for file in files_found:
                print(file)
        else:
            print(output)

    error_handler(list_only, err, ignore_errors, cmd[-1])

def search_pdfs(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files=None):
    find_cmd = ['find', search_path, '-type', 'f', '-iname', file_type, '-print0']
    process_files_in_parallel(find_cmd, process_pdf, search_string, verbose, list_only, ignore_errors, binary_files)

def process_pdf(file_path, search_string, verbose, list_only, ignore_errors, binary_files):
    grep_cmd = ['pdfgrep', '-H', search_string, file_path]
    execute_search(grep_cmd, verbose, list_only, True, "*.pdf")

def search_text_files(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files):
    find_cmd = ['find', search_path, '-type', 'f', '-iname', file_type, '-print0']
    process_files_in_parallel(find_cmd, process_text_file, search_string, verbose, list_only, ignore_errors, binary_files=binary_files)

def process_text_file(file_path, search_string, verbose, list_only, ignore_errors, binary_files):
    grep_cmd = ['grep', '-H', search_string, file_path]
    if binary_files:
        grep_cmd.insert(2, '--binary-files=text')
    execute_search(grep_cmd, verbose, list_only, ignore_errors, "*.txt")

def process_image(file_path, search_string, verbose, list_only, ignore_errors, binary_files):
    try:
        text = ""
        if file_path.endswith(".pdf"):
            pages = convert_from_path(file_path)
            for page in pages:
                text += pytesseract.image_to_string(page)
        else:
            text += pytesseract.image_to_string(Image.open(file_path))

        if search_string in text:
            if list_only:
                print(file_path)
            else:
                print(f"Found in {file_path}")
        return None
    except Exception as e:
        error_handler(list_only, str(e), ignore_errors, file_path)
    return None

def search_images(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files=None):
    find_cmd = ['find', search_path, '-type', 'f', '-iname', file_type, '-print0']
    process_files_in_parallel(find_cmd, process_image, search_string, verbose, list_only, ignore_errors)

def process_xls(file_path, search_string, verbose, list_only, ignore_errors, binary_files=None):
    try:
        workbook = xlrd.open_workbook(file_path)
        for sheet in workbook.sheets():
            for row_idx in range(sheet.nrows):
                for col_idx in range(sheet.ncols):
                    cell_value = sheet.cell(row_idx, col_idx).value
                    if search_string in str(cell_value):
                        if list_only:
                            print(file_path)
                        else:
                            print(f"Found in {file_path}")
                        return file_path
    except Exception as e:
        error_handler(list_only, str(e), ignore_errors, file_path)
    return None

def search_xls_files(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files=None):
    find_cmd = ['find', search_path, '-type', 'f', '-iname', file_type, '-print0']
    process_files_in_parallel(find_cmd, process_xls, search_string, verbose, list_only, ignore_errors)

def process_doc(file_path, search_string, verbose, list_only, ignore_errors, binary_files=None):
    try:
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text
        if search_string in text:
            if list_only:
                print(file_path)
            else:
                print(f"Found in {file_path}")
        return None
    except Exception as e:
        error_handler(list_only, str(e), ignore_errors, file_path)
    return None

def search_doc_files(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files=None):
    find_cmd = ['find', search_path, '-type', 'f', '-iname', file_type, '-print0']
    process_files_in_parallel(find_cmd, process_doc, search_string, verbose, list_only, ignore_errors)

def process_sqlite(file_path, search_string, verbose, list_only, ignore_errors, binary_files=None):
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table_name in tables:
            table_name = table_name[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            for column in column_names:
                cursor.execute(f"SELECT * FROM {table_name} WHERE {column} LIKE ?", ('%' + search_string + '%',))
                rows = cursor.fetchall()
                if rows:
                    if list_only:
                        print(file_path)
                    else:
                        print(f"Found in {file_path} in table {table_name}, column {column}")
                    return None
        conn.close()
    except Exception as e:
        error_handler(list_only, str(e), ignore_errors, file_path)
    return None

def search_sqlite_files(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files=None):
    find_cmd = ['find', search_path, '-type', 'f', '-iname', file_type, '-print0']
    process_files_in_parallel(find_cmd, process_sqlite, search_string, verbose, list_only, ignore_errors)

def process_odp(file_path, search_string, verbose, list_only, ignore_errors, binary_files=None):
    try:
        with zipfile.ZipFile(file_path, 'r') as odp:
            for entry in odp.namelist():
                if entry.endswith('.xml'):
                    with odp.open(entry) as xml_file:
                        content = xml_file.read().decode('utf-8')
                        if search_string in content:
                            if list_only:
                                print(file_path)
                            else:
                                print(f"Found in {file_path}")
                            return file_path
    except Exception as e:
        error_handler(list_only, str(e), ignore_errors, file_path)
    return None

def search_odp_files(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files=None):
    find_cmd = ['find', search_path, '-type', 'f', '-iname', file_type, '-print0']
    process_files_in_parallel(find_cmd, process_odp, search_string, verbose, list_only, ignore_errors)

def process_files_in_parallel(find_cmd, process_func, search_string, verbose, list_only, ignore_errors, binary_files=None):
    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    out, err = find_proc.communicate()

    if out:
        file_paths = out.decode().split('\0')
        verbose_print(verbose, f"Processing {len(file_paths)} files...")
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(partial(process_func, file_path, search_string, verbose, list_only, ignore_errors, binary_files)): file_path for file_path in file_paths if file_path}
            try:
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        if isinstance(result, str) and "error" in result.lower():
                            error_handler(list_only, result, ignore_errors, file_path)
                        elif result:
                            if list_only:
                                print(result)
                            else:
                                print(f"Found in {result}")
            except KeyboardInterrupt:
                for future in futures:
                    future.cancel()
                raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for a string in various file types, including PDF, text, image, xls, doc, and odp files.")
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
        '.log',
        '.mp3',
        '.mp4',
        '.old',
        '.tar', 
        '.zip',
        '.xcf'
    ]

    if args.add:
        skip_patterns = default_skip + [pattern.lower() for pattern in args.skip]
    else:
        skip_patterns = [pattern.lower() for pattern in args.skip]
    
    search_files(args.search_string, args.types, args.path, args.verbose, args.list, args.ignore, skip_patterns, args.binary_files)
