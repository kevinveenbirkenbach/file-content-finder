# models.py
class FileResult:
    def __init__(self, path, file_type, content):
        self.path = path
        self.file_type = file_type
        self.content = content
        self.show_content = False

    def __repr__(self):
        if self.show_content:
            return f"FileResult(path={self.path}, file_type={self.file_type}, content={self.content})"
        else:
            return f"FileResult(path={self.path}, file_type={self.file_type})"

