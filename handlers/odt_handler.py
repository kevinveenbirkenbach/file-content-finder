# odt_handler.py
import zipfile
from xml.etree import ElementTree as ET
from .base_handler import BaseHandler
from models import FileResult

class ODTHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        return self.process_files_in_parallel(find_cmd, self.process_odt)

    def process_odt(self, file_path):
        results = []
        if not self.is_zipfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for search_string in self.search_strings:
                        if search_string in content:
                            results.append(FileResult(file_path, self.file_type, content))
            except Exception as e:
                self.error_handler(str(e), file_path)
            return results

        try:
            with zipfile.ZipFile(file_path, 'r') as odt:
                for entry in odt.namelist():
                    if entry == 'content.xml':
                        with odt.open(entry) as xml_file:
                            content = xml_file.read().decode('utf-8', errors='ignore')
                            text = self.extract_text_from_odt(content)
                            for search_string in self.search_strings:
                                if search_string in text:
                                    results.append(FileResult(file_path, self.file_type, text))
        except Exception as e:
            self.error_handler(str(e), file_path)
        return results

    def is_zipfile(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                return zipfile.is_zipfile(f)
        except IOError:
            return False

    def extract_text_from_odt(self, content):
        try:
            root = ET.fromstring(content)
            text_elements = root.findall('.//{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p')
            text = ''.join([elem.text for elem in text_elements if elem.text])
            return text
        except ET.ParseError:
            return ""
