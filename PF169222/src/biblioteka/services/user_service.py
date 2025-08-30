import uuid
from datetime import datetime, timezone
from typing import List

from biblioteka.storage.repository import Repository
from biblioteka.models.user import User, Role
from biblioteka.utils.exceptions import UserNotFound, PermissionDenied


class UserService:
    """
    Serwis zarządzania użytkownikami:
    tworzenie kont, zmiana ról, aktywacja/dezaktywacja,
    logowanie oraz podstawowe raporty.
    """

    def __init__(self, repo: Repository):
        """
        Inicjalizuje serwis z repozytorium przechowującym obiekty User.
        Repozytorium służy do zapisywania,
        odczytu i aktualizacji kont użytkowników.
        """
        self.repo = repo

    def create_user(self, name: str, role: Role) -> User:
        """
        Tworzy nowe konto użytkownika:
        - Generuje unikalny user_id.
        - Ustawia datę dołączenia na teraz (UTC).
        - Zapisuje użytkownika w repozytorium.
        Zwraca obiekt User.
        """
        user = User(
            user_id=str(uuid.uuid4()),
            name=name,
            role=role,
            joined_on=datetime.now(timezone.utc)
        )
        self.repo.add(user)
        return user

    def get_user(self, user_id: str) -> User:
        """
        Pobiera użytkownika po jego identyfikatorze.
        Podnosi UserNotFound, jeśli konto nie istnieje.
        """
        user = self.repo.get(User, user_id)
        if not user:
            raise UserNotFound(f"User {user_id} not found")
        return user

    def change_role(
            self,
            admin_id: str,
            target_user_id: str,
            new_role: Role,
    ) -> User:
        """
        Zmienia rolę innego użytkownika:
        - Weryfikuje, że admin_id należy do aktywnego ADMINA.
        - Podnosi PermissionDenied, jeśli nie ma uprawnień.
        - Modyfikuje pole role i aktualizuje w repozytorium.
        Zwraca zmodyfikowany obiekt User.
        """
        admin = self.get_user(admin_id)
        if not admin.is_admin():
            raise PermissionDenied("Only ADMIN can change roles")
        user = self.get_user(target_user_id)
        user.role = new_role
        self.repo.update(user)
        return user

    def deactivate_user(self, admin_id: str, target_user_id: str) -> User:
        """
        Dezaktywuje konto wskazanego użytkownika:
        - Sprawdza uprawnienia ADMINA.
        - Ustawia is_active = False i zapisuje zmiany.
        Zwraca zmodyfikowany obiekt User.
        """
        admin = self.get_user(admin_id)
        if not admin.is_admin():
            raise PermissionDenied("Only ADMIN can deactivate users")
        user = self.get_user(target_user_id)
        user.deactivate()
        self.repo.update(user)
        return user

    def activate_user(self, admin_id: str, target_user_id: str) -> User:
        """
        Aktywuje (przywraca) konto użytkownika:
        - Wymaga uprawnień ADMINA.
        - Ustawia is_active = True i zapisuje zmiany.
        Zwraca zmodyfikowany obiekt User.
        """
        admin = self.get_user(admin_id)
        if not admin.is_admin():
            raise PermissionDenied("Only ADMIN can activate users")
        user = self.get_user(target_user_id)
        user.activate()
        self.repo.update(user)
        return user

    def login_user(self, user_id: str) -> User:
        """
        Rejestruje moment logowania:
        - Pobiera konto, podnosi UserNotFound jeśli brak.
        - Wywołuje metodę login() na modelu,
        ustawiając last_login = teraz (UTC).
        - Aktualizuje obiekt w repozytorium.
        Zwraca zaktualizowany obiekt User.
        """
        user = self.get_user(user_id)
        user.login()
        self.repo.update(user)
        return user

    def list_users_by_role(self, role: Role) -> List[User]:
        """
        Zwraca listę wszystkich użytkowników o wskazanej roli.
        """
        return [u for u in self.repo.list(User) if u.role == role]

    def list_active_users(self) -> List[User]:
        """
        Zwraca listę aktywnych (is_active=True) użytkowników.
        """
        return [u for u in self.repo.list(User) if u.is_active]

    def count_users(self) -> int:
        """
        Zwraca łączną liczbę zapisanych kont użytkowników.
        """
        return self.repo.count(User)
