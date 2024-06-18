from .base_handler import BaseHandler

class PDFHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_pdf)

    def process_pdf(self, file_path):
        grep_cmd = ['pdfgrep', '-H', self.search_string, file_path]
        self.execute_search(grep_cmd, file_path)
