from .base_handler import BaseHandler

class PDFHandler(BaseHandler):
    def __init__(self, search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files=None):
        super().__init__(search_string, file_type, search_path, verbose, list_only, True, binary_files)
    
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_pdf)

    def process_pdf(self, file_path):
        grep_cmd = ['pdfgrep', '-H', self.search_string, file_path]
        self.execute_search(grep_cmd, file_path)
