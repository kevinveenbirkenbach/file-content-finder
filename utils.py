class SearchUtils:
    @staticmethod
    def handle_search_result(search_string, text, file_path, list_only, message=None):
        if search_string in text:
            if list_only:
                print(file_path)
            else:
                if message:
                    print(message)
                else:
                    print(f"Found in {file_path}")
