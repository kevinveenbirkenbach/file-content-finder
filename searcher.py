import os
import fnmatch
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from handlers import (
    PDFHandler, TextHandler, ImageHandler, XLSHandler,
    DocHandler, SQLiteHandler, ODPHandler, MetadataHandler
)

class Searcher:
    def __init__(self, search_string, file_types, search_path, verbose, list_only, ignore_errors, skip_patterns, binary_files):
        self.search_string = search_string
        self.file_types = file_types
        self.search_path = search_path
        self.verbose = verbose
        self.list_only = list_only
        self.ignore_errors = ignore_errors
        self.skip_patterns = skip_patterns
        self.binary_files = binary_files

    def verbose_print(self, *messages):
        if self.verbose:
            print(" ".join(messages))

    def find_all_file_types(self):
        file_types = set()
        for root, _, files in os.walk(self.search_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()  # Normalize to lower case
                if ext and not any(fnmatch.fnmatch(ext, pattern.lower()) for pattern in self.skip_patterns):
                    file_types.add(f"*{ext}")
        return list(file_types)

    def search_files(self):
        if not self.search_path.endswith('/'):
            self.search_path += '/'
        
        if not self.file_types:
            self.file_types = self.find_all_file_types()
        
        dispatch = {
            "*.pdf": PDFHandler,
            "*.jpeg": ImageHandler,
            "*.jpg": ImageHandler,
            "*.png": ImageHandler,
            "*.xls": XLSHandler,
            "*.odp": ODPHandler,
            "*.odt": DocHandler,
            "*.doc": DocHandler,
            "*.ppt": ODPHandler,
            "*.sqlite": SQLiteHandler,
            "*.mp3": MetadataHandler,
            "*.wav": MetadataHandler,
            "*.flac": MetadataHandler,
            "*.mp4": MetadataHandler,
            "*.avi": MetadataHandler,
            "*.mov": MetadataHandler,
            "*.wmv": MetadataHandler,
        }

        for file_type in self.file_types:
            normalized_file_type = file_type.lower()
            self.verbose_print(f"Searching in {file_type} files with normalized type {normalized_file_type}...")
            handler_class = dispatch.get(normalized_file_type, TextHandler)
            handler = handler_class(self.search_string, normalized_file_type, self.search_path, self.verbose, self.list_only, self.ignore_errors, self.binary_files)
            handler.search()