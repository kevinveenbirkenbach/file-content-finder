# pdf_handler.py
from .base_handler import BaseHandler

class PDFHandler(BaseHandler):
    def __init__(self, search_strings, file_type, search_path, verbose, list_only, ignore_errors, binary_files=None, case_sensitive=None, fixed=False):
        super().__init__(search_strings, file_type, search_path, verbose, list_only, True, binary_files, case_sensitive, fixed)

    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_pdf)

    def process_pdf(self, file_path):
        for search_string in self.search_strings:
            grep_cmd = ['pdfgrep', '-H']
            if self.fixed:
                grep_cmd.append('-F')
            if not self.case_sensitive:
                grep_cmd.append('-i')
            grep_cmd.extend([search_string, file_path])
            self.execute_search(grep_cmd, file_path)
