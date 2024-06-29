# xls_handler.py
import xlrd
from .base_handler import BaseHandler
from models import FileResult

class XLSHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        return self.process_files_in_parallel(find_cmd, self.process_xls)

    def process_xls(self, file_path):
        results = []
        try:
            workbook = xlrd.open_workbook(file_path)
            for sheet in workbook.sheets():
                for row_idx in range(sheet.nrows):
                    for col_idx in range(sheet.ncols):
                        cell_value = sheet.cell(row_idx, col_idx).value
                        for search_string in self.search_strings:
                            if search_string in str(cell_value):
                                results.append(FileResult(file_path, self.file_type, str(cell_value)))
        except Exception as e:
            self.error_handler(str(e), file_path)
        return results
