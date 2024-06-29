# composite_handler.py
from .base_handler import BaseHandler
from .image_handler import ImageHandler
from .metadata_handler import MetadataHandler

class CompositeHandler(BaseHandler):
    def __init__(self, search_strings, file_type, search_path, verbose,  ignore_errors=True, binary_files=None, case_sensitive=False, fixed=False):
        super().__init__(search_strings, file_type, search_path, verbose,  ignore_errors, binary_files, case_sensitive, fixed)
        self.handlers = [
            ImageHandler(search_strings, file_type, search_path, verbose,  ignore_errors, binary_files, case_sensitive, fixed),
            MetadataHandler(search_strings, file_type, search_path, verbose,  ignore_errors, binary_files, case_sensitive, fixed)
        ]

    def search(self):
        results = []
        for handler in self.handlers:
            results.extend(handler.search())
        return results
