from typing import List
from datetime import timedelta

from biblioteka.storage.repository import Repository
from biblioteka.models.member import Member
from biblioteka.utils.exceptions import MemberNotFound, MembershipExpired
from biblioteka.config import DEFAULT_MEMBERSHIP_DURATION_DAYS


class MemberService:
    """
    Serwis zarządzania członkami biblioteki:
    rejestracja, usuwanie, odnowienie członkostwa, wyszukiwanie i statystyki.
    """

    def __init__(self, repo: Repository):
        """
        Inicjalizuje serwis z repozytorium przechowującym obiekty Member.
        """
        self.repo = repo

    def register_member(self, member: Member) -> None:
        """
        Rejestruje nowego członka.
        Podnosi ValueError, jeśli member_id jest już w użyciu.
        """
        if self.repo.get(Member, member.member_id):
            raise ValueError(f"Member {member.member_id} already registered")
        self.repo.add(member)

    def deregister_member(self, member_id: str) -> None:
        """
        Usuwa członka z systemu:
        - Podnosi MemberNotFound, jeśli nie ma takiego member_id.
        - Podnosi ValueError, jeśli członek ma nadal aktywne wypożyczenia.
        """
        member = self.repo.get(Member, member_id)
        if not member:
            raise MemberNotFound(f"Member {member_id} not found")
        if member.current_loans:
            raise ValueError("Cannot deregister member with active loans")
        self.repo.delete(Member, member_id)

    def renew_membership(
            self,
            member_id: str,
            extra_days: int = DEFAULT_MEMBERSHIP_DURATION_DAYS,
    ) -> Member:
        """
        Przedłuża członkostwo o extra_days dni.
        - Podnosi MemberNotFound, jeśli nie znaleziono member_id.
        - Zwraca zaktualizowany obiekt Member.
        """
        member = self.repo.get(Member, member_id)
        if not member:
            raise MemberNotFound(f"Member {member_id} not found")
        member.renew_membership(extra_days)
        self.repo.update(member)
        return member

    def list_active(self) -> List[Member]:
        """
        Zwraca listę wszystkich aktywnych członków (członkostwo ważne).
        """
        return [m for m in self.repo.list(Member) if m.is_membership_active()]

    def list_expired(self) -> List[Member]:
        """
        Zwraca listę członków z wygasłym członkostwem.
        """
        return [
            member
            for member in self.repo.list(Member)
            if not member.is_membership_active()
        ]

    def find_member(self, member_id: str) -> Member:
        """
        Zwraca obiekt Member po member_id.
        Podnosi MemberNotFound, jeśli nie istnieje.
        """
        member = self.repo.get(Member, member_id)
        if not member:
            raise MemberNotFound(f"Member {member_id} not found")
        return member

    def force_expire(self, member_id: str) -> Member:
        """
        Wymusza wygaśnięcie członkostwa:
        ustawia expiry na dzień przed datą rejestracji.
        - Podnosi MemberNotFound lub MembershipExpired,
        jeśli członkostwo nadal aktywne.
        Zwraca zaktualizowany obiekt Member.
        """
        member = self.find_member(member_id)
        member.membership_expiry = member.registered_on - timedelta(days=1)
        if member.is_membership_active():
            raise MembershipExpired("Cannot force expire an active membership")
        self.repo.update(member)
        return member

    def count_members(self) -> int:
        """
        Zwraca liczbę wszystkich zarejestrowanych członków.
        """
        return self.repo.count(Member)
