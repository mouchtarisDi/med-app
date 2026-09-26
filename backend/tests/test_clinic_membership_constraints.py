import pytest
from sqlalchemy.exc import IntegrityError

from app.db.models import Clinic, ClinicMembership, User


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
