import zipfile
from .base_handler import BaseHandler

class ODPHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_odp)

    def process_odp(self, file_path):
        try:
            with zipfile.ZipFile(file_path, 'r') as odp:
                for entry in odp.namelist():
                    if entry.endswith('.xml'):
                        with odp.open(entry) as xml_file:
                            content = xml_file.read().decode('utf-8', errors='ignore')
                            if self.search_string in content:
                                if self.list_only:
                                    print(file_path)
                                else:
                                    print(f"Found in {file_path}")
        except Exception as e:
            self.error_handler(str(e), file_path)
