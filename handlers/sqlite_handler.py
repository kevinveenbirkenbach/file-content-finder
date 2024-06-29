# sqlite_handler.py
import sqlite3
from .base_handler import BaseHandler
from models import FileResult

class SQLiteHandler(BaseHandler):
    def search(self):
        find_cmd = ['find', self.search_path, '-type', 'f', '-iname', self.file_type, '-print0']
        return self.process_files_in_parallel(find_cmd, self.process_sqlite)

    def process_sqlite(self, file_path):
        results = []
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table_name in tables:
                table_name = table_name[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                column_names = [column[1] for column in columns]
                for column in column_names:
                    for search_string in self.search_strings:
                        cursor.execute(f"SELECT * FROM {table_name} WHERE {column} LIKE ?", ('%' + search_string + '%',))
                        rows = cursor.fetchall()
                        if rows:
                            content = f"Found in table {table_name}, column {column}"
                            results.append(FileResult(file_path, self.file_type, content))
            conn.close()
        except Exception as e:
            self.error_handler(str(e), file_path)
        return results
