# xls_handler.py
import xlrd
from .base_handler import BaseHandler
from utils import SearchUtils

class XLSHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        self.process_files_in_parallel(find_cmd, self.process_xls)

    def process_xls(self, file_path):
        try:
            workbook = xlrd.open_workbook(file_path)
            for sheet in workbook.sheets():
                for row_idx in range(sheet.nrows):
                    for col_idx in range(sheet.ncols):
                        cell_value = sheet.cell(row_idx, col_idx).value
                        for search_string in self.search_strings:
                            SearchUtils.handle_search_result(search_string, str(cell_value), file_path, self.list_only)
        except Exception as e:
            self.error_handler(str(e), file_path)
