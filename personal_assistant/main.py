"""Personal Assistant - CLI entry point.

Run with:
    python main.py

Type `help` inside the program to see the list of available commands.
"""

from address_book import AddressBook, Record, FieldError, DEFAULT_BIRTHDAY_WINDOW_DAYS
from note_book import Note, NoteBook, NoteError
from storage import save_data, load_data

CONTACTS_FILE = "address_book.pkl"
NOTES_FILE = "note_book.pkl"


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
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        return "Usage: phone <name>"
    (name,) = args
    record = book.find(name)
    if record is None:
        return f"Contact '{name}' not found."
    phones = ", ".join(p.value for p in record.phones) or "no phones"
    return f"{name}: {phones}"


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


# ---------------------------------------------------------------------------
# Note commands
# ---------------------------------------------------------------------------
@input_error
def add_note(args, notes: NoteBook):
    if not args:
        return "Usage: add-note <title> [#tag ...]"
    tags = [a for a in args if a.startswith("#")]
    title_parts = [a for a in args if not a.startswith("#")]
    title = " ".join(title_parts) if title_parts else args[0]
    note = notes.add_note(title, tags=tags)
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
    found = notes.find_by_title(keyword) or notes.find_by_text(keyword)
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
# Help / menu
# ---------------------------------------------------------------------------
HELP_TEXT = """\
Available commands:
  Contacts:
    add-contact <name> <phone>              - add a contact or a phone to an existing one
    change-phone <name> <old> <new>         - change a contact's phone number
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

  Notes:
    add-note <title> [#tag ...]             - add a note (optionally with tags)
    edit-note <id> <new text...>            - edit a note's text
    delete-note <id>                        - delete a note
    find-note <keyword>                     - find notes by title or text
    search-notes-tag <tag>                  - find notes by tag
    all-notes                               - show all notes

  General:
    help                                    - show this help message
    close / exit                            - save data and exit the assistant
"""


def restore_note_id_counter(notes: NoteBook):
    """Make sure new notes get ids after the highest loaded id."""
    if notes.data:
        Note._id_counter = iter(range(max(notes.data.keys()) + 1, 10**9))


def main():
    book = load_data(CONTACTS_FILE, AddressBook)
    notes = load_data(NOTES_FILE, NoteBook)
    restore_note_id_counter(notes)

    print("Welcome to the Personal Assistant!")
    print("Type 'help' to see the list of commands.")

    while True:
        user_input = input("\n>>> ")
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            save_data(book, CONTACTS_FILE)
            save_data(notes, NOTES_FILE)
            print("Data saved. Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "help":
            print(HELP_TEXT)
        elif command == "add-contact":
            print(add_contact(args, book))
        elif command == "change-phone":
            print(change_phone(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all-contacts":
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "edit-birthday":
            print(edit_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "add-email":
            print(add_email(args, book))
        elif command == "edit-email":
            print(edit_email(args, book))
        elif command == "add-address":
            print(add_address(args, book))
        elif command == "delete-contact":
            print(delete_contact(args, book))
        elif command == "add-note":
            print(add_note(args, notes))
        elif command == "edit-note":
            print(edit_note(args, notes))
        elif command == "delete-note":
            print(delete_note(args, notes))
        elif command == "find-note":
            print(find_notes(args, notes))
        elif command == "search-notes-tag":
            print(search_notes_by_tag(args, notes))
        elif command == "all-notes":
            print(show_all_notes(notes))
        elif command == "":
            continue
        else:
            print("Unknown command. Type 'help' to see the list of commands.")


if __name__ == "__main__":
    main()
