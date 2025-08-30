import uuid
from datetime import date
from typing import List

from biblioteka.storage.repository import Repository
from biblioteka.models.reservation import Reservation
from biblioteka.models.book import Book
from biblioteka.utils.exceptions import BookNotAvailable


class ReservationService:
    """
    Serwis obsługi rezerwacji książek:
    tworzenie nowych rezerwacji, anulowanie,
    wygaszanie oraz podstawowe statystyki.
    """

    def __init__(self, repo: Repository):
        """
        Inicjalizuje serwis z repozytorium
        przechowującym obiekty Reservation i Book.
        """
        self.repo = repo

    def reserve_book(self, member_id: str, isbn: str) -> Reservation:
        """
        Tworzy nową rezerwację:
        1. Sprawdza, czy książka istnieje.
        2. Oznacza książkę jako zarezerwowaną i zapisuje w repozytorium.
        3. Tworzy obiekt Reservation z unikalnym ID i datą rezerwacji.
        4. Dodaje rezerwację do repozytorium.
        Zwraca utworzoną rezerwację.
        Podnosi BookNotAvailable, jeśli książka nie istnieje.
        """
        book = self.repo.get(Book, isbn)
        if not book:
            raise BookNotAvailable(f"Book {isbn} not found in catalog")

        book.mark_reserved()
        self.repo.update(book)

        reservation = Reservation(
            reservation_id=str(uuid.uuid4()),
            member_id=member_id,
            isbn=isbn,
            reserved_on=date.today()
        )
        self.repo.add(reservation)
        return reservation

    def cancel_reservation(self, reservation_id: str) -> None:
        """
        Anuluje istniejącą rezerwację:
        1. Pobiera Reservation, podnosi KeyError, jeśli nie istnieje.
        2. Wywołuje metodę cancel() na obiekcie
        (może podnieść ValueError lub ReservationExpired).
        3. Aktualizuje rezerwację w repozytorium.
        4. Przywraca status książki na
        AVAILABLE i aktualizuje Book w repozytorium.
        """
        reservation = self.repo.get(Reservation, reservation_id)
        if not reservation:
            raise KeyError(f"Reservation {reservation_id} not found")

        reservation.cancel()
        self.repo.update(reservation)

        book = self.repo.get(Book, reservation.isbn)
        book.mark_returned()
        self.repo.update(book)

    def expire_reservations(self) -> List[Reservation]:
        """
        Przegląda wszystkie rezerwacje i wygasza te, których termin minął:
        - Dla każdej rezerwacji wywołuje is_expired(),
        a jeśli True, to expire() i aktualizuje w repo.
        - Zwraca listę wszystkich wygaszonych obiektów Reservation.
        """
        expired = []
        for r in self.repo.list(Reservation):
            if r.is_expired():
                r.expire()
                self.repo.update(r)
                expired.append(r)
        return expired

    def list_active_reservations(self) -> List[Reservation]:
        """
        Zwraca listę wszystkich aktywnych rezerwacji.
        """
        return [r for r in self.repo.list(Reservation) if r.active]

    def list_expired_reservations(self) -> List[Reservation]:
        """
        Zwraca listę rezerwacji,
        które są przeterminowane (is_expired() == True).
        """
        return [r for r in self.repo.list(Reservation) if r.is_expired()]

    def count_reservations(self) -> int:
        """
        Zwraca łączną liczbę rezerwacji w repozytorium.
        """
        return self.repo.count(Reservation)
