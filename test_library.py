import unittest
from datetime import date, timedelta
from library import Library


class TestLibrary(unittest.TestCase):

    def setUp(self) -> None:
        # Reset the singleton by recreating Library internals (simple hack for tests)
        lib = Library()
        lib._users.clear()
        lib._books.clear()
        lib._records.clear()
        lib._next_record_id = 1
        self.lib = lib

        # Add one user and one book for tests
        self.user = self.lib.add_user(1, "Alice", "alice@example.com")
        self.book = self.lib.add_book(
            100, "1984", "George Orwell", "Fiction", total_copies=2
        )

    def test_add_user(self):
        self.assertEqual(self.user.name, "Alice")
        self.assertEqual(self.user.email, "alice@example.com")

    def test_add_book(self):
        self.assertEqual(self.book.title, "1984")
        self.assertEqual(self.book.available_copies, 2)

    def test_borrow_book_reduces_available_copies(self):
        record = self.lib.borrow_book(self.user.user_id, self.book.book_id)
        self.assertEqual(self.book.available_copies, 1)
        self.assertEqual(record.user_id, self.user.user_id)
        self.assertEqual(record.book_id, self.book.book_id)

    def test_borrow_book_no_copies_raises(self):
        # Borrow twice (2 copies available)
        self.lib.borrow_book(self.user.user_id, self.book.book_id)
        self.lib.borrow_book(self.user.user_id, self.book.book_id)
        # Third borrow should fail
        with self.assertRaises(ValueError):
            self.lib.borrow_book(self.user.user_id, self.book.book_id)

    def test_return_book_increases_available_copies(self):
        record = self.lib.borrow_book(self.user.user_id, self.book.book_id)
        self.lib.return_book(record.record_id)
        self.assertEqual(self.book.available_copies, 2)
        self.assertIsNotNone(record.return_date)

    def test_overdue_detection(self):
        record = self.lib.borrow_book(self.user.user_id, self.book.book_id)
        # simulate future date
        future = date.today() + timedelta(days=self.lib.LOAN_DAYS + 1)
        overdue = self.lib.list_overdue_records(today=future)
        self.assertIn(record, overdue)


if __name__ == "__main__":
    unittest.main()
