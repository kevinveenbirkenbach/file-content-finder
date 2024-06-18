# handlers/pptx_handler.py
from pptx import Presentation
from .base_handler import BaseHandler
from utils import SearchUtils

class PPTXHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_pptx)

    def process_pptx(self, file_path):
        try:
            prs = Presentation(file_path)
            text = ""
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text
            SearchUtils.handle_search_result(self.search_string, text, file_path, self.list_only)
        except Exception as e:
            self.error_handler(str(e), file_path)
