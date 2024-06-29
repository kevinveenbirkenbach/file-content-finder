import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

class SearchExecutionError(Exception):
    def __init__(self, message, file_path):
        super().__init__(
            f"Error occurred during search execution in {file_path}: {message}"
        )

def error_handler(err, ignore_errors, file_path, verbose):
    if err:
        execution_exception = SearchExecutionError(err, file_path)
        if not ignore_errors:
            raise execution_exception
        if not verbose:
            print(f"Ignoring the following error: {execution_exception}")

def process_files_in_parallel(find_cmd, process_func, search_string, verbose,  ignore_errors, binary_files=None):
    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    out, err = find_proc.communicate()

    if out:
        file_paths = out.decode(errors='ignore').split('\0')
        verbose_print(verbose, f"Processing {len(file_paths)} files...")
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(partial(process_func, file_path, search_string, verbose,  ignore_errors, binary_files)): file_path for file_path in file_paths if file_path}
            try:
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        if isinstance(result, str) and "error" in result.lower():
                            error_handler(result, ignore_errors, file_path, verbose)
                        elif result:
                            print(result)
            except KeyboardInterrupt:
                for future in futures:
                    future.cancel()
                raise

def verbose_print(verbose, *messages):
    if verbose:
        print(" ".join(messages))
