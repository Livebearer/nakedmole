import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from datetime import datetime
from PyPDF2 import PdfReader

__version__ = '0.02.0-dev'

def ask_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select folder with PDF files")
    root.destroy()
    return folder or os.getcwd()

def find_pdfs(folder):
    return sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(".pdf")
    ])

def _extract_meta_field(text, key):
    match = re.search(rf'/{re.escape(key)}\s*\((.*?)\)', text)
    return match.group(1).strip() if match else ''

def extract_pdf_metadata(path):
    try:
        reader = PdfReader(path)
        info = reader.metadata or {}
        title = info.get("/Title") or ""
        author = info.get("/Author") or ""
        creation = info.get("/CreationDate") or ""
    except Exception:
        with open(path, "rb") as f:
            data = f.read(8192)
        text = data.decode("latin1", errors="ignore")
        title = _extract_meta_field(text, "Title")
        author = _extract_meta_field(text, "Author")
        creation = _extract_meta_field(text, "CreationDate")
    year_match = re.search(r"(\d{4})", str(creation))
    year = year_match.group(1) if year_match else ""
    return {"title": title, "author": author, "year": year}

def shorten_title(title, limit=60):
    t = re.sub(r'\s+', ' ', title).strip()
    return t[:limit] if len(t) > limit else t

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

def confirm_rename_gui(old_name, suggested_name):
    result = {'action': 'none', 'newname': None}

    def on_action(action_type):
        result['action'] = action_type
        result['newname'] = entry.get()
        root.quit()

    root = tk.Tk()
    root.title("Confirm Rename")

    tk.Label(root, text="Original filename:").pack(anchor='w')
    tk.Label(root, text=old_name, fg='blue').pack(anchor='w')

    tk.Label(root, text="Proposed new name:").pack(anchor='w')
    entry = tk.Entry(root, width=80)
    entry.insert(0, suggested_name)
    entry.pack(padx=10, pady=5)

    frame = tk.Frame(root)
    tk.Button(frame, text="OK", command=lambda: on_action("accept")).pack(side='left', padx=5)
    tk.Button(frame, text="Editar", command=lambda: on_action("edit")).pack(side='left', padx=5)
    tk.Button(frame, text="Pular", command=lambda: on_action("skip")).pack(side='left', padx=5)
    frame.pack(pady=10)

    root.mainloop()
    root.destroy()
    return result['action'], result['newname']

def rename_interactive(files):
    renamed = []
    for fpath in files:
        meta = extract_pdf_metadata(fpath)
        new_name = build_new_name(meta, os.path.splitext(fpath)[1])
        new_path = ensure_unique_filename(os.path.join(os.path.dirname(fpath), new_name))
        action, edited_name = confirm_rename_gui(os.path.basename(fpath), os.path.basename(new_path))
        if action == "skip":
            continue
        elif action == "edit":
            new_path = ensure_unique_filename(os.path.join(os.path.dirname(fpath), sanitize(edited_name)))
        os.rename(fpath, new_path)
        renamed.append((fpath, new_path))
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
    files = find_pdfs(folder)
    if not files:
        messagebox.showinfo("Nenhum PDF encontrado", "Não há arquivos PDF na pasta selecionada.")
        return
    renamed = rename_interactive(files)
    if renamed:
        report = write_report(folder, renamed)
        messagebox.showinfo('Concluído', f'{len(renamed)} arquivos renomeados.\nRelatório salvo em:\n{report}')
    else:
        messagebox.showinfo('Nada renomeado', 'Nenhum arquivo foi renomeado.')

if __name__ == '__main__':
    main()
