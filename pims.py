import json #For handling JSON data storage and retrieval
import os #For file handling and checking file existence
import re #For validating phone numbers and email addresses using regular expressions

DATA_FILE = "data.json"

PHONE_PATTERN = re.compile(r"^90\d{10}$")
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9_]+@(gmail|outlook|yahoo)\.com$")

# Functions
# Load records from the JSON file, returning an empty list if the file doesn't exist or is invalid
def load_records(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_records(file_path, records):
    with open(file_path, "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2)


def validate_phone(phone):
    return bool(PHONE_PATTERN.match(phone))


def validate_email(email):
    return bool(EMAIL_PATTERN.match(email))


def find_record_index(records, record_id):
    for index, record in enumerate(records):
        if record.get("id") == record_id:
            return index
    return None


def prompt_non_empty(prompt_text):
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Input cannot be empty.")


def add_record(records, file_path):
    print("\n--- Add New Record ---")
    record_id = prompt_non_empty("Enter ID: ")
    if find_record_index(records, record_id) is not None:
        print(">> ERROR: ID already exists. Record rejected.")
        return

    first_name = prompt_non_empty("Enter First Name: ")
    last_name = prompt_non_empty("Enter Last Name: ")
    phone = prompt_non_empty("Enter Phone Number (starts with 90, 12 digits): ")
    email = prompt_non_empty("Enter Email: ")

    if not validate_email(email):
        print(">> ERROR: Invalid email structure. Record rejected.")
        return
    
    if not validate_phone(phone):
        print(">> ERROR: Invalid phone number. Record rejected.")
        return

    records.append(
        {
            "id": record_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
        }
    )
    save_records(file_path, records)
    print(">> Record added successfully!")


def edit_record(records, file_path):
    print("\n--- Edit Record ---")
    record_id = prompt_non_empty("Enter ID to edit: ")
    index = find_record_index(records, record_id)
    if index is None:
        print(">> ERROR: Record ID not found.")
        return

    record = records[index]
    print("Leave blank to keep the current value.")

    first_name = input(f"First Name [{record['first_name']}]: ").strip()
    last_name = input(f"Last Name [{record['last_name']}]: ").strip()
    phone = input(f"Phone Number [{record['phone']}]: ").strip()
    email = input(f"Email [{record['email']}]: ").strip()

    updated = {
        "id": record["id"],
        "first_name": first_name or record["first_name"],
        "last_name": last_name or record["last_name"],
        "phone": phone or record["phone"],
        "email": email or record["email"],
    }

    if not validate_phone(updated["phone"]):
        print(">> ERROR: Invalid phone number. Edit canceled.")
        return
    
    if not validate_email(updated["email"]):
        print(">> ERROR: Invalid email structure. Edit canceled.")
        return   
    
    records[index] = updated
    save_records(file_path, records)
    print(">> Record updated successfully!")


def remove_record(records, file_path):
    print("\n--- Remove Record ---")
    record_id = prompt_non_empty("Enter ID to remove: ")
    index = find_record_index(records, record_id)
    if index is None:
        print(">> ERROR: Record ID not found.")
        return

    records.pop(index)
    save_records(file_path, records)
    print(">> Record removed successfully!")


def search_records(records):
    print("\n--- Multi-Field Search Interface ---")
    print("Enter values to search, or type 'empty' to ignore that field.")

    first_name = input("Search First Name: ").strip()
    last_name = input("Search Last Name: ").strip()
    phone = input("Search Phone Number: ").strip()
    email = input("Search Email: ").strip()

    criteria = {
        "first_name": None if first_name.lower() == "empty" else first_name.lower(),
        "last_name": None if last_name.lower() == "empty" else last_name.lower(),
        "phone": None if phone.lower() == "empty" else phone,
        "email": None if email.lower() == "empty" else email.lower(),
    }

    matches = []
    for record in records:
        if criteria["first_name"] and record["first_name"].lower() != criteria["first_name"]:
            continue
        if criteria["last_name"] and record["last_name"].lower() != criteria["last_name"]:
            continue
        if criteria["phone"] and record["phone"] != criteria["phone"]:
            continue
        if criteria["email"] and record["email"].lower() != criteria["email"]:
            continue
        matches.append(record)

    print("\n--- Matching Search Results ---")
    if not matches:
        print("No matching records were found.")
        return

    print(f"Found {len(matches)} record(s):")
    for record in matches:
        print(
            f"ID: {record['id']} | Name: {record['first_name']} {record['last_name']} "
            f"| Phone: {record['phone']} | Email: {record['email']}"
        )


def show_sorted_list(records):
    print("\nHow would you like to sort?")
    print("A. Sort by ID")
    print("B. Sort by Name")
    print("C. Sort by Phone Number")
    choice = input("Choose sort criteria (A/B/C): ").strip().upper()

    if choice == "A":
        sorted_records = sorted(records, key=lambda item: str(item["id"]))
        header = "--- Sorted Records (by ID) ---"
    elif choice == "B":
        sorted_records = sorted(records, key=lambda item: (item["first_name"].lower(), item["last_name"].lower()),)
        header = "--- Sorted Records (by Name) ---"
    elif choice == "C":
        sorted_records = sorted(records, key=lambda item: item["phone"])
        header = "--- Sorted Records (by Phone) ---"
    else:
        print(">> ERROR: Invalid choice.")
        return

    print(f"\n{header}")
    if not sorted_records:
        print("No records available.")
        return

    for record in sorted_records:
        print(
            f"ID: {record['id']} | Name: {record['first_name']} {record['last_name']} "
            f"| Phone: {record['phone']} | Email: {record['email']}"
        )


# Main
def main():
    records = load_records(DATA_FILE)

    while True:
        print("\n*** PERSONAL INFORMATION SYSTEM ***")
        print("1. Add Record")
        print("2. Edit Record")
        print("3. Remove Record")
        print("4. Search Records")
        print("5. Show Sorted List")
        print("6. Exit")
        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            add_record(records, DATA_FILE)
        elif choice == "2":
            edit_record(records, DATA_FILE)
        elif choice == "3":
            remove_record(records, DATA_FILE)
        elif choice == "4":
            search_records(records)
        elif choice == "5":
            show_sorted_list(records)
        elif choice == "6":
            print("Shutting down core processes... Execution terminated. Goodbye!")
            break
        else:
            print(">> ERROR: Invalid selection.")


if __name__ == "__main__":
    main()
