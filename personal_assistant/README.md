# Personal Assistant

A simple command-line personal assistant written in pure Python (standard
library only). It keeps an address book of contacts and a note book with
tagged notes, and saves both between sessions.

## Features

- **Contacts**: name, one or more phone numbers, birthday, email, address.
- **Birthdays**: list contacts whose birthday falls within the next N days.
- **Notes**: title, text and tags; search notes by title, text or tag.
- **Persistence**: data is automatically saved (via `pickle`) to
  `~/.personal_assistant/` and reloaded on the next run, so nothing is lost
  when you close the program.

## Project structure

| File               | Purpose                                              |
|--------------------|-------------------------------------------------------|
| `main.py`          | CLI entry point: command loop and menu                |
| `address_book.py`  | `Record` / `AddressBook` classes for contacts          |
| `note_book.py`     | `Note` / `NoteBook` classes for notes and tags          |
| `storage.py`       | Save/load helpers (pickle) used for persistence        |
| `requirements.txt` | External dependencies (none - standard library only)   |

## Requirements

- Python 3.10+
- No external dependencies.

## How to run

```bash
python main.py
```

Once running, type `help` to see the full list of available commands, e.g.:

```
>>> add-contact John 1234567890
>>> add-birthday John 15.08.1990
>>> birthdays 30
>>> add-note "Buy milk" #shopping
>>> all-notes
>>> exit
```

## Authors

- **olev0885-design** — developer: `main.py` (CLI), `address_book.py` (contacts), `note_book.py` (notes), `storage.py` (persistence)
- **NazarHook** — code review and feedback
