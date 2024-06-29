# doc_handler.py
import docx
from .base_handler import BaseHandler
from models import FileResult

class DocHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        return self.process_files_in_parallel(find_cmd, self.process_doc)

    def process_doc(self, file_path):
        results = []
        try:
            doc = docx.Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text
            for search_string in self.search_strings:
                if search_string in text:
                    results.append(FileResult(file_path, self.file_type, text))
        except Exception as e:
            self.error_handler(str(e), file_path)
        return results
