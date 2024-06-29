# image_handler.py
from .base_handler import BaseHandler
import pytesseract
from PIL import Image
from models import FileResult

class ImageHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        return self.process_files_in_parallel(find_cmd, self.process_image)

    def process_image(self, file_path):
        results = []
        try:
            text = pytesseract.image_to_string(Image.open(file_path))
            for search_string in self.search_strings:
                if search_string in text:
                    results.append(FileResult(file_path, self.file_type, text))
        except Exception as e:
            self.error_handler(str(e), file_path)
        return results
