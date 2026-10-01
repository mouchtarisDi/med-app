import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DataError, IntegrityError

from app.db.models import (
    Clinic,
    ClinicMembership,
    MembershipRole,
    MembershipRoleValue,
    User,
)


def test_duplicate_user_clinic_membership_is_rejected(db_session):
    user = User(
        email="membership-constraint@example.invalid",
        hashed_password="synthetic-unused-password-hash",
        full_name="Synthetic Test User",
    )
    clinic = Clinic(name="Synthetic Test Clinic")
    db_session.add_all([user, clinic])
    db_session.flush()

    first_membership = ClinicMembership(user_id=user.id, clinic_id=clinic.id)
    db_session.add(first_membership)
    db_session.flush()

    with pytest.raises(IntegrityError) as exc_info:
        with db_session.begin_nested():
            duplicate_membership = ClinicMembership(
                user_id=user.id,
                clinic_id=clinic.id,
            )
            db_session.add(duplicate_membership)
            db_session.flush()

    assert exc_info.value.orig.pgcode == "23505"
    assert (
        exc_info.value.orig.diag.constraint_name
        == "uq_clinic_memberships_user_id_clinic_id"
    )


def test_membership_with_nonexistent_user_is_rejected(db_session):
    clinic = Clinic(name="Synthetic FK Test Clinic")
    db_session.add(clinic)
    db_session.flush()

    nonexistent_user_id = -1
    assert db_session.get(User, nonexistent_user_id) is None

    with pytest.raises(IntegrityError) as exc_info:
        with db_session.begin_nested():
            membership = ClinicMembership(
                user_id=nonexistent_user_id,
                clinic_id=clinic.id,
            )
            db_session.add(membership)
            db_session.flush()

    assert exc_info.value.orig.pgcode == "23503"
    assert (
        exc_info.value.orig.diag.constraint_name
        == "clinic_memberships_user_id_fkey"
    )
    # A database read confirms the outer transaction survived the failed insert.
    db_session.refresh(clinic)
    assert clinic.name == "Synthetic FK Test Clinic"


def test_membership_with_nonexistent_clinic_is_rejected(db_session):
    user = User(
        email="membership-fk-constraint@example.invalid",
        hashed_password="synthetic-unused-password-hash",
        full_name="Synthetic FK Test User",
    )
    db_session.add(user)
    db_session.flush()

    nonexistent_clinic_id = -1
    assert db_session.get(Clinic, nonexistent_clinic_id) is None

    with pytest.raises(IntegrityError) as exc_info:
        with db_session.begin_nested():
            membership = ClinicMembership(
                user_id=user.id,
                clinic_id=nonexistent_clinic_id,
            )
            db_session.add(membership)
            db_session.flush()

    assert exc_info.value.orig.pgcode == "23503"
    assert (
        exc_info.value.orig.diag.constraint_name
        == "clinic_memberships_clinic_id_fkey"
    )
    # A database read confirms the outer transaction survived the failed insert.
    db_session.refresh(user)
    assert user.full_name == "Synthetic FK Test User"


def test_membership_accepts_multiple_different_roles(db_session):
    user = User(
        email="multiple-roles@example.invalid",
        hashed_password="synthetic-unused-password-hash",
        full_name="Synthetic Multi-Role User",
    )
    clinic = Clinic(name="Synthetic Multi-Role Clinic")
    db_session.add_all([user, clinic])
    db_session.flush()

    membership = ClinicMembership(user_id=user.id, clinic_id=clinic.id)
    db_session.add(membership)
    db_session.flush()

    owner_role = MembershipRole(
        membership_id=membership.id, role=MembershipRoleValue.OWNER
    )
    doctor_role = MembershipRole(
        membership_id=membership.id, role=MembershipRoleValue.DOCTOR
    )
    db_session.add_all([owner_role, doctor_role])
    db_session.flush()

    roles = db_session.scalars(
        select(MembershipRole.role).where(
            MembershipRole.membership_id == membership.id
        )
    ).all()
    assert len(roles) == 2
    assert set(roles) == {MembershipRoleValue.OWNER, MembershipRoleValue.DOCTOR}


def test_duplicate_membership_role_is_rejected(db_session):
    user = User(
        email="duplicate-role@example.invalid",
        hashed_password="synthetic-unused-password-hash",
        full_name="Synthetic Duplicate-Role User",
    )
    clinic = Clinic(name="Synthetic Duplicate-Role Clinic")
    db_session.add_all([user, clinic])
    db_session.flush()

    membership = ClinicMembership(user_id=user.id, clinic_id=clinic.id)
    db_session.add(membership)
    db_session.flush()

    doctor_role = MembershipRole(
        membership_id=membership.id, role=MembershipRoleValue.DOCTOR
    )
    db_session.add(doctor_role)
    db_session.flush()

    with pytest.raises(IntegrityError) as exc_info:
        with db_session.begin_nested():
            duplicate_role = MembershipRole(
                membership_id=membership.id, role=MembershipRoleValue.DOCTOR
            )
            db_session.add(duplicate_role)
            db_session.flush()

    assert exc_info.value.orig.pgcode == "23505"
    assert (
        exc_info.value.orig.diag.constraint_name
        == "uq_membership_roles_membership_id_role"
    )
    # The original role remains readable after rolling back the failed insert.
    roles = db_session.scalars(
        select(MembershipRole.role).where(
            MembershipRole.membership_id == membership.id
        )
    ).all()
    assert roles == [MembershipRoleValue.DOCTOR]


def test_membership_role_enum_has_exactly_expected_values(db_session):
    roles = db_session.scalars(
        text("SELECT unnest(enum_range(NULL::membership_role))::text")
    ).all()

    assert roles == ["OWNER", "DOCTOR", "SECRETARY"]


def test_membership_role_enum_rejects_invalid_value(db_session):
    user = User(
        email="invalid-enum-role@example.invalid",
        hashed_password="synthetic-unused-password-hash",
        full_name="Synthetic Enum Test User",
    )
    clinic = Clinic(name="Synthetic Enum Test Clinic")
    db_session.add_all([user, clinic])
    db_session.flush()

    membership = ClinicMembership(user_id=user.id, clinic_id=clinic.id)
    db_session.add(membership)
    db_session.flush()

    with pytest.raises(DataError) as exc_info:
        with db_session.begin_nested():
            # Raw SQL bypasses Python enum conversion and executes immediately.
            db_session.execute(
                text(
                    "INSERT INTO membership_roles (membership_id, role) "
                    "VALUES (:membership_id, :role)"
                ),
                {"membership_id": membership.id, "role": "ADMIN"},
            )

    assert exc_info.value.orig.pgcode == "22P02"
    # The outer transaction remains usable and no invalid role was inserted.
    roles = db_session.scalars(
        select(MembershipRole.role).where(
            MembershipRole.membership_id == membership.id
        )
    ).all()
    assert roles == []
