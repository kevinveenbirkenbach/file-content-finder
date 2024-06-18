# handlers/ppt_handler.py
import subprocess
from .pptx_handler import PPTXHandler

class PPTHandler(PPTXHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_ppt)

    def process_ppt(self, file_path):
        converted_path = self.convert_to_pptx(file_path)
        if converted_path:
            self.process_pptx(converted_path)
        else:
            self.error_handler(f"Failed to convert {file_path} to .pptx", file_path)

    def convert_to_pptx(self, file_path):
        try:
            converted_path = f"{file_path}.pptx"
            subprocess.run(['unoconv', '-f', 'pptx', '-o', converted_path, file_path], check=True)
            return converted_path
        except subprocess.CalledProcessError as e:
            self.error_handler(str(e), file_path)
            return None
