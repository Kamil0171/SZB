from dataclasses import dataclass
from enum import Enum, auto
from datetime import datetime, timezone
from typing import Optional


class Role(Enum):
    GUEST = auto()
    STUDENT = auto()
    TEACHER = auto()
    LIBRARIAN = auto()
    ADMIN = auto()


@dataclass
class User:
    user_id: str
    name: str
    role: Role
    joined_on: datetime
    is_active: bool = True
    last_login: Optional[datetime] = None

    def is_admin(self) -> bool:
        """
        Sprawdza, czy użytkownik jest administratorem i konto jest aktywne.
        Zwraca True tylko dla roli ADMIN i is_active=True.
        """
        return self.role == Role.ADMIN and self.is_active

    def has_permission(self, action: str) -> bool:
        """
        Określa, czy użytkownik ma prawo do wykonania danej akcji.
        - ADMIN: wszystkie akcje.
        - LIBRARIAN: akcje związane z wypożyczeniami i zarządzaniem książkami.
        - STUDENT/TEACHER: akcje loan i reserve.
        - GUEST: brak uprawnień do chronionych akcji.
        Jeśli konto jest nieaktywne, zawsze False.
        """
        if not self.is_active:
            return False
        if self.role == Role.ADMIN:
            return True
        if self.role == Role.LIBRARIAN and action in (
            "loan", "return", "reserve", "add_book", "remove_book"
        ):
            return True
        if (
                self.role in (Role.STUDENT, Role.TEACHER)
                and action in ("loan", "reserve")
        ):
            return True
        return False

    def deactivate(self) -> None:
        """Dezaktywuje konto użytkownika (ustawia is_active=False)."""
        self.is_active = False

    def activate(self) -> None:
        """Aktywuje konto użytkownika (ustawia is_active=True)."""
        self.is_active = True

    def login(self) -> None:
        """
        Aktualizuje timestamp ostatniego logowania do UTC.
        Pozwala śledzić, kiedy użytkownik ostatnio korzystał z systemu.
        """
        self.last_login = datetime.now(timezone.utc)

    def __str__(self) -> str:
        """
        Zwraca czytelną reprezentację użytkownika:
        'User <user_id> (<name>) – role <ROLE>, active/inactive'
        """
        status = "active" if self.is_active else "inactive"
        return (
            f"User {self.user_id} ({self.name}) "
            f"– role {self.role.name}, {status}"
        )
