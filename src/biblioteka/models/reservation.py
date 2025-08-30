from dataclasses import dataclass, field
from datetime import date, timedelta

from biblioteka.config import DEFAULT_RESERVATION_DURATION_DAYS
from biblioteka.utils.exceptions import ReservationExpired


@dataclass
class Reservation:
    reservation_id: str
    member_id: str
    isbn: str
    reserved_on: date
    expiration_date: date = field(init=False)
    active: bool = True

    def __post_init__(self):
        """
        Ustawia datę wygaśnięcia rezerwacji
        na reserved_on + domyślny czas trwania.
        Metoda wywoływana automatycznie po inicjalizacji obiektu.
        """
        self.expiration_date = (
                self.reserved_on
                + timedelta(days=DEFAULT_RESERVATION_DURATION_DAYS)
        )

    def cancel(self) -> None:
        """
        Anuluje aktywną rezerwację.
        - Podnosi ValueError, jeśli rezerwacja jest już nieaktywna.
        - Podnosi ReservationExpired,
        jeśli rezerwacja minęła (data > expiration_date).
        """
        if not self.active:
            raise ValueError(
                f"Reservation {self.reservation_id} "
                f"is already inactive"
            )
        if self.is_expired():
            raise ReservationExpired(
                f"Reservation {self.reservation_id} "
                f"expired on {self.expiration_date}"
            )
        self.active = False

    def is_expired(self) -> bool:
        """
        Sprawdza, czy rezerwacja przekroczyła datę wygaśnięcia.
        Zwraca True, jeśli dzisiejsza data jest po expiration_date.
        """
        return date.today() > self.expiration_date

    def expire(self) -> None:
        """
        Automatycznie wygasza rezerwację po upływie terminu.
        - Ustawia active=False, jeśli rezerwacja
        jest aktywna i data > expiration_date.
        - Nie wykonuje akcji, jeśli rezerwacja jest
        już nieaktywna lub termin jeszcze nie nadszedł.
        """
        if self.active and self.is_expired():
            self.active = False

    def __str__(self) -> str:
        """
        Zwraca czytelną reprezentację rezerwacji:
        'Reservation <reservation_id> for <isbn> – active/inactive'
        """
        state = "active" if self.active else "inactive"
        return f"Reservation {self.reservation_id} for {self.isbn} – {state}"
