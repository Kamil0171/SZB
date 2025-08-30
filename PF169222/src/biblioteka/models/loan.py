from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from biblioteka.config import DEFAULT_LOAN_DURATION_DAYS, MAX_RENEWALS
from biblioteka.utils.exceptions import MaxRenewalsExceeded


@dataclass
class Loan:
    loan_id: str
    member_id: str
    isbn: str
    loan_date: date
    due_date: date
    returned_on: Optional[date] = None
    renew_count: int = 0

    def mark_returned(self, return_date: date) -> None:
        """
        Oznacza wypożyczenie jako zwrócone.
        Podnosi ValueError, jeśli już wcześniej zwrócono tę pozycję.
        """
        if self.returned_on is not None:
            raise ValueError(
                f"Loan {self.loan_id} "
                f"already returned on {self.returned_on}"
            )
        self.returned_on = return_date

    @property
    def is_overdue(self) -> bool:
        """
        Sprawdza, czy wypożyczenie jest przeterminowane.
        Zwraca True, gdy książka nie została zwrócona, a termin minął.
        """
        return self.returned_on is None and date.today() > self.due_date

    def can_renew(self) -> bool:
        """
        Określa, czy można odnowić wypożyczenie.
        Warunki: nie zostało zwrócone oraz
        nie przekroczono maksymalnej liczby odnowień.
        """
        return (
                self.returned_on is None
                and self.renew_count < MAX_RENEWALS
        )

    def renew(self, extra_days: int = DEFAULT_LOAN_DURATION_DAYS) -> None:
        """
        Przedłuża termin zwrotu o określoną liczbę dni.
        Podnosi MaxRenewalsExceeded,
        jeśli przekroczono dozwoloną liczbę odnowień.
        """
        if not self.can_renew():
            raise MaxRenewalsExceeded(
                f"Loan {self.loan_id} "
                f"cannot be renewed more than {MAX_RENEWALS} times"
            )
        self.due_date += timedelta(days=extra_days)
        self.renew_count += 1

    def __str__(self) -> str:
        """
        Zwraca czytelną reprezentację wypożyczenia:
        np. "Loan <id>: <isbn> to <member_id> – out/returned"
        """
        status = "returned" if self.returned_on else "out"
        return (
            f"Loan {self.loan_id}: {self.isbn} "
            f"to {self.member_id} – {status}"
        )
