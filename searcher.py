# searcher.py
import os
import fnmatch
from handlers.pdf_handler import PDFHandler
from handlers.text_handler import TextHandler
from handlers.xls_handler import XLSHandler
from handlers.doc_handler import DocHandler
from handlers.sqlite_handler import SQLiteHandler
from handlers.odp_handler import ODPHandler
from handlers.metadata_handler import MetadataHandler
from handlers.composite_handler import CompositeHandler
from handlers.pptx_handler import PPTXHandler
from handlers.odt_handler import ODTHandler 

class Searcher:
    def __init__(self, search_strings, file_types, search_path, verbose, list_only, ignore_errors, skip_patterns, binary_files, case_sensitive, fixed):
        self.search_strings = search_strings
        self.file_types = file_types
        self.search_path = search_path
        self.verbose = verbose
        self.list_only = list_only
        self.ignore_errors = ignore_errors
        self.skip_patterns = skip_patterns
        self.binary_files = binary_files
        self.case_sensitive = case_sensitive
        self.fixed = fixed

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
            "*.jpeg": CompositeHandler,
            "*.jpg": CompositeHandler,
            "*.png": CompositeHandler,
            "*.xls": XLSHandler,
            "*.odp": ODPHandler,
            "*.odt": ODTHandler,
            #"*.doc": DocHandler,
            "*.pptx": PPTXHandler,
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
            handler = handler_class(self.search_strings, normalized_file_type, self.search_path, self.verbose, self.list_only, self.ignore_errors, self.binary_files, self.case_sensitive, self.fixed)
            handler.search()
