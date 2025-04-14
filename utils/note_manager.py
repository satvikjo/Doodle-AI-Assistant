import os
from datetime import datetime
import pyperclip

NOTES_FOLDER = "notes"

if not os.path.exists(NOTES_FOLDER):
    os.makedirs(NOTES_FOLDER)

def save_note(name, text):
    # Sanitize filename: remove invalid characters and add .txt
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
    filename = f"{NOTES_FOLDER}/{safe_name}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)
    return filename

def get_clipboard_text():
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Could not read clipboard: {e}"
    
def delete_note_by_name(note_name):
    safe_name = "".join(c for c in note_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
    filename = f"{NOTES_FOLDER}/{safe_name}.txt"

    if os.path.exists(filename):
        os.remove(filename)
        return f"The note named '{note_name}' has been deleted."
    else:
        return f"I couldn't find a note named '{note_name}'."

def rename_note(old_name, new_name):
    old_safe = "".join(c for c in old_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
    new_safe = "".join(c for c in new_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")

    old_path = f"{NOTES_FOLDER}/{old_safe}.txt"
    new_path = f"{NOTES_FOLDER}/{new_safe}.txt"

    if not os.path.exists(old_path):
        return f"I couldn't find a note named '{old_name}'."
    
    if os.path.exists(new_path):
        return f"A note named '{new_name}' already exists."

    os.rename(old_path, new_path)
    return f"Note '{old_name}' has been renamed to '{new_name}'."

def delete_all_notes():
    deleted = 0
    for file in os.listdir(NOTES_FOLDER):
        if file.endswith(".txt"):
            try:
                os.remove(os.path.join(NOTES_FOLDER, file))
                deleted += 1
            except:
                continue
    return f"Deleted {deleted} note{'s' if deleted != 1 else ''}."


def list_all_notes():
    notes = [
        f.replace(".txt", "")
        for f in os.listdir(NOTES_FOLDER)
        if f.endswith(".txt")
    ]
    return notes if notes else []

def read_note_by_name(note_name):
    safe_name = "".join(c for c in note_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
    filename = f"{NOTES_FOLDER}/{safe_name}.txt"

    if not os.path.exists(filename):
        return None

    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()
    return content






