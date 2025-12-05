from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Dict, Optional


# -----------------------------
# Domain Model
# -----------------------------

@dataclass
class User:
    user_id: int
    name: str
    email: str

    def __str__(self) -> str:
        return f"{self.user_id} - {self.name} ({self.email})"


@dataclass
class Book:
    book_id: int
    title: str
    author: str
    category: str
    total_copies: int
    available_copies: int

    def is_available(self) -> bool:
        return self.available_copies > 0

    def borrow_copy(self) -> None:
        if self.available_copies <= 0:
            raise ValueError(f"No available copies for '{self.title}'.")
        self.available_copies -= 1

    def return_copy(self) -> None:
        if self.available_copies >= self.total_copies:
            # Defensive check – shouldn't go over total copies
            raise ValueError(f"All copies of '{self.title}' are already in library.")
        self.available_copies += 1

    def __str__(self) -> str:
        return f"{self.book_id} - {self.title} by {self.author} [{self.category}] " \
               f"(Available: {self.available_copies}/{self.total_copies})"


@dataclass
class BorrowRecord:
    record_id: int
    user_id: int
    book_id: int
    borrow_date: date
    due_date: date
    return_date: Optional[date] = None

    def mark_returned(self, return_date: Optional[date] = None) -> None:
        self.return_date = return_date or date.today()

    def is_overdue(self, today: Optional[date] = None) -> bool:
        if self.return_date is not None:
            return False
        today = today or date.today()
        return today > self.due_date

    def __str__(self) -> str:
        status = "Returned" if self.return_date else "Borrowed"
        return f"Record {self.record_id}: User {self.user_id}, Book {self.book_id}, " \
               f"Borrowed {self.borrow_date}, Due {self.due_date}, Status: {status}"


# -----------------------------
# Singleton Pattern: Library
# -----------------------------

class _LibrarySingleton(type):
    """
    Metaclass implementing the Singleton pattern.
    Ensures only one Library instance exists.
    """
    _instance: Optional["Library"] = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(_LibrarySingleton, cls).__call__(*args, **kwargs)
        return cls._instance


class Library(metaclass=_LibrarySingleton):
    """
    Library class acts as the central manager for users, books, and borrow records.
    This uses the Singleton pattern so there is only one library instance in the app.
    """

    LOAN_DAYS = 14

    def __init__(self) -> None:
        self._users: Dict[int, User] = {}
        self._books: Dict[int, Book] = {}
        self._records: Dict[int, BorrowRecord] = {}
        self._next_record_id: int = 1

    # -------- User Management --------

    def add_user(self, user_id: int, name: str, email: str) -> User:
        if user_id in self._users:
            raise ValueError(f"User with id {user_id} already exists.")
        user = User(user_id=user_id, name=name, email=email)
        self._users[user_id] = user
        return user

    def get_user(self, user_id: int) -> User:
        if user_id not in self._users:
            raise ValueError(f"User with id {user_id} not found.")
        return self._users[user_id]

    # -------- Book Management (Admin) --------

    def add_book(
            self,
            book_id: int,
            title: str,
            author: str,
            category: str,
            total_copies: int,
    ) -> Book:
        if book_id in self._books:
            raise ValueError(f"Book with id {book_id} already exists.")
        if total_copies <= 0:
            raise ValueError("total_copies must be positive.")
        book = Book(
            book_id=book_id,
            title=title,
            author=author,
            category=category,
            total_copies=total_copies,
            available_copies=total_copies,
        )
        self._books[book_id] = book
        return book

    def update_book(
            self,
            book_id: int,
            title: Optional[str] = None,
            author: Optional[str] = None,
            category: Optional[str] = None,
            total_copies: Optional[int] = None,
    ) -> Book:
        if book_id not in self._books:
            raise ValueError(f"Book with id {book_id} not found.")

        book = self._books[book_id]

        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if category is not None:
            book.category = category
        if total_copies is not None:
            if total_copies < (book.total_copies - book.available_copies):
                # Can't reduce below already borrowed copies
                raise ValueError("total_copies less than borrowed count.")
            diff = total_copies - book.total_copies
            book.total_copies = total_copies
            book.available_copies += diff
            if book.available_copies < 0:
                book.available_copies = 0

        return book

    def delete_book(self, book_id: int) -> None:
        if book_id not in self._books:
            raise ValueError(f"Book with id {book_id} not found.")
        # Optionally: check if any active borrow records exist first
        del self._books[book_id]

    # -------- Search & Listing --------

    def search_books(
            self,
            title: Optional[str] = None,
            author: Optional[str] = None,
            category: Optional[str] = None,
    ) -> List[Book]:
        results: List[Book] = []
        for book in self._books.values():
            if title and title.lower() not in book.title.lower():
                continue
            if author and author.lower() not in book.author.lower():
                continue
            if category and category.lower() not in book.category.lower():
                continue
            results.append(book)
        return results

    def list_all_books(self) -> List[Book]:
        return list(self._books.values())

    def list_available_books(self) -> List[Book]:
        return [b for b in self._books.values() if b.is_available()]

    # -------- Borrow / Return --------

    def borrow_book(self, user_id: int, book_id: int) -> BorrowRecord:
        user = self.get_user(user_id)
        if book_id not in self._books:
            raise ValueError(f"Book with id {book_id} not found.")
        book = self._books[book_id]

        if not book.is_available():
            raise ValueError(f"Book '{book.title}' is not available.")

        book.borrow_copy()
        today = date.today()
        due_date = today + timedelta(days=self.LOAN_DAYS)

        record = BorrowRecord(
            record_id=self._next_record_id,
            user_id=user.user_id,
            book_id=book.book_id,
            borrow_date=today,
            due_date=due_date,
        )
        self._records[self._next_record_id] = record
        self._next_record_id += 1
        return record

    def return_book(self, record_id: int) -> BorrowRecord:
        if record_id not in self._records:
            raise ValueError(f"Borrow record with id {record_id} not found.")
        record = self._records[record_id]
        if record.return_date is not None:
            raise ValueError("Book already returned for this record.")

        if record.book_id not in self._books:
            raise ValueError("Book no longer exists in catalog.")
        book = self._books[record.book_id]

        book.return_copy()
        record.mark_returned()
        return record

    def list_user_borrowed_books(self, user_id: int) -> List[BorrowRecord]:
        self.get_user(user_id)  # will raise if not found
        return [
            r for r in self._records.values()
            if r.user_id == user_id and r.return_date is None
        ]

    def list_overdue_records(self, today: Optional[date] = None) -> List[BorrowRecord]:
        return [
            r for r in self._records.values()
            if r.is_overdue(today=today)
        ]
