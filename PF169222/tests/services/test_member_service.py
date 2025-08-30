import pytest
from datetime import date, timedelta
from biblioteka.models.member import Member
from biblioteka.services.member_service import MemberService
from biblioteka.storage.repository import Repository
from biblioteka.utils.exceptions import MemberNotFound


@pytest.fixture
def repo():
    return Repository()


@pytest.fixture
def member_svc(repo):
    return MemberService(repo)


@pytest.fixture
def sample_member():
    return Member(
        member_id="M1",
        name="Jan",
        registered_on=date.today()
    )


def test_register_and_find_member(member_svc, repo, sample_member):
    member_svc.register_member(sample_member)
    m = member_svc.find_member("M1")
    assert m is sample_member


def test_register_duplicate_raises(member_svc, sample_member):
    member_svc.register_member(sample_member)
    with pytest.raises(ValueError):
        member_svc.register_member(sample_member)


def test_deregister_member_success(member_svc, sample_member):
    member_svc.register_member(sample_member)
    member_svc.deregister_member("M1")
    with pytest.raises(MemberNotFound):
        member_svc.find_member("M1")


def test_deregister_with_loans_raises(member_svc, sample_member):
    member_svc.register_member(sample_member)
    sample_member.current_loans.append("L1")
    with pytest.raises(ValueError):
        member_svc.deregister_member("M1")


def test_renew_membership(member_svc, sample_member):
    member_svc.register_member(sample_member)
    old_expiry = sample_member.membership_expiry
    renewed = member_svc.renew_membership("M1", extra_days=30)
    assert renewed.membership_expiry == old_expiry + timedelta(days=30)


def test_list_active_and_expired(member_svc, sample_member):
    member_svc.register_member(sample_member)
    active = member_svc.list_active()
    assert sample_member in active


    sample_member.membership_expiry = date.today() - timedelta(days=1)
    expired = member_svc.list_expired()
    assert sample_member in expired


def test_find_missing_member_raises(member_svc):
    with pytest.raises(MemberNotFound):
        member_svc.find_member("NOPE")
