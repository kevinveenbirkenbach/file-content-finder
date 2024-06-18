import subprocess
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

def execute_search(cmd, verbose, list_only, ignore_errors, file_path):
    verbose_print(verbose, "Executing:", ' '.join(cmd))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    if out:
        try:
            output = out.decode(errors='ignore')
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

    if err:
        error_handler(list_only, err.decode(errors='ignore'), ignore_errors, cmd[-1])

def process_files_in_parallel(find_cmd, process_func, search_string, verbose, list_only, ignore_errors, binary_files=None):
    find_proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
    out, err = find_proc.communicate()

    if out:
        file_paths = out.decode(errors='ignore').split('\0')
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
