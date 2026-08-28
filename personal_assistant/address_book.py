"""Address book: contacts with name, phones, birthday, email and address."""

import re
from collections import UserDict
from datetime import datetime, date, timedelta


class FieldError(ValueError):
    """Raised when a field value fails validation."""


DEFAULT_BIRTHDAY_WINDOW_DAYS = 7


class Field:
    """Base class for all record fields."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.value == other.value
        return self.value == other

    def __hash__(self):
        return hash(self.value)


class Name(Field):
    """Contact's name. Required, non-empty."""

    def __init__(self, value):
        value = (value or "").strip()
        if not value:
            raise FieldError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    """Phone number. Must consist of exactly 10 digits."""

    def __init__(self, value):
        value = (value or "").strip()
        if not re.fullmatch(r"\d{10}", value):
            raise FieldError(f"Phone '{value}' is invalid: expected 10 digits.")
        super().__init__(value)


class Email(Field):
    """Email address with a simple format check."""

    _PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

    def __init__(self, value):
        value = (value or "").strip()
        if not self._PATTERN.match(value):
            raise FieldError(f"Email '{value}' is invalid.")
        super().__init__(value)


class Address(Field):
    """Free-form home/postal address."""

    def __init__(self, value):
        value = (value or "").strip()
        if not value:
            raise FieldError("Address cannot be empty.")
        super().__init__(value)


class Birthday(Field):
    """Birthday stored as a date, parsed from DD.MM.YYYY."""

    def __init__(self, value):
        try:
            parsed = datetime.strptime(value.strip(), "%d.%m.%Y").date()
        except ValueError:
            raise FieldError("Invalid date format. Use DD.MM.YYYY")
        if parsed > date.today():
            raise FieldError("Birthday cannot be in the future.")
        super().__init__(parsed)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    """A single contact: name + phones + optional birthday/email/address."""

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None

    # ---- phones -----------------------------------------------------
    def add_phone(self, phone):
        new_phone = Phone(phone)
        if new_phone in self.phones:
            raise FieldError(f"Phone '{new_phone.value}' already exists for {self.name.value}.")
        self.phones.append(new_phone)
        return new_phone

    def remove_phone(self, phone):
        found = self.find_phone(phone)
        if not found:
            raise FieldError(f"Phone '{phone}' not found for {self.name.value}.")
        self.phones.remove(found)

    def edit_phone(self, old_phone, new_phone):
        found = self.find_phone(old_phone)
        if not found:
            raise FieldError(f"Phone '{old_phone}' not found for {self.name.value}.")
        validated_new = Phone(new_phone)
        index = self.phones.index(found)
        self.phones[index] = validated_new

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    # ---- other fields -------------------------------------------------
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_email(self, email):
        self.email = Email(email)

    def add_address(self, address):
        self.address = Address(address)

    def days_to_birthday(self):
        """Number of days from today until the next birthday, or None."""
        if not self.birthday:
            return None
        today = date.today()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones) or "-"
        birthday = str(self.birthday) if self.birthday else "-"
        email = str(self.email) if self.email else "-"
        address = str(self.address) if self.address else "-"
        return (
            f"Contact name: {self.name.value}, phones: {phones}, "
            f"birthday: {birthday}, email: {email}, address: {address}"
        )


class AddressBook(UserDict):
    """A collection of Records keyed by contact name."""

    def add_record(self, record):
        if record.name.value in self.data:
            raise FieldError(f"Contact '{record.name.value}' already exists.")
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self, days=DEFAULT_BIRTHDAY_WINDOW_DAYS):
        """Return records whose birthday falls within the next `days` days."""
        upcoming = []
        for record in self.data.values():
            d2b = record.days_to_birthday()
            if d2b is not None and 0 <= d2b <= days:
                upcoming.append(record)
        return sorted(upcoming, key=lambda r: r.days_to_birthday())

    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())
