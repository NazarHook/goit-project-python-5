"""Persistence layer for the Personal Assistant.

Saves and loads Python objects (AddressBook, NoteBook, ...) as pickle
files inside a hidden folder in the user's home directory, e.g.:
    Windows: C:/Users/<Name>/.personal_assistant
    Linux/macOS: /home/<name>/.personal_assistant
"""

import pickle
from pathlib import Path

# Automatically creates a folder in the user's home directory
STORAGE_DIR = Path.home() / ".personal_assistant"
STORAGE_DIR.mkdir(exist_ok=True)


def save_data(data, filename):
    """Serialize `data` and save it to STORAGE_DIR/filename."""
    filepath = STORAGE_DIR / filename
    with open(filepath, "wb") as f:
        pickle.dump(data, f)


def load_data(filename, default_factory):
    """Load and return data from STORAGE_DIR/filename.

    If the file does not exist (first run) or cannot be read,
    return `default_factory()` instead (e.g. AddressBook, NoteBook).
    """
    filepath = STORAGE_DIR / filename
    try:
        with open(filepath, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        return default_factory()
