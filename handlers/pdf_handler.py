import PyPDF2
from .grep_handler import GrepHandler
from models import FileResult

class PDFHandler(GrepHandler):
    def __init__(self, search_strings, file_type, search_path, verbose,  ignore_errors, binary_files=None, case_sensitive=None, fixed=False):
        super().__init__(search_strings, file_type, search_path, verbose,  True, binary_files, case_sensitive, fixed)

    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        return self.process_files_in_parallel(find_cmd, self.process_pdf)

    def process_pdf(self, file_path):
        results = []
        for search_string in self.search_strings:
            grep_cmd = ['pdfgrep', '-H']
            if self.fixed:
                grep_cmd.append('-F')
            if not self.case_sensitive:
                grep_cmd.append('-i')
            grep_cmd.extend([search_string, file_path])
            if self.execute_search(grep_cmd, file_path):
                file_content = self.read_pdf_content(file_path)
                results.append(FileResult(file_path, self.file_type, file_content))
        return results

    def read_pdf_content(self, file_path):
        file_content = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    file_content += page.extract_text()
        except Exception as e:
            self.error_handler(str(e), file_path)
        return file_content
