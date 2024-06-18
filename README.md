# File Content Finder

This repository contains `search_files.py`, a script to search for a string in various file types, including PDF, text, and image files.

## Usage

```bash
python search_files.py [-h] [-t [TYPES [TYPES ...]]] [-p PATH] [-v] [-l] [-i] search_string
```

### Positional Arguments

- `search_string`: The string to search for.

### Optional Arguments

- `-t`, `--types`: Optional list of file types to search in (e.g., `*.txt`, `*.md`, `*.jpg`). If not provided, all files will be searched.
- `-p`, `--path`: The path to search in. If not provided, the current directory will be used.
- `-v`, `--verbose`: Print the executed commands.
- `-l`, `--list`: Only list files containing the search string, without additional information.
- `-i`, `--ignore`: Ignore errors and continue searching.

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

## Author

- **Kevin Veen-Birkenbach**
  - Email: kevin@veen.world
  - Website: [https://www.veen.world/](https://www.veen.world/)

## License

This project is licensed under the GNU Affero General Public License, Version 3, 19 November 2007.

## AI Assistance

This code was generated with the help of AI. For more details, refer to this [chat conversation with ChatGPT](https://chatgpt.com/share/7eae44ac-d4c0-4978-9e8e-bfa85dcc4b75).
