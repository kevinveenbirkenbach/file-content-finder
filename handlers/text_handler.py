from .base_handler import BaseHandler

class TextHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_text_file)

    def process_text_file(self, file_path):
        grep_cmd = ['grep', '-H', self.search_string, file_path]
        if self.binary_files:
            grep_cmd.insert(2, '--binary-files=text')
        self.execute_search(grep_cmd, file_path)
