"""Personal Assistant - CLI entry point.

Run with:
    python main.py

Type `help` inside the program to see the list of available commands.
"""

from colorama import init as colorama_init, Fore

from address_book import AddressBook, Record, FieldError, DEFAULT_BIRTHDAY_WINDOW_DAYS
from note_book import NoteBook, NoteError
from storage import save_data, load_data

colorama_init(autoreset=True)

CONTACTS_FILE = "address_book.pkl"
NOTES_FILE = "note_book.pkl"

# Substrings that mark a result as a problem rather than a success, used by
# output() below to color CLI feedback (red for problems, green otherwise).
_PROBLEM_MARKERS = (
    "usage:", "not found", "already exists", "invalid", "cannot",
    "error", "no matching", "no birthdays", "no notes", "has no",
    "unknown command",
)

HELP_TEXT = """\
Available commands:
  Contacts:
    add-contact <name> <phone>              - add a contact or a phone to an existing one
    change-phone <name> <old> <new>         - change a contact's phone number
    remove-phone <name> <phone>             - remove a phone number from a contact
    phone <name>                            - show a contact's phone numbers
    add-birthday <name> <DD.MM.YYYY>        - add a birthday to a contact
    edit-birthday <name> <DD.MM.YYYY>       - change a contact's birthday
    show-birthday <name>                    - show a contact's birthday
    birthdays [days]                        - show birthdays in the next N days (default 7)
    add-email <name> <email>                - add an email to a contact
    edit-email <name> <new_email>           - change a contact's email
    add-address <name> <address...>         - add an address to a contact
    delete-contact <name>                   - delete a contact
    all-contacts                            - show all contacts
    search-contact <query>                  - find contacts by name, phone, email or address

  Notes:
    add-note <title> [| <text>] [#tag ...]  - add a note, optionally with text and tags
    edit-note <id> <new text...>            - edit a note's text
    edit-title <id> <new title...>          - edit a note's title
    add-tag <id> <tag>                      - add a tag to an existing note
    remove-tag <id> <tag>                   - remove a tag from an existing note
    delete-note <id>                        - delete a note
    find-note <keyword>                     - find notes by title or text
    search-notes-tag <tag>                  - find notes by tag
    all-notes                               - show all notes

  General:
    help                                    - show this help message
    close / exit                            - save data and exit the assistant
"""


def input_error(func):
    """Decorator that turns expected errors into friendly messages."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FieldError, NoteError) as e:
            return str(e)
        except (KeyError, ValueError, IndexError) as e:
            return f"Error: {e}" if str(e) else "Invalid input for that command."

    return wrapper


def output(message):
    """Print a command result, colored green for success / red for problems.

    Multi-line output (listings, help text) is printed as-is - the
    red/green distinction only makes sense for a single status line.
    """
    if message is None:
        return
    if "\n" in message:
        print(message)
        return
    color = Fore.RED if any(marker in message.lower() for marker in _PROBLEM_MARKERS) else Fore.GREEN
    print(color + message)


def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    cmd, *args = parts
    return cmd.strip().lower(), args


# ---------------------------------------------------------------------------
# Contact commands
# ---------------------------------------------------------------------------
@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Usage: add-contact <name> <phone>"
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        new_record = Record(name)
        new_record.add_phone(phone)  # validate before inserting into the book
        book.add_record(new_record)
        return "Contact added."
    record.add_phone(phone)
    return "Contact updated."


@input_error
def change_phone(args, book: AddressBook):
    if len(args) != 3:
        return "Usage: change-phone <name> <old_phone> <new_phone>"
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error
def remove_phone(args, book: AddressBook):
    if len(args) != 2:
        return "Usage: remove-phone <name> <phone>"
    name, phone = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."
    record.remove_phone(phone)
    return "Phone number removed."


@input_error
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        return "Usage: phone <name>"
    (name,) = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."
    phones = ", ".join(p.value for p in record.phones) or "no phones"
    return f"{name}: {phones}"


@input_error
def delete_contact(args, book: AddressBook):
    if len(args) != 1:
        return "Usage: delete-contact <name>"
    (name,) = args
    if book.delete(name):
        return "Contact deleted."
    return f"Contact '{name}' not found."


def show_all_contacts(book: AddressBook):
    return str(book)


@input_error
def search_contacts(args, book: AddressBook):
    if not args:
        return "Usage: search-contact <query>"
    found = book.search(" ".join(args))
    if not found:
        return "No matching contacts found."
    return "\n".join(str(r) for r in found)


# ---- Birthdays & other -------------------------------------------------
@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        return "Usage: add-birthday <name> <DD.MM.YYYY>"
    name, birthday = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def edit_birthday(args, book: AddressBook):
    if len(args) != 2:
        return "Usage: edit-birthday <name> <DD.MM.YYYY>"
    name, birthday = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."
    if not record.birthday:
        return f"{name} has no birthday yet. Use add-birthday to set one."
    record.add_birthday(birthday)
    return "Birthday updated."


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        return "Usage: show-birthday <name>"
    (name,) = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."
    if not record.birthday:
        return f"{name} has no birthday saved."
    return f"{name}: {record.birthday}"


@input_error
def birthdays(args, book: AddressBook):
    days = int(args[0]) if args else DEFAULT_BIRTHDAY_WINDOW_DAYS
    upcoming = book.get_upcoming_birthdays(days)
    if not upcoming:
        return f"No birthdays in the next {days} days."
    lines = [f"{r.name.value}: {r.birthday} (in {r.days_to_birthday()} days)" for r in upcoming]
    return "\n".join(lines)


@input_error
def add_email(args, book: AddressBook):
    if len(args) != 2:
        return "Usage: add-email <name> <email>"
    name, email = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."
    record.add_email(email)
    return "Email added."


@input_error
def edit_email(args, book: AddressBook):
    if len(args) != 2:
        return "Usage: edit-email <name> <new_email>"
    name, new_email = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."
    if not record.email:
        return f"{name} has no email yet. Use add-email to set one."
    record.add_email(new_email)
    return "Email updated."


@input_error
def add_address(args, book: AddressBook):
    if len(args) < 2:
        return "Usage: add-address <name> <address...>"
    name, *address_parts = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."
    record.add_address(" ".join(address_parts))
    return "Address added."


# ---------------------------------------------------------------------------
# Note commands
# ---------------------------------------------------------------------------
@input_error
def add_note(args, notes: NoteBook):
    if not args:
        return "Usage: add-note <title> [| <text>] [#tag ...]"
    tags = [a for a in args if a.startswith("#")]
    rest = [a for a in args if not a.startswith("#")]
    text = ""
    if "|" in rest:
        i = rest.index("|")
        title_parts, text_parts = rest[:i], rest[i + 1:]
        text = " ".join(text_parts)
    else:
        title_parts = rest
    title = " ".join(title_parts) if title_parts else args[0]
    note = notes.add_note(title, text=text, tags=tags)
    return f"Note added with id {note.id}."


@input_error
def edit_note(args, notes: NoteBook):
    if len(args) < 2:
        return "Usage: edit-note <id> <new text...>"
    note_id, *text_parts = args
    note = notes.find_note(int(note_id))
    if note is None:
        return f"Note {note_id} not found."
    note.edit_text(" ".join(text_parts))
    return "Note updated."


@input_error
def edit_title(args, notes: NoteBook):
    if len(args) < 2:
        return "Usage: edit-title <id> <new title...>"
    note_id, *title_parts = args
    note = notes.find_note(int(note_id))
    if note is None:
        return f"Note {note_id} not found."
    note.edit_title(" ".join(title_parts))
    return "Title updated."


@input_error
def add_tag(args, notes: NoteBook):
    if len(args) != 2:
        return "Usage: add-tag <id> <tag>"
    note_id, tag = args
    note = notes.find_note(int(note_id))
    if note is None:
        return f"Note {note_id} not found."
    note.add_tag(tag)
    return "Tag added."


@input_error
def remove_tag(args, notes: NoteBook):
    if len(args) != 2:
        return "Usage: remove-tag <id> <tag>"
    note_id, tag = args
    note = notes.find_note(int(note_id))
    if note is None:
        return f"Note {note_id} not found."
    note.remove_tag(tag)
    return "Tag removed."


@input_error
def delete_note(args, notes: NoteBook):
    if len(args) != 1:
        return "Usage: delete-note <id>"
    (note_id,) = args
    if notes.delete_note(int(note_id)):
        return "Note deleted."
    return f"Note {note_id} not found."


@input_error
def find_notes(args, notes: NoteBook):
    if not args:
        return "Usage: find-note <keyword>"
    keyword = " ".join(args)
    by_title = notes.find_by_title(keyword)
    by_text = notes.find_by_text(keyword)
    seen_ids = {n.id for n in by_title}
    found = by_title + [n for n in by_text if n.id not in seen_ids]
    if not found:
        return "No matching notes found."
    return "\n".join(str(n) for n in found)


@input_error
def search_notes_by_tag(args, notes: NoteBook):
    if len(args) != 1:
        return "Usage: search-notes-tag <tag>"
    (tag,) = args
    found = notes.find_by_tag(tag)
    if not found:
        return f"No notes with tag '#{tag.lstrip('#')}'."
    return "\n".join(str(n) for n in found)


def show_all_notes(notes: NoteBook):
    return str(notes)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    book = load_data(CONTACTS_FILE, AddressBook)
    notes = load_data(NOTES_FILE, NoteBook)

    output("Welcome to the Personal Assistant!")
    print("Type 'help' to see the list of commands.")

    while True:
        user_input = input("\n>>> ")
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            save_data(book, CONTACTS_FILE)
            save_data(notes, NOTES_FILE)
            output("Data saved. Good bye!")
            break
        elif command == "hello":
            output("How can I help you?")
        elif command == "help":
            output(HELP_TEXT)
        elif command == "add-contact":
            output(add_contact(args, book))
        elif command == "change-phone":
            output(change_phone(args, book))
        elif command == "remove-phone":
            output(remove_phone(args, book))
        elif command == "phone":
            output(show_phone(args, book))
        elif command == "all-contacts":
            output(show_all_contacts(book))
        elif command == "search-contact":
            output(search_contacts(args, book))
        elif command == "add-birthday":
            output(add_birthday(args, book))
        elif command == "edit-birthday":
            output(edit_birthday(args, book))
        elif command == "show-birthday":
            output(show_birthday(args, book))
        elif command == "birthdays":
            output(birthdays(args, book))
        elif command == "add-email":
            output(add_email(args, book))
        elif command == "edit-email":
            output(edit_email(args, book))
        elif command == "add-address":
            output(add_address(args, book))
        elif command == "delete-contact":
            output(delete_contact(args, book))
        elif command == "add-note":
            output(add_note(args, notes))
        elif command == "edit-note":
            output(edit_note(args, notes))
        elif command == "edit-title":
            output(edit_title(args, notes))
        elif command == "add-tag":
            output(add_tag(args, notes))
        elif command == "remove-tag":
            output(remove_tag(args, notes))
        elif command == "delete-note":
            output(delete_note(args, notes))
        elif command == "find-note":
            output(find_notes(args, notes))
        elif command == "search-notes-tag":
            output(search_notes_by_tag(args, notes))
        elif command == "all-notes":
            output(show_all_notes(notes))
        elif command == "":
            continue
        else:
            output("Unknown command. Type 'help' to see the list of commands.")


if __name__ == "__main__":
    main()
