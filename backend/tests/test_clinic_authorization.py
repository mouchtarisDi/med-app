from datetime import timedelta
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from app.api.deps import get_current_clinic_membership, require_permission
from app.core.permissions import Permission
from app.core.security import create_access_token
from app.db.models import Clinic, ClinicMembership, MembershipRole, MembershipRoleValue, User
from app.db.session import get_db


# Explicit expected permissions independently describe the approved policy.
EXPECTED = {
    "owner": {
        "patients.read", "patients.create", "patients.update_basic", "patients.delete",
        "medical_records.read", "medical_records.write", "appointments.read",
        "appointments.manage", "payments.read", "payments.manage",
        "clinic.manage_members", "clinic.settings",
    },
    "doctor": {
        "patients.read", "patients.create", "patients.update_basic",
        "medical_records.read", "medical_records.write",
        "appointments.read", "appointments.manage",
    },
    "secretary": {
        "patients.read", "patients.create", "patients.update_basic",
        "appointments.read", "appointments.manage", "payments.read", "payments.manage",
    },
    "combined": {
        "patients.read", "patients.create", "patients.update_basic",
        "medical_records.read", "medical_records.write", "appointments.read",
        "appointments.manage", "payments.read", "payments.manage",
    },
}


@pytest.fixture
def authorization_data(db_session):
    user = User(email="authorization@example.invalid", full_name="Authorization User",
                hashed_password="synthetic-unused-hash", is_active=True)
    other = User(email="other-authorization@example.invalid", full_name="Other User",
                 hashed_password="synthetic-unused-hash", is_active=True)
    db_session.add_all([user, other])
    db_session.flush()
    memberships = {}
    role_sets = {
        "owner": [MembershipRoleValue.OWNER],
        "doctor": [MembershipRoleValue.DOCTOR],
        "secretary": [MembershipRoleValue.SECRETARY],
        "combined": [MembershipRoleValue.DOCTOR, MembershipRoleValue.SECRETARY],
        "empty": [],
        "other": [MembershipRoleValue.OWNER],
    }
    for name, roles in role_sets.items():
        clinic = Clinic(name=f"Authorization {name}")
        db_session.add(clinic)
        db_session.flush()
        membership = ClinicMembership(
            user_id=other.id if name == "other" else user.id, clinic_id=clinic.id,
        )
        db_session.add(membership)
        db_session.flush()
        db_session.add_all([
            MembershipRole(membership_id=membership.id, role=role) for role in roles
        ])
        memberships[name] = membership
    db_session.flush()
    return user, memberships


def authorization_path(clinic_id, permission):
    return f"/clinics/{clinic_id}/authorization/{permission.value}"


def token_headers(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


def permission_handler(permission):
    def handler(
        membership: Annotated[ClinicMembership, Depends(require_permission(permission))],
        context: Annotated[ClinicMembership, Depends(get_current_clinic_membership)],
    ):
        # The factory returns the original context, not a replacement or another query.
        assert membership is context
        return {"membership_id": membership.id, "clinic_id": membership.clinic.id}
    return handler


@pytest.fixture
def authorization_client(db_session):
    app = FastAPI()
    for permission in Permission:
        app.add_api_route(
            authorization_path("{clinic_id}", permission), permission_handler(permission),
            methods=["GET"],
        )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client


@pytest.mark.parametrize("role", ["owner", "doctor", "secretary", "combined"])
@pytest.mark.parametrize("permission", list(Permission))
def test_request_permission_matrix(authorization_client, authorization_data, role, permission):
    user, memberships = authorization_data
    membership = memberships[role]
    response = authorization_client.get(
        authorization_path(membership.clinic_id, permission), headers=token_headers(user),
    )
    if permission.value in EXPECTED[role]:
        assert response.status_code == 200
        assert response.json() == {
            "membership_id": membership.id, "clinic_id": membership.clinic_id,
        }
    else:
        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}


def test_owner_in_another_clinic_does_not_grant_access(authorization_client, authorization_data):
    user, memberships = authorization_data
    headers = token_headers(user)
    for role, status in (("owner", 200), ("doctor", 403), ("secretary", 403)):
        response = authorization_client.get(
            authorization_path(memberships[role].clinic_id, Permission.CLINIC_SETTINGS),
            headers=headers,
        )
        assert response.status_code == status
        if status == 403:
            assert response.json() == {"detail": "Forbidden"}


@pytest.mark.parametrize("role, permission", [
    ("doctor", Permission.PAYMENTS_MANAGE),
    ("secretary", Permission.MEDICAL_RECORDS_WRITE),
])
def test_roles_in_different_clinics_do_not_combine(
    authorization_client, authorization_data, role, permission,
):
    user, memberships = authorization_data
    response = authorization_client.get(
        authorization_path(memberships[role].clinic_id, permission), headers=token_headers(user),
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_zero_roles_denied(authorization_client, authorization_data):
    user, memberships = authorization_data
    response = authorization_client.get(
        authorization_path(memberships["empty"].clinic_id, Permission.PATIENTS_READ),
        headers=token_headers(user),
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_inaccessible_and_nonexistent_clinics_have_identical_404(
    authorization_client, authorization_data, db_session,
):
    user, memberships = authorization_data
    assert db_session.get(Clinic, 2147483647) is None
    headers = token_headers(user)
    for clinic_id in (memberships["other"].clinic_id, 2147483647):
        response = authorization_client.get(
            authorization_path(clinic_id, Permission.PATIENTS_READ), headers=headers,
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Clinic not found or inaccessible"}


@pytest.mark.parametrize("credential", ["missing", "invalid", "expired"])
def test_authentication_errors_preserved(authorization_client, authorization_data, credential):
    user, memberships = authorization_data
    headers = {}
    if credential == "invalid":
        headers = {"Authorization": "Bearer invalid-jwt"}
    elif credential == "expired":
        token = create_access_token({"sub": str(user.id)}, expires_delta=timedelta(minutes=-1))
        headers = {"Authorization": f"Bearer {token}"}
    response = authorization_client.get(
        authorization_path(memberships["owner"].clinic_id, Permission.PATIENTS_READ),
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_inactive_user_denied(authorization_client, authorization_data, db_session):
    user, memberships = authorization_data
    user.is_active = False
    db_session.flush()
    response = authorization_client.get(
        authorization_path(memberships["owner"].clinic_id, Permission.PATIENTS_READ),
        headers=token_headers(user),
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Inactive user"}


@pytest.mark.parametrize("role, status, detail", [
    ("other", 404, "Clinic not found or inaccessible"),
    ("doctor", 403, "Forbidden"),
])
def test_superuser_does_not_bypass_authorization(
    authorization_client, authorization_data, db_session, role, status, detail,
):
    user, memberships = authorization_data
    user.is_superuser = True
    db_session.flush()
    response = authorization_client.get(
        authorization_path(memberships[role].clinic_id, Permission.CLINIC_SETTINGS),
        headers=token_headers(user),
    )
    assert response.status_code == status
    assert response.json() == {"detail": detail}


def test_role_changes_take_effect_with_same_jwt(
    authorization_client, authorization_data, db_session,
):
    user, memberships = authorization_data
    membership = memberships["doctor"]
    headers = token_headers(user)
    path = authorization_path(membership.clinic_id, Permission.MEDICAL_RECORDS_WRITE)
    assert authorization_client.get(path, headers=headers).status_code == 200
    role = db_session.execute(select(MembershipRole).where(
        MembershipRole.membership_id == membership.id,
    )).scalar_one()
    role.role = MembershipRoleValue.SECRETARY
    db_session.flush()
    response = authorization_client.get(path, headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
    role.role = MembershipRoleValue.DOCTOR
    db_session.flush()
    assert authorization_client.get(path, headers=headers).status_code == 200


def test_database_errors_propagate(
    authorization_client, authorization_data, db_session, monkeypatch,
):
    user, memberships = authorization_data
    headers = token_headers(user)
    original_execute = db_session.execute
    failure = OperationalError("SELECT", {}, Exception("Synthetic failure"))

    def failing_execute(statement, *args, **kwargs):
        if statement.column_descriptions[0].get("entity") is ClinicMembership:
            raise failure
        return original_execute(statement, *args, **kwargs)

    monkeypatch.setattr(db_session, "execute", failing_execute)
    with pytest.raises(OperationalError) as exc_info:
        authorization_client.get(
            authorization_path(memberships["owner"].clinic_id, Permission.PATIENTS_READ),
            headers=headers,
        )
    assert exc_info.value is failure


def test_authorization_routes_are_not_in_production():
    from app.main import app

    with TestClient(app) as client:
        for permission in Permission:
            response = client.get(authorization_path(1, permission))
            assert response.status_code == 404
            assert response.json() == {"detail": "Not Found"}
