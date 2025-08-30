import pytest
from datetime import datetime
from biblioteka.models.user import Role
from biblioteka.services.user_service import UserService
from biblioteka.storage.repository import Repository
from biblioteka.utils.exceptions import UserNotFound, PermissionDenied


@pytest.fixture
def repo():
    return Repository()


@pytest.fixture
def user_svc(repo):
    return UserService(repo)


def test_create_and_get_user(user_svc, repo):
    user = user_svc.create_user("Ala", Role.STUDENT)
    fetched = user_svc.get_user(user.user_id)
    assert fetched is user


def test_get_nonexistent_user_raises(user_svc):
    with pytest.raises(UserNotFound):
        user_svc.get_user("NOPE")


def test_change_role_permission(user_svc, repo):
    admin = user_svc.create_user("Adm", Role.ADMIN)
    user = user_svc.create_user("Bob", Role.STUDENT)
    updated = user_svc.change_role(admin.user_id, user.user_id, Role.TEACHER)
    assert updated.role == Role.TEACHER


def test_change_role_no_permission(user_svc):
    nonadmin = user_svc.create_user("Ewa", Role.STUDENT)
    with pytest.raises(PermissionDenied):
        user_svc.change_role(nonadmin.user_id, nonadmin.user_id, Role.ADMIN)


def test_deactivate_activate_login(user_svc):
    admin = user_svc.create_user("Adm", Role.ADMIN)
    user = user_svc.create_user("Tom", Role.STUDENT)
    deact = user_svc.deactivate_user(admin.user_id, user.user_id)
    assert not deact.is_active
    act = user_svc.activate_user(admin.user_id, user.user_id)
    assert act.is_active
    logged = user_svc.login_user(act.user_id)
    assert isinstance(logged.last_login, datetime)
