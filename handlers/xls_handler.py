import xlrd
from .base_handler import BaseHandler

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
                        if self.search_string in str(cell_value):
                            if self.list_only:
                                print(file_path)
                            else:
                                print(f"Found in {file_path}")
        except Exception as e:
            self.error_handler(str(e), file_path)
