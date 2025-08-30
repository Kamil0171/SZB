from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional
import re

from biblioteka.utils.exceptions import MembershipExpired

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PHONE_REGEX = re.compile(r"^\+?[0-9]{7,15}$")


@dataclass
class Member:
    member_id: str
    name: str
    registered_on: date
    email: Optional[str] = None
    phone: Optional[str] = None
    membership_expiry: date = field(
        default_factory=lambda: date.today() + timedelta(days=365)
    )
    max_books: int = 5
    current_loans: List[str] = field(
        default_factory=list,
    )

    def __post_init__(self):
        if self.email and not EMAIL_REGEX.match(self.email):
            raise ValueError(f"Invalid email address: {self.email}")
        if self.phone and not PHONE_REGEX.match(self.phone):
            raise ValueError(f"Invalid phone number: {self.phone}")

    def is_membership_active(self) -> bool:
        """
        Sprawdza, czy członkostwo jest wciąż aktywne.
        Zwraca True, jeśli dzisiejsza data jest przed datą wygaśnięcia.
        """
        return date.today() <= self.membership_expiry

    def can_loan(self) -> bool:
        """
        Określa, czy członek może wypożyczyć kolejną książkę.
        Podnosi MembershipExpired, jeśli członkostwo wygasło.
        Zwraca True, jeśli liczba aktualnych wypożyczeń jest poniżej limitu.
        """
        if not self.is_membership_active():
            raise MembershipExpired(
                f"Membership expired on {self.membership_expiry}"
            )
        return len(self.current_loans) < self.max_books

    def add_loan(self, loan_id: str) -> None:
        """
        Dodaje nowe wypożyczenie do listy current_loans.
        Podnosi ValueError, jeśli przekroczono maksymalny limit wypożyczeń.
        """
        if not self.can_loan():
            raise ValueError(f"Member {self.member_id} cannot take more loans")
        self.current_loans.append(loan_id)

    def remove_loan(self, loan_id: str) -> None:
        """
        Usuwa wypożyczenie z listy current_loans po zwrocie.
        Podnosi ValueError, jeśli podany identyfikator nie istnieje.
        """
        if loan_id in self.current_loans:
            self.current_loans.remove(loan_id)
        else:
            raise ValueError(
                f"Loan {loan_id} "
                f"not found for member {self.member_id}"
            )

    def renew_membership(self, extra_days: int = 365) -> None:
        """
        Przedłuża członkostwo o określoną liczbę dni.
        Jeśli członkostwo wygasło, ustawia nowe wygaśnięcie od dzisiaj.
        W przeciwnym przypadku dodaje extra_days do obecnej daty wygaśnięcia.
        """
        if not self.is_membership_active():
            self.membership_expiry = date.today() + timedelta(days=extra_days)
        else:
            self.membership_expiry += timedelta(days=extra_days)

    def __str__(self) -> str:
        """
        Zwraca czytelną reprezentację członka:
        '<Imię Nazwisko> (<member_id>) – membership
        active/expired until <expiry_date>'
        """
        status = "active" if self.is_membership_active() else "expired"
        return (
            f"{self.name} ({self.member_id}) – "
            f"membership {status} until {self.membership_expiry}"
        )
