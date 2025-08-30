import uuid
from datetime import date, timedelta
from typing import List

from biblioteka.storage.repository import Repository
from biblioteka.models.loan import Loan
from biblioteka.models.book import Book, BookStatus
from biblioteka.models.member import Member
from biblioteka.utils.exceptions import BookNotAvailable, MemberNotFound
from biblioteka.config import DEFAULT_LOAN_DURATION_DAYS


class LoanService:
    """
    Serwis obsługi wypożyczeń:
    tworzenie nowych wypożyczeń, zwroty,
    odnowienia oraz administracja listami wypożyczeń.
    """

    def __init__(self, repo: Repository):
        """
        Inicjalizuje serwis z repozytorium,
        w którym przechowywane są obiekty Loan, Book i Member.
        """
        self.repo = repo

    def loan_book(self, member_id: str, isbn: str) -> Loan:
        """
        Tworzy nowe wypożyczenie:
        1. Sprawdza istnienie członka.
        2. Sprawdza istnienie książki.
        3. Normalizuje jej status (jeśli to string).
        4. Sprawdza dostępność (status == AVAILABLE).
        5. Oznacza książkę jako wypożyczoną i zapisuje.
        6. Tworzy i przechowuje Loan.
        7. Przypisuje loan_id do Member.
        Podnosi:
          - MemberNotFound, jeśli nie znaleziono member_id.
          - BookNotAvailable, jeśli książka nie istnieje lub nie jest dostępna.
        """
        member = self.repo.get(Member, member_id)
        if not member:
            raise MemberNotFound(f"Member {member_id} not found")

        book = self.repo.get(Book, isbn)
        if not book:
            raise BookNotAvailable(f"Book {isbn} not found in catalog")

        if isinstance(book.status, str):
            try:
                key = book.status.split('.')[-1]
                book.status = BookStatus[key]
            except Exception:
                book.status = BookStatus.UNAVAILABLE

        if book.status is not BookStatus.AVAILABLE:
            raise BookNotAvailable(f"Book {isbn} is not available")

        book.mark_loaned()
        self.repo.update(book)

        loan = Loan(
            loan_id=str(uuid.uuid4()),
            member_id=member_id,
            isbn=isbn,
            loan_date=date.today(),
            due_date=date.today() + timedelta(days=DEFAULT_LOAN_DURATION_DAYS)
        )
        self.repo.add(loan)

        member.add_loan(loan.loan_id)
        self.repo.update(member)

        return loan

    def return_book(self, loan_id: str) -> None:
        """
        Przetwarza zwrot wypożyczenia:
        - Oznacza Loan jako zwrócony.
        - Przywraca status książki na AVAILABLE.
        - Usuwa loan_id z listy członka.
        Podnosi KeyError, jeśli wypożyczenie nie istnieje.
        """
        loan = self.repo.get(Loan, loan_id)
        if not loan:
            raise KeyError(f"Loan {loan_id} not found")

        loan.mark_returned(date.today())
        self.repo.update(loan)

        book = self.repo.get(Book, loan.isbn)
        book.mark_returned()
        self.repo.update(book)

        member = self.repo.get(Member, loan.member_id)
        member.remove_loan(loan_id)
        self.repo.update(member)

    def renew_loan(
            self,
            loan_id: str,
            extra_days: int = DEFAULT_LOAN_DURATION_DAYS,
    ) -> Loan:
        """
        Przedłuża termin zwrotu o extra_days.
        Podnosi KeyError, jeśli wypożyczenie nie istnieje.
        """
        loan = self.repo.get(Loan, loan_id)
        if not loan:
            raise KeyError(f"Loan {loan_id} not found")

        loan.renew(extra_days=extra_days)
        self.repo.update(loan)
        return loan

    def cancel_loan(self, loan_id: str) -> None:
        """
        Anuluje wypożyczenie:
        - Przywraca status książki na AVAILABLE.
        - Usuwa wpis Loan z repo.
        Podnosi KeyError, jeśli wypożyczenie nie istnieje.
        """
        loan = self.repo.get(Loan, loan_id)
        if not loan:
            raise KeyError(f"Loan {loan_id} not found")

        book = self.repo.get(Book, loan.isbn)
        book.mark_returned()
        self.repo.update(book)

        self.repo.delete(Loan, loan_id)

    def list_active_loans(self) -> List[Loan]:
        """
        Zwraca listę aktywnych wypożyczeń.
        """
        return [
            loan
            for loan in self.repo.list(Loan)
            if loan.returned_on is None
        ]

    def list_overdue_loans(self) -> List[Loan]:
        """
        Zwraca listę przeterminowanych wypożyczeń.
        """
        return [
            loan
            for loan in self.list_active_loans()
            if loan.is_overdue
        ]

    def count_loans(self) -> int:
        """
        Zwraca łączną liczbę wypożyczeń.
        """
        return self.repo.count(Loan)
