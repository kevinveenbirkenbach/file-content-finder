from .base_handler import BaseHandler
from .image_handler import ImageHandler
from .metadata_handler import MetadataHandler

class CompositeHandler(BaseHandler):
    def __init__(self, search_string, file_type, search_path, verbose, list_only, ignore_errors=True, binary_files=None):
        super().__init__(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files)
        self.handlers = [
            ImageHandler(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files),
            MetadataHandler(search_string, file_type, search_path, verbose, list_only, ignore_errors, binary_files)
        ]

    def search(self):
        for handler in self.handlers:
            handler.search()
