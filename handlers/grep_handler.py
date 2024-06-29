from .base_handler import BaseHandler
from models import FileResult
import subprocess

class GrepHandler(BaseHandler):
    def execute_search(self, cmd, file_path):
        self.verbose_print("Executing:", ' '.join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if out:
            return True
        if err:
            self.error_handler(err.decode(errors='ignore'), file_path)
        return False