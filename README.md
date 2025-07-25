# nakedmole

This repository contains a simple Python script for renaming PDF files using information extracted from their metadata.

## Script

`rename_pdfs.py` provides a small Tkinter-based interface that lets you choose a folder, decide whether to include subfolders, and select between renaming files individually or in batch mode. The script relies on `PyPDF2` to read each file's metadata (Title, Author and CreationDate) and renames the file accordingly. In batch mode, a `read.me` report is created listing the original and new file names.

Install the required dependency with:

```bash
pip install PyPDF2
```

Run the script with:

```bash
python3 rename_pdfs.py
```

A window will open asking you to select the folder and options.
