# File Content Finder

This repository contains `file-content-finder`, a set of scripts to search for a string in various file types, including PDFs, text files, images, spreadsheets, documents, SQLite databases, and more.

## Features

- Search for a string in multiple file types: PDFs, text, images, Excel files, documents, SQLite databases, audio, and video files.
- Support for case-insensitive search.
- Option to list only the files containing the search string.
- Verbose mode to print executed commands.
- Error handling with options to ignore errors and continue searching.

## Installation

### Prerequisites

Ensure you have the following installed on your system:

1. **Python 3**: This script requires Python 3.
2. **Package Managers**: `yay` and `pacman` for Arch Linux.
3. **Pip**: Python package manager.

### Install Dependencies

Run the following commands to install necessary packages:

```bash
# Using yay for AUR packages
yay -S python-pdf2image
yay -S python-pypdf2

# Using pacman for official repository packages
sudo pacman -S python-pytesseract
sudo pacman -S tesseract-data-eng
sudo pacman -S pdfgrep
sudo pacman -S python-xlrd

# Using pip for Python packages
pip install xlrd
pip install pdf2image
pip install pytesseract
```

### Clone the Repository

```bash
git clone https://github.com/kevinveenbirkenbach/file-content-finder.git
cd file-content-finder
```

### Requirements File

Here is the `requirements.txt` file for pip:

```text
pytesseract
pdf2image
xlrd
PyPDF2
mutagen
docx
```

To install the Python dependencies using `pip`, run:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python search_files.py [-h] [-t [TYPES [TYPES ...]]] [-p PATH] [-v] [-l] [-i] [-s [SKIP [SKIP ...]]] [-a] [-b] search_string
```

### Positional Arguments

- `search_string`: The string to search for.

### Optional Arguments

- `-t`, `--types`: Optional list of file types to search in (e.g., `*.txt`, `*.md`, `*.jpg`). If not provided, all files will be searched.
- `-p`, `--path`: The path to search in. If not provided, the current directory will be used.
- `-v`, `--verbose`: Print the executed commands.
- `-l`, `--list`: Only list files containing the search string, without additional information.
- `-i`, `--ignore`: Ignore errors and continue searching.
- `-s`, `--skip`: Optional list of file extensions to skip (e.g., `.zip`, `.tar`, `.gz`).
- `-a`, `--add`: Extend the default list of skipped files.
- `-b`, `--binary-files`: Treat binary files as text for searching.

### Examples

Search for the string "example" in all files in the current directory:

```bash
python search_files.py "example"
```

Search for the string "example" in `.txt` and `.md` files in a specific directory:

```bash
python search_files.py "example" -t "*.txt" "*.md" -p /path/to/search
```

Search for the string "example" in all files and print the executed commands:

```bash
python search_files.py "example" -v
```

Search for the string "example" and only list the files containing the string:

```bash
python search_files.py "example" -l
```

Search for the string "example" and ignore any errors encountered:

```bash
python search_files.py "example" -i
```

## Setup

To install the required Python packages, run:

```bash
pip install -r requirements.txt
```

## Author

- **Kevin Veen-Birkenbach**
  - Email: kevin@veen.world
  - Website: [https://www.veen.world/](https://www.veen.world/)

## License

This project is licensed under the GNU Affero General Public License, Version 3, 19 November 2007.

## AI Assistance

This code was generated with the help of AI. For more details, refer to this [chat conversation with ChatGPT](https://chatgpt.com/share/7eae44ac-d4c0-4978-9e8e-bfa85dcc4b75).
