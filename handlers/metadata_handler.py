import subprocess
from .base_handler import BaseHandler
from utils import SearchUtils

class MetadataHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_metadata)

    def process_metadata(self, file_path):
        try:
            metadata = subprocess.check_output(['exiftool', file_path], universal_newlines=False)
            metadata = metadata.decode('utf-8', errors='ignore')
            SearchUtils.handle_search_result(self.search_string, metadata, file_path, self.list_only, f"Found in metadata of {file_path}")
        except Exception as e:
            self.error_handler(str(e), file_path)
