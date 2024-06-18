# base_handler.py
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

class BaseHandler:
    def __init__(self, search_strings, file_type, search_path, verbose, list_only, ignore_errors, binary_files=None, case_sensitive=False, fixed=False):
        self.search_strings = search_strings
        self.file_type = file_type
        self.search_path = search_path
        self.verbose = verbose
        self.list_only = list_only
        self.ignore_errors = ignore_errors
        self.binary_files = binary_files
        self.case_sensitive = case_sensitive
        self.fixed = fixed

    def verbose_print(self, *messages):
        if self.verbose:
            print(" ".join(messages))

    def error_handler(self, err, file_path):
        if err:
            if self.ignore_errors:
                print(f"Ignoring error: {err}")
            else:
                raise Exception(f"Error occurred during search execution in {file_path}: {err}")

    def execute_search(self, cmd, file_path):
        self.verbose_print("Executing:", ' '.join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if out:
            output = out.decode(errors='ignore')
            if self.list_only:
                files_found = {line.split(':')[0] for line in output.strip().split('\n')}
                for file in files_found:
                    print(file)
            else:
                print(output)
        if err:
            self.error_handler(err.decode(errors='ignore'), file_path)

    def process_files_in_parallel(self, find_cmd, process_func):
        proc = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
        out, _ = proc.communicate()
        if out:
            file_paths = out.decode().split('\0')
            self.verbose_print(f"Processing {len(file_paths)} files...")
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(partial(process_func, file_path)): file_path for file_path in file_paths if file_path}
                try:
                    for future in as_completed(futures):
                        result = future.result()
                        if result and not self.list_only:
                            print(f"Found in {result}")
                except KeyboardInterrupt:
                    for future in futures:
                        future.cancel()
                    raise

    def search(self):
        raise NotImplementedError("Subclasses must implement this method.")
