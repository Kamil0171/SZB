from datetime import datetime, timedelta, timezone
from biblioteka.models.user import User, Role


def make_user(**kwargs):
    defaults = {
        "user_id": "U1",
        "name": "Alicja",
        "role": Role.STUDENT,
        "joined_on": datetime.now(timezone.utc) - timedelta(days=1),
    }
    defaults.update(kwargs)
    return User(**defaults)


def test_is_admin_and_active():
    u = make_user(role=Role.ADMIN)
    assert u.is_admin()
    u.deactivate()
    assert not u.is_admin()


def test_has_permission_various_roles():
    u1 = make_user(role=Role.LIBRARIAN)
    assert u1.has_permission("loan")
    assert u1.has_permission("add_book")
    assert not u1.has_permission("change_role")

    u2 = make_user(role=Role.STUDENT)
    assert u2.has_permission("reserve")
    assert not u2.has_permission("remove_book")

    u3 = make_user(role=Role.GUEST)
    assert not u3.has_permission("loan")


def test_activate_deactivate_login_updates_last_login():
    u = make_user()
    assert u.is_active
    u.deactivate()
    assert not u.is_active
    u.activate()
    assert u.is_active

    assert u.last_login is None
    u.login()
    assert isinstance(u.last_login, datetime)
    prev = u.last_login
    u.login()
    assert u.last_login >= prev


def test_str_shows_role_name_and_active_flag():
    u = make_user(role=Role.TEACHER)
    s = str(u)
    assert "TEACHER" in s
    assert "active" in s


def test_user_with_other_actions_denied():
    u = make_user(role=Role.STUDENT)
    assert not u.has_permission("remove_book")


def test_last_login_none_then_updated_twice():
    u = make_user()
    assert u.last_login is None
    u.login()
    first = u.last_login
    u.login()
    second = u.last_login
    assert second >= first


def test_login_sets_last_login_and_str():
    u = make_user()
    assert u.last_login is None
    u.login()
    assert isinstance(u.last_login, datetime)
    s = str(u)
    assert u.user_id in s
