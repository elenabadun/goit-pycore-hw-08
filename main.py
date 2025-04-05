import pickle
from collections import UserDict
from datetime import datetime, timedelta


class BirthdayError(Exception):
    pass


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be 10 digits long")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise BirthdayError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        try:
            phone = Phone(phone_number)
            self.phones.append(phone)
            return f"Phone number {phone_number} added"
        except ValueError as e:
            return str(e)

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                return f"Phone number {phone_number} removed"
        return "Phone number not found"

    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if phone.value == old_number:
                try:
                    phone.value = Phone(new_number).value
                    return f"Phone number {old_number} changed to {new_number}"
                except ValueError as e:
                    return str(e)
        return "Phone number not found"

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return f"{phone_number}"
        return "Phone number not found"

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)
            return f"Contact {name} deleted"
        return "Contact not found"

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_date = record.birthday.value.replace(year=today.year)
                if birthday_date < today:
                    birthday_date = birthday_date.replace(year=today.year + 1)
                if today <= birthday_date and birthday_date < today + timedelta(days=7):
                    upcoming_birthdays.append(
                        {
                            "name": record.name.value,
                            "birthday": birthday_date.strftime("%d.%m.%Y"),
                        }
                    )
        return upcoming_birthdays


def parse_input(user_input):
    """
    Parses user input into a command and arguments.
    Takes user input as parametr and return a tupple with a command and arguments.
    """
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def input_error(func):
    """
    Decorator for handling errors in user input.
    It catches ValueError, KeyError, IndexError and BirthdayError and returns
    appropriate error messages instead of stopping the program.
    """

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone number please"
        except KeyError:
            return "Enter user name"
        except IndexError:
            return "Enter the argument for the command"
        except BirthdayError:
            return "Invalid date format. Use DD.MM.YYYY"

    return inner


@input_error
def add_contact(args, book: AddressBook):
    """
    Adds a new contact to the contacts dictionary.
    If we already have contact in the book, contact will be updated.
    """
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    """
    Updates an existing contact's phone number.
    If such contact does not founded, the function return an error message.
    """
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    return "Error: Contact not found."


@input_error
def delete_contact(args, book: AddressBook):
    """
    Deletes a contact from the address book.
    If the contact is not found, returns an error message.
    """
    name = args[0]
    record = book.find(name)
    if record:
        book.delete(name)
        return "Contact deleted."
    return "Error: Contact not found."


@input_error
def show_phone(args, book: AddressBook):
    """
    Shows the phone number of a contact.
    If such contact does not founded, the function return an error message.
    """
    name = args[0]
    record = book.find(name)
    if record:
        phones = ", ".join(p.value for p in record.phones)
        return f"{name}: {phones}"
    return "Error: Contact not found."


@input_error
def show_all(book: AddressBook):
    """
    Displays all saved contacts.
    If contacts do not founded, the function return relevant message.
    """
    if not book.data:
        return "Contacts not found"
    result = ""
    for name, record in book.data.items():
        phones = ", ".join(f"{phone}" for phone in record.phones)
        result += f"{name}: {phones} \n"
    return result


@input_error
def add_birthday(args, book: AddressBook):
    """
    Adds a birthday to an existing contact.
    If the contact is not found, returns an error message.
    """
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday {birthday} added for contact {name}"
    else:
        return "Contact not found"


@input_error
def show_birthday(args, book: AddressBook):
    """
    Shows the birthday of a specific contact.
    If the contact or birthday is not found, returns an error message.
    """
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"Contact {name} has birthday on {record.birthday.value.strftime('%d.%m.%Y')}"
    return "Contact not found"


@input_error
def birthdays(args, book: AddressBook):
    """
    Displays upcoming birthdays within the next 7 days.
    Returns a list of names and birthday dates.
    """
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthday next week."
    result = []
    for record in upcoming_birthdays:
        name = record["name"]
        birthday = record["birthday"]
        result.append(f"{name}: {birthday}")
    return "\n".join(result)


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    """
    The main function that runs the assistant bot.
    """
    print("Welcome to the assistant bot!")
    book = load_data()
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit", "bye"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "delete":
            print(delete_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
