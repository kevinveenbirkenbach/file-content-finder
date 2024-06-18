import subprocess
from .base_handler import BaseHandler

class MetadataHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_metadata)

    def process_metadata(self, file_path):
        try:
            metadata = subprocess.check_output(['exiftool', file_path], universal_newlines=True)
            if self.search_string in metadata:
                if self.list_only:
                    print(file_path)
                else:
                    print(f"Found in metadata of {file_path}")
        except Exception as e:
            self.error_handler(str(e), file_path)
