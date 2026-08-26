"""Note book: text notes with titles and tags."""

from collections import UserDict
from datetime import datetime
from itertools import count


class NoteError(ValueError):
    """Raised when a note operation fails validation."""


class Note:
    """A single note: id, title, text and a list of tags."""

    _id_counter = count(1)

    def __init__(self, title, text="", tags=None):
        title = (title or "").strip()
        if not title:
            raise NoteError("Note title cannot be empty.")
        self.id = next(Note._id_counter)
        self.title = title
        self.text = text.strip() if text else ""
        self.tags = self._normalize_tags(tags)
        self.created_at = datetime.now()

    @staticmethod
    def _normalize_tags(tags):
        if not tags:
            return []
        normalized = []
        for tag in tags:
            tag = tag.strip().lower().lstrip("#")
            if tag and tag not in normalized:
                normalized.append(tag)
        return normalized

    def add_tag(self, tag):
        tag = tag.strip().lower().lstrip("#")
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        tag = tag.strip().lower().lstrip("#")
        if tag in self.tags:
            self.tags.remove(tag)

    def edit_text(self, new_text):
        self.text = new_text.strip() if new_text else ""

    def edit_title(self, new_title):
        new_title = (new_title or "").strip()
        if not new_title:
            raise NoteError("Note title cannot be empty.")
        self.title = new_title

    def __str__(self):
        tags = ", ".join(f"#{t}" for t in self.tags) or "-"
        text = self.text or "-"
        return (
            f"[{self.id}] {self.title}\n"
            f"    text: {text}\n"
            f"    tags: {tags}\n"
            f"    created: {self.created_at.strftime('%d.%m.%Y %H:%M')}"
        )

 
class NoteBook(UserDict):
    """A collection of Notes keyed by their numeric id."""

    def add_note(self, title, text="", tags=None):
        note = Note(title, text, tags)
        self.data[note.id] = note
        return note

    def find_note(self, note_id):
        return self.data.get(note_id)

    def delete_note(self, note_id):
        if note_id in self.data:
            del self.data[note_id]
            return True
        return False

    def find_by_title(self, title):
        title = title.strip().lower()
        return [n for n in self.data.values() if title in n.title.lower()]

    def find_by_text(self, keyword):
        keyword = keyword.strip().lower()
        return [n for n in self.data.values() if keyword in n.text.lower()]

    def find_by_tag(self, tag):
        tag = tag.strip().lower().lstrip("#")
        return [n for n in self.data.values() if tag in n.tags]

    def all_notes(self):
        return sorted(self.data.values(), key=lambda n: n.id)

    def __str__(self):
        if not self.data:
            return "Note book is empty."
        return "\n".join(str(note) for note in self.all_notes())
