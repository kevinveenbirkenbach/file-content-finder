# metadata_handler.py
import subprocess
from .base_handler import BaseHandler
from models import FileResult

class MetadataHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        return self.process_files_in_parallel(find_cmd, self.process_metadata)

    def process_metadata(self, file_path):
        results = []
        try:
            metadata = subprocess.check_output(['exiftool', file_path], universal_newlines=False)
            metadata = metadata.decode('utf-8', errors='ignore')
            for search_string in self.search_strings:
                if search_string in metadata:
                    results.append(FileResult(file_path, self.file_type, metadata))
        except Exception as e:
            self.error_handler(str(e), file_path)
        return results
