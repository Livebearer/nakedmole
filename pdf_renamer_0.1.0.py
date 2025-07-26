__version__ = '0.1.0'
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

from PyPDF2 import PdfReader

def ask_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select folder with PDF files")
    root.destroy()
    if not folder:
        folder = os.getcwd()
    return folder

def ask_options():
    root = tk.Tk()
    root.title("PDF Renamer Options")
    recursive_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Include subfolders", variable=recursive_var).pack(anchor="w")
    mode_var = tk.StringVar(value="single")
    tk.Radiobutton(root, text="Rename one by one", variable=mode_var, value="single").pack(anchor="w")
    tk.Radiobutton(root, text="Rename all", variable=mode_var, value="batch").pack(anchor="w")

    def submit():
        root.quit()

    tk.Button(root, text="Start", command=submit).pack(pady=10)
    root.mainloop()
    mode = mode_var.get()
    recursive = recursive_var.get()
    root.destroy()
    return mode, recursive

def find_pdfs(folder, recursive=False):
    pdfs = []
    if recursive:
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower().endswith('.pdf'):
                    pdfs.append(os.path.join(root, f))
    else:
        for f in os.listdir(folder):
            if f.lower().endswith('.pdf'):
                pdfs.append(os.path.join(folder, f))
    return sorted(pdfs)

def _extract_meta_field(text, key):
    match = re.search(r'/%s\s*\((.*?)\)' % re.escape(key), text)
    return match.group(1).strip() if match else ''

def extract_pdf_metadata(path):
    """Return title, author and year from PDF metadata."""
    try:
        reader = PdfReader(path)
        info = reader.metadata or {}
        title = info.get("/Title") or ""
        author = info.get("/Author") or ""
        creation = info.get("/CreationDate") or ""
    except (ValueError, KeyError, TypeError):
        with open(path, "rb") as f:
            data = f.read(8192)
        text = data.decode("latin1", errors="ignore")
        title = _extract_meta_field(text, "Title")
        author = _extract_meta_field(text, "Author")
        creation = _extract_meta_field(text, "CreationDate")

    year_match = re.search(r"(\d{4})", str(creation))
    year = year_match.group(1) if year_match else ""
    return {
        "title": title,
        "author": author,
        "year": year,
    }

def shorten_title(title, limit=60):
    t = re.sub(r'\s+', ' ', title).strip()
    if len(t) > limit:
        t = t[:limit]
    return t

def sanitize(text):
    return re.sub(r'[\s/\\:*?"<>|]', '_', text)

def build_new_name(meta, ext):
    authors_raw = meta.get('author', '')
    authors = [a.strip() for a in re.split(r';|,| and |\band\b', authors_raw) if a.strip()]
    year = meta.get('year', '')
    title_short = sanitize(shorten_title(meta.get('title', '')))
    if len(authors) > 3:
        author_part = f"{sanitize(authors[0])}_etal"
    elif len(authors) == 3:
        author_part = f"{sanitize(authors[0])},{sanitize(authors[1])}/&{sanitize(authors[2])}"
    elif len(authors) == 2:
        author_part = f"{sanitize(authors[0])},{sanitize(authors[1])}"
    elif len(authors) == 1:
        author_part = sanitize(authors[0])
    else:
        author_part = 'unknown'
    return f"{author_part}{year}.{title_short}{ext}"

def ensure_unique_filename(path):
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    i = 1
    while os.path.exists(f"{base}_{i}{ext}"):
        i += 1
    return f"{base}_{i}{ext}"

def rename_interactive(files):
    renamed = []
    for fpath in files:
        meta = extract_pdf_metadata(fpath)
        new_name = build_new_name(meta, os.path.splitext(fpath)[1])
        new_path = ensure_unique_filename(os.path.join(os.path.dirname(fpath), new_name))
        root = tk.Tk(); root.withdraw()
        ans = messagebox.askyesno('Rename file?', f"Rename\n{os.path.basename(fpath)}\nto\n{os.path.basename(new_path)}?")
        root.destroy()
        if ans:
            os.rename(fpath, new_path)
            renamed.append((fpath, new_path))
    return renamed

def rename_batch(files):
    renamed = []
    progress = tk.Tk()
    progress.title("Renaming PDFs")
    bar = ttk.Progressbar(progress, length=300, mode='determinate', maximum=len(files))
    bar.pack(pady=20)
    progress.update()
    for idx, fpath in enumerate(files):
        meta = extract_pdf_metadata(fpath)
        new_name = build_new_name(meta, os.path.splitext(fpath)[1])
        new_path = ensure_unique_filename(os.path.join(os.path.dirname(fpath), new_name))
        os.rename(fpath, new_path)
        renamed.append((fpath, new_path))
        bar['value'] = idx + 1
        progress.update()
    progress.destroy()
    return renamed

def write_report(folder, renamed):
    report_path = os.path.join(folder, 'read.me')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"Renaming session: {datetime.now()}\n\n")
        for old, new in renamed:
            f.write(f'[{old}] --> [{new}]\n')
    return report_path

def main():
    folder = ask_folder()
    mode, recursive = ask_options()
    files = find_pdfs(folder, recursive)
    if not files:
        print('No PDF files found.')
        return
    if mode == 'single':
        renamed = rename_interactive(files)
    else:
        renamed = rename_batch(files)
    if renamed:
        report = write_report(folder, renamed)
        root = tk.Tk(); root.withdraw()
        messagebox.showinfo('Rename complete', f'Renamed {len(renamed)} files.')
        ans = messagebox.askyesno('Review renamed files?', 'Do you want to review the renamed files?')
        root.destroy()
        if ans:
            for _, new in renamed:
                print(new)
        print(f'Report written to {report}')
    else:
        print('No files renamed.')

if __name__ == '__main__':
    main()
