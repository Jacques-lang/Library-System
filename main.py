from library import Library


def print_menu() -> None:
    print("\n=== Library Menu ===")
    print("1. Add user")
    print("2. Add book")
    print("3. List books")
    print("4. Search books")
    print("5. Borrow book")
    print("6. Return book")
    print("7. List user borrowed books")
    print("8. List overdue records")
    print("0. Exit")


def main() -> None:
    lib = Library()

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                user_id = int(input("User ID: "))
                name = input("Name: ")
                email = input("Email: ")
                user = lib.add_user(user_id, name, email)
                print("Added user:", user)

            elif choice == "2":
                book_id = int(input("Book ID: "))
                title = input("Title: ")
                author = input("Author: ")
                category = input("Category: ")
                total_copies = int(input("Total copies: "))
                book = lib.add_book(book_id, title, author, category, total_copies)
                print("Added book:", book)

            elif choice == "3":
                for b in lib.list_all_books():
                    print(b)

            elif choice == "4":
                title = input("Title (or blank): ").strip() or None
                author = input("Author (or blank): ").strip() or None
                category = input("Category (or blank): ").strip() or None
                results = lib.search_books(title=title, author=author, category=category)
                if not results:
                    print("No matching books.")
                else:
                    for b in results:
                        print(b)

            elif choice == "5":
                user_id = int(input("User ID: "))
                book_id = int(input("Book ID: "))
                record = lib.borrow_book(user_id, book_id)
                print("Borrowed:", record)

            elif choice == "6":
                record_id = int(input("Borrow record ID: "))
                record = lib.return_book(record_id)
                print("Returned:", record)

            elif choice == "7":
                user_id = int(input("User ID: "))
                records = lib.list_user_borrowed_books(user_id)
                if not records:
                    print("No active borrowed books.")
                else:
                    for r in records:
                        print(r)

            elif choice == "8":
                overdue = lib.list_overdue_records()
                if not overdue:
                    print("No overdue records.")
                else:
                    for r in overdue:
                        print(r)

            elif choice == "0":
                print("Goodbye.")
                break

            else:
                print("Invalid choice.")

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
