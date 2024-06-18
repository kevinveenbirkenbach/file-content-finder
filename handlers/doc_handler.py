# doc_handler.py
import docx
from .base_handler import BaseHandler
from utils import SearchUtils

class DocHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_doc)

    def process_doc(self, file_path):
        try:
            doc = docx.Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text
            for search_string in self.search_strings:
                SearchUtils.handle_search_result(search_string, text, file_path, self.list_only)
        except Exception as e:
            self.error_handler(str(e), file_path)
