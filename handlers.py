import subprocess
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import xlrd
import zipfile
import docx
import sqlite3
from mutagen import File as MutagenFile
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

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
                        content = xml_file.read()decode('utf-8', errors='ignore')
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

def process_metadata(file_path, search_string, verbose, list_only, ignore_errors, binary_files=None):
    try:
        metadata = subprocess.check_output(['exiftool', file_path], universal_newlines=True)
        if search_string in metadata:
            if list_only:
                print(file_path)
            else:
                print(f"Found in metadata of {file_path}")
        return None
    except Exception as e:
        error_handler(list_only, str(e), ignore_errors, file_path)
    return None

def search_audio_files(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files=None):
    find_cmd = ['find', search_path, '-type', 'f', '-iname', file_type, '-print0']
    process_files_in_parallel(find_cmd, process_metadata, search_string, verbose, list_only, ignore_errors)

def search_video_files(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files=None):
    find_cmd = ['find', search_path, '-type', 'f', '-iname', file_type, '-print0']
    process_files_in_parallel(find_cmd, process_metadata, search_string, verbose, list_only, ignore_errors)

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

def verbose_print(verbose, *messages):
    if verbose:
        print(" ".join(messages))
