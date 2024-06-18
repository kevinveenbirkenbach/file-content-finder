# composite_handler.py
from .base_handler import BaseHandler
from .image_handler import ImageHandler
from .metadata_handler import MetadataHandler

class CompositeHandler(BaseHandler):
    def __init__(self, search_strings, file_type, search_path, verbose, list_only, ignore_errors=True, binary_files=None, case_sensitive=False):
        super().__init__(search_strings, file_type, search_path, verbose, list_only, ignore_errors, binary_files, case_sensitive)
        self.handlers = [
            ImageHandler(search_strings, file_type, search_path, verbose, list_only, ignore_errors, binary_files, case_sensitive),
            MetadataHandler(search_strings, file_type, search_path, verbose, list_only, ignore_errors, binary_files, case_sensitive)
        ]

    def search(self):
        for handler in self.handlers:
            handler.search()
