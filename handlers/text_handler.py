# text_handler.py
from .base_handler import BaseHandler
from models import FileResult

class TextHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        return self.process_files_in_parallel(find_cmd, self.process_text_file)

    def process_text_file(self, file_path):
        results = []
        for search_string in self.search_strings:
            grep_cmd = ['grep', '-H']
            if self.fixed:
                grep_cmd.append('-F')
            if not self.case_sensitive:
                grep_cmd.append('-i')
            grep_cmd.extend([search_string, file_path])
            if self.binary_files:
                grep_cmd.insert(2, '--binary-files=text')
            output = self.execute_search(grep_cmd, file_path)
            if output:
                results.append(FileResult(file_path, self.file_type, output))
        return results
