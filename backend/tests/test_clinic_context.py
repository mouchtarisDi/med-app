from datetime import timedelta
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import inspect, select
from sqlalchemy.exc import OperationalError

from app.api.deps import get_current_clinic_membership
from app.core.security import create_access_token
from app.db.models import (
    Clinic, ClinicMembership, MembershipRole, MembershipRoleValue, User,
)
from app.db.session import get_db


@pytest.fixture
def context_data(db_session):
    user = User(email="context@example.invalid", full_name="Context User",
                hashed_password="synthetic-unused-hash", is_active=True)
    other = User(email="other-context@example.invalid", full_name="Other User",
                 hashed_password="synthetic-unused-hash", is_active=True)
    clinics = [Clinic(name=name) for name in ("Clinic A", "Clinic B", "Other Clinic")]
    db_session.add_all([user, other, *clinics])
    db_session.flush()
    memberships = [
        ClinicMembership(user_id=user.id, clinic_id=clinics[0].id),
        ClinicMembership(user_id=user.id, clinic_id=clinics[1].id),
        ClinicMembership(user_id=other.id, clinic_id=clinics[2].id),
    ]
    db_session.add_all(memberships)
    db_session.flush()
    db_session.add_all([
        MembershipRole(membership_id=memberships[0].id, role=role)
        for role in (MembershipRoleValue.OWNER, MembershipRoleValue.DOCTOR)
    ] + [MembershipRole(membership_id=memberships[1].id,
                        role=MembershipRoleValue.SECRETARY)])
    db_session.flush()
    return user, clinics, memberships


@pytest.fixture
def context_client(db_session):
    # A separate app keeps this route out of the production application.
    app = FastAPI()

    @app.get("/clinics/{clinic_id}/context")
    def context(
        membership: Annotated[ClinicMembership, Depends(get_current_clinic_membership)],
    ):
        # Assert eager loading before accessing either relationship.
        assert "clinic" not in inspect(membership).unloaded
        assert "roles" not in inspect(membership).unloaded
        return {
            "membership_id": membership.id,
            "clinic_id": membership.clinic.id,
            "clinic_name": membership.clinic.name,
            "roles": sorted(role.role.value for role in membership.roles),
        }

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client


def auth_headers(user):
    return {"Authorization": f"Bearer {create_access_token({'sub': str(user.id)})}"}


def test_valid_membership_returns_clinic_and_multiple_roles(context_client, context_data):
    user, clinics, memberships = context_data
    response = context_client.get(f"/clinics/{clinics[0].id}/context", headers=auth_headers(user))
    assert response.status_code == 200
    assert response.json() == {
        "membership_id": memberships[0].id, "clinic_id": clinics[0].id,
        "clinic_name": "Clinic A", "roles": ["DOCTOR", "OWNER"],
    }


def test_two_clinics_resolve_independently_without_role_leakage(context_client, context_data):
    user, clinics, memberships = context_data
    headers = auth_headers(user)
    for index, roles in ((1, ["SECRETARY"]), (0, ["DOCTOR", "OWNER"]), (1, ["SECRETARY"])):
        response = context_client.get(f"/clinics/{clinics[index].id}/context", headers=headers)
        assert response.status_code == 200
        assert response.json()["membership_id"] == memberships[index].id
        assert response.json()["clinic_id"] == clinics[index].id
        assert response.json()["roles"] == roles


def test_other_users_membership_and_absent_clinic_have_identical_404(
    context_client, context_data, db_session,
):
    user, clinics, _ = context_data
    assert db_session.get(Clinic, 2147483647) is None
    responses = [context_client.get(f"/clinics/{clinic_id}/context", headers=auth_headers(user))
                 for clinic_id in (clinics[2].id, 2147483647)]
    for response in responses:
        assert response.status_code == 404
        assert response.json() == {"detail": "Clinic not found or inaccessible"}


def test_zero_roles_is_valid(context_client, context_data, db_session):
    user, clinics, memberships = context_data
    for role in db_session.scalars(select(MembershipRole).where(
        MembershipRole.membership_id == memberships[1].id,
    )).all():
        db_session.delete(role)
    db_session.flush()
    response = context_client.get(f"/clinics/{clinics[1].id}/context", headers=auth_headers(user))
    assert response.status_code == 200
    assert response.json()["roles"] == []


@pytest.mark.parametrize("clinic_id", ["invalid", "0", "-1", "1.5", "2147483648"])
def test_invalid_clinic_id(context_client, context_data, clinic_id):
    user, _, _ = context_data
    response = context_client.get(f"/clinics/{clinic_id}/context", headers=auth_headers(user))
    assert response.status_code == 422


@pytest.mark.parametrize("credential", ["missing", "invalid", "expired"])
def test_invalid_credentials(context_client, context_data, credential):
    user, clinics, _ = context_data
    headers = {}
    if credential == "invalid":
        headers = {"Authorization": "Bearer invalid-jwt"}
    elif credential == "expired":
        token = create_access_token({"sub": str(user.id)}, expires_delta=timedelta(minutes=-1))
        headers = {"Authorization": f"Bearer {token}"}
    response = context_client.get(f"/clinics/{clinics[0].id}/context", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_inactive_user(context_client, context_data, db_session):
    user, clinics, _ = context_data
    user.is_active = False
    db_session.flush()
    response = context_client.get(f"/clinics/{clinics[0].id}/context", headers=auth_headers(user))
    assert response.status_code == 403
    assert response.json() == {"detail": "Inactive user"}


def test_superuser_cannot_bypass_membership(context_client, context_data, db_session):
    user, clinics, _ = context_data
    user.is_superuser = True
    db_session.flush()
    response = context_client.get(f"/clinics/{clinics[2].id}/context", headers=auth_headers(user))
    assert response.status_code == 404
    assert response.json() == {"detail": "Clinic not found or inaccessible"}


def test_database_changes_are_reflected_with_same_jwt(context_client, context_data, db_session):
    user, clinics, memberships = context_data
    headers = auth_headers(user)
    path = f"/clinics/{clinics[1].id}/context"
    assert context_client.get(path, headers=headers).json()["roles"] == ["SECRETARY"]
    role = db_session.execute(select(MembershipRole).where(
        MembershipRole.membership_id == memberships[1].id,
    )).scalar_one()
    role.role = MembershipRoleValue.DOCTOR
    db_session.flush()
    assert context_client.get(path, headers=headers).json()["roles"] == ["DOCTOR"]
    db_session.delete(role)
    db_session.flush()
    assert context_client.get(path, headers=headers).json()["roles"] == []
    db_session.delete(memberships[1])
    db_session.flush()
    assert context_client.get(path, headers=headers).status_code == 404
    db_session.add(ClinicMembership(user_id=user.id, clinic_id=clinics[1].id))
    db_session.flush()
    assert context_client.get(path, headers=headers).status_code == 200


def test_database_failure_propagates(context_client, context_data, db_session, monkeypatch):
    user, clinics, _ = context_data
    headers = auth_headers(user)
    original_execute = db_session.execute
    failure = OperationalError("SELECT", {}, Exception("Synthetic failure"))

    def failing_execute(statement, *args, **kwargs):
        if statement.column_descriptions[0].get("entity") is ClinicMembership:
            raise failure
        return original_execute(statement, *args, **kwargs)

    monkeypatch.setattr(db_session, "execute", failing_execute)
    with pytest.raises(OperationalError) as exc_info:
        context_client.get(f"/clinics/{clinics[0].id}/context", headers=headers)
    assert exc_info.value is failure


def test_context_route_is_not_registered_in_production():
    from app.main import app

    for route in app.routes:
        assert getattr(route, "path", None) != "/clinics/{clinic_id}/context"

    # Exercise routing too, including routers represented by wrapper entries.
    with TestClient(app) as client:
        response = client.get("/clinics/1/context")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
