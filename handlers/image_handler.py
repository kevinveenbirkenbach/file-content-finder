from .base_handler import BaseHandler
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from utils import SearchUtils

class ImageHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_image)

    def process_image(self, file_path):
        try:
            text = pytesseract.image_to_string(Image.open(file_path))
            SearchUtils.handle_search_result(self.search_string, text, file_path, self.list_only)
        except Exception as e:
            self.error_handler(str(e), file_path)
