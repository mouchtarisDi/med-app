"""Real PostgreSQL-backed HTTP tests with real JWT/membership dependencies."""

from datetime import datetime, timedelta, timezone
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select
from sqlalchemy.exc import OperationalError

from app.core.security import create_access_token
from app.db.models import Clinic, ClinicMembership, MembershipRole, MembershipRoleValue, Patient, User
from app.db.session import get_db
from app.main import app


PUBLIC_FIELDS = {"id", "first_name", "last_name", "date_of_birth", "phone", "email",
                 "created_at", "updated_at"}
PAYLOAD = {"first_name": "Synthetic", "last_name": "Patient", "amka": "01234567890",
           "phone": "+44 123", "email": "synthetic@example.com", "date_of_birth": "2000-01-01"}


@pytest.fixture
def data(db_session):
    user = User(email="patient-staff@example.invalid", full_name="Synthetic Staff",
                hashed_password="synthetic-unused", is_active=True)
    clinics = [Clinic(name="Synthetic A"), Clinic(name="Synthetic B")]
    db_session.add_all([user, *clinics])
    db_session.flush()
    memberships = [ClinicMembership(user_id=user.id, clinic_id=c.id) for c in clinics]
    db_session.add_all(memberships)
    db_session.flush()
    role = MembershipRole(membership_id=memberships[0].id, role=MembershipRoleValue.OWNER)
    db_session.add(role)
    # Release fixture setup savepoint: service rollback must not remove setup.
    db_session.commit()
    return user, clinics, memberships, role


@pytest.fixture
def client(db_session):
    previous = app.dependency_overrides.copy()

    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as http:
            yield http
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


def headers(user):
    return {"Authorization": f"Bearer {create_access_token({'sub': str(user.id)})}"}


def path(clinic, patient_id=None):
    base = f"/clinics/{clinic.id}/patients"
    return base if patient_id is None else f"{base}/{patient_id}"


def request(client, method, clinic, auth):
    if method == "post":
        return client.post(path(clinic), json=PAYLOAD, headers=auth)
    return client.get(path(clinic, 2147483647), headers=auth)


def assert_private(response, *values):
    for value in values:
        assert str(value) not in response.text
    assert "SELECT " not in response.text
    assert "INSERT " not in response.text
    assert "Traceback" not in response.text


@pytest.mark.parametrize("role_value", list(MembershipRoleValue))
def test_create_and_detail_allowlist_and_ownership(client, data, db_session, role_value):
    user, clinics, _, role = data
    role.role = role_value
    db_session.commit()
    auth = headers(user)
    response = client.post(path(clinics[0]), json=PAYLOAD, headers=auth)
    assert response.status_code == 201
    body = response.json()
    assert set(body) == PUBLIC_FIELDS
    assert body["date_of_birth"] == "2000-01-01"
    assert body["created_at"] and body["updated_at"]
    assert_private(response, PAYLOAD["amka"])
    stored = db_session.scalar(select(Patient).where(Patient.id == body["id"],
                                                   Patient.clinic_id == clinics[0].id))
    assert stored.amka == PAYLOAD["amka"]
    detail = client.get(path(clinics[0], stored.id), headers=auth)
    assert detail.status_code == 200
    assert detail.json() == body
    assert_private(detail, PAYLOAD["amka"])


@pytest.mark.parametrize("method", ["post", "get"])
@pytest.mark.parametrize("credential", ["missing", "invalid", "expired", "absent_user"])
def test_authentication(client, data, method, credential):
    user, clinics, _, _ = data
    auth = {}
    if credential == "invalid":
        auth = {"Authorization": "Bearer invalid-jwt"}
    elif credential == "expired":
        auth = {"Authorization": "Bearer " + create_access_token(
            {"sub": str(user.id)}, expires_delta=timedelta(minutes=-1))}
    elif credential == "absent_user":
        auth = {"Authorization": "Bearer " + create_access_token({"sub": "2147483647"})}
    response = request(client, method, clinics[0], auth)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize("method", ["post", "get"])
def test_inactive_and_removed_authorization(client, data, db_session, method):
    user, clinics, memberships, role = data
    auth = headers(user)
    user.is_active = False
    db_session.commit()
    assert request(client, method, clinics[0], auth).json() == {"detail": "Inactive user"}
    assert request(client, method, clinics[0], auth).status_code == 403
    user.is_active = True
    db_session.commit()
    # The same JWT observes role and membership removal immediately.
    assert request(client, method, clinics[0], auth).status_code == (201 if method == "post" else 404)
    db_session.delete(role)
    db_session.commit()
    response = request(client, method, clinics[0], auth)
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
    db_session.delete(memberships[0])
    db_session.commit()
    user.is_superuser = True
    db_session.commit()
    response = request(client, method, clinics[0], auth)
    assert response.status_code == 404
    assert response.json() == {"detail": "Clinic not found or inaccessible"}


@pytest.mark.parametrize("method", ["post", "get"])
def test_other_clinic_membership_is_not_authority(client, data, db_session, method):
    user, clinics, memberships, _ = data
    db_session.delete(memberships[1])
    user.is_superuser = True
    db_session.commit()
    response = request(client, method, clinics[1], headers(user))
    assert response.status_code == 404
    assert response.json() == {"detail": "Clinic not found or inaccessible"}


def test_cross_clinic_independent_records_and_identical_404(client, data, db_session):
    user, clinics, memberships, _ = data
    db_session.add(MembershipRole(membership_id=memberships[1].id, role=MembershipRoleValue.SECRETARY))
    db_session.commit()
    auth = headers(user)
    a = client.post(path(clinics[0]), json=PAYLOAD, headers=auth)
    b = client.post(path(clinics[1]), json=PAYLOAD, headers=auth)
    assert a.status_code == b.status_code == 201
    assert a.json()["id"] != b.json()["id"]
    foreign = client.get(path(clinics[0], b.json()["id"]), headers=auth)
    missing = client.get(path(clinics[0], 2147483647), headers=auth)
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json() == {"detail": "Patient not found or inaccessible"}
    assert client.get(path(clinics[1], b.json()["id"]), headers=auth).status_code == 200


def test_duplicate_rollback_and_subsequent_success(client, data, db_session, caplog):
    user, clinics, _, _ = data
    auth = headers(user)
    first = client.post(path(clinics[0]), json=PAYLOAD, headers=auth)
    assert first.status_code == 201
    duplicate = client.post(path(clinics[0]), json={**PAYLOAD, "first_name": "SecretDuplicate"}, headers=auth)
    assert duplicate.status_code == 409
    assert duplicate.json() == {"detail": "Patient data conflict"}
    assert_private(duplicate, PAYLOAD["amka"], PAYLOAD["email"], "SecretDuplicate", "uq_patients")
    assert client.get(path(clinics[0], first.json()["id"]), headers=auth).json() == first.json()
    assert db_session.scalar(select(func.count()).select_from(Patient).where(
        Patient.clinic_id == clinics[0].id)) == 1
    assert client.post(path(clinics[0]), json={"first_name": "Next", "last_name": "Synthetic"}, headers=auth).status_code == 201
    assert PAYLOAD["amka"] not in caplog.text
    assert PAYLOAD["email"] not in caplog.text
    assert "SecretDuplicate" not in caplog.text


@pytest.mark.parametrize("changes", [
    {"first_name": " \t\n\r\f\vName \t", "last_name": " Family ", "phone": " +44 123 "},
    {"first_name": "N" * 100, "last_name": "F" * 100, "phone": "1" * 25},
    {"phone": " \t\n\r\f\v"},
    {"phone": None, "email": None, "amka": None, "date_of_birth": None},
    {"first_name": "\u00a0Name\u00a0", "date_of_birth": datetime.now(timezone.utc).date().isoformat()},
])
def test_valid_normalization(client, data, changes):
    user, clinics, _, _ = data
    response = client.post(path(clinics[0]), json={**PAYLOAD, **changes}, headers=headers(user))
    assert response.status_code == 201
    for field in ("first_name", "last_name", "phone"):
        expected = changes.get(field, PAYLOAD[field])
        if isinstance(expected, str):
            expected = expected.strip(" \t\n\r\f\v")
            if field == "phone" and not expected:
                expected = None
        assert response.json()[field] == expected


INVALID_CHANGES = [
    {"first_name": None}, {"first_name": " \t\n"}, {"last_name": ""},
    {"first_name": "N" * 101}, {"last_name": "F" * 101},
    {"first_name": 123}, {"last_name": True}, {"phone": 123}, {"phone": "1" * 26},
    {"email": "private-invalid-email"}, {"email": "a" * 255 + "@example.com"},
    {"email": " "}, {"email": ""}, {"email": 123},
    {"amka": "1234567890"}, {"amka": "123456789012"}, {"amka": "０１２３４５６７８９０"},
    {"amka": " 01234567890"}, {"amka": "01234567890 "}, {"amka": "0123456789\n"},
    {"amka": ""}, {"amka": 12345678901}, {"amka": True},
    {"date_of_birth": "2999-01-01"}, {"date_of_birth": "2000-01-01T00:00:00"},
    {"date_of_birth": 946684800}, {"date_of_birth": "2000-1-1"}, {"date_of_birth": "2000-02-30"},
    *[{field: "attacker-sensitive-value"} for field in (
        "id", "clinic_id", "created_at", "updated_at", "actor_id", "clinical_notes", "secret-field-name")],
]


@pytest.mark.parametrize("changes", INVALID_CHANGES)
def test_invalid_payload_is_private(client, data, changes, caplog):
    user, clinics, _, _ = data
    response = client.post(path(clinics[0]), json={**PAYLOAD, **changes}, headers=headers(user))
    assert response.status_code == 422
    assert response.json() == {"detail": [{"loc": ["request"], "type": "invalid_patient_request",
                                          "msg": "Invalid patient request"}]}
    assert_private(response, PAYLOAD["amka"], PAYLOAD["email"], "attacker-sensitive-value", "secret-field-name")
    assert PAYLOAD["amka"] not in caplog.text
    assert PAYLOAD["email"] not in caplog.text


@pytest.mark.parametrize("payload", [{}, {"first_name": "SensitiveName"}, [], None, "secret-body"])
def test_missing_names_and_wrong_body(client, data, payload):
    user, clinics, _, _ = data
    response = client.post(path(clinics[0]), content=json.dumps(payload),
                           headers={**headers(user), "Content-Type": "application/json"})
    assert response.status_code == 422
    assert_private(response, "SensitiveName", "secret-body")


def test_malformed_json_and_path_privacy(client, data):
    user, clinics, _, _ = data
    auth = headers(user)
    response = client.post(path(clinics[0]), content='{"amka":"SensitiveMalformed",',
                           headers={**auth, "Content-Type": "application/json"})
    assert response.status_code == 422
    assert_private(response, "SensitiveMalformed")
    for identifier in ("secret-path-value", "0", "-1", "2147483648"):
        response = client.get(path(clinics[0], identifier), headers=auth)
        assert response.status_code == 422
        assert_private(response, "secret-path-value")
    response = client.post("/clinics/secret-clinic-value/patients", json=PAYLOAD, headers=auth)
    assert response.status_code == 422
    assert_private(response, "secret-clinic-value", PAYLOAD["amka"])


@pytest.mark.parametrize("stage", ["flush", "commit"])
def test_write_failure_rolls_back_and_remains_usable(client, data, db_session, monkeypatch, caplog, stage):
    user, clinics, _, _ = data
    auth = headers(user)
    url = path(clinics[0])
    failure = OperationalError("INSERT sensitive-sql", {"amka": PAYLOAD["amka"]}, Exception("sensitive-db"))
    with monkeypatch.context() as patch:
        def fail(*args, **kwargs):
            raise failure
        patch.setattr(db_session, stage, fail)
        response = client.post(url, json=PAYLOAD, headers=auth)
    assert response.status_code == 500
    assert response.json() == {"detail": "Patient operation failed"}
    assert_private(response, PAYLOAD["amka"], "sensitive-db", "sensitive-sql")
    assert db_session.scalar(select(func.count()).select_from(Patient)) == 0
    assert client.post(url, json=PAYLOAD, headers=auth).status_code == 201
    assert PAYLOAD["amka"] not in caplog.text
    assert "sensitive-db" not in caplog.text


def test_only_approved_patient_routes_are_registered():
    routes = app.openapi()["paths"]
    assert set(routes["/clinics/{clinic_id}/patients"]) == {"post", "get"}
    assert set(routes["/clinics/{clinic_id}/patients/{patient_id}"]) == {"get"}


@pytest.mark.parametrize("forced,status,detail", [
    ({"first_name": ""}, 422, "Invalid patient data"),
    ({"last_name": None}, 422, "Invalid patient data"),
    ({"clinic_id": 2147483647}, 404, "Clinic not found or inaccessible"),
])
def test_real_database_constraint_error_mapping(client, data, db_session, forced, status, detail):
    user, clinics, _, _ = data
    auth = headers(user)
    url = path(clinics[0])

    def force_storage_violation(session, context, instances):
        # Fault injection only after real auth/input validation. PostgreSQL
        # produces the actual SQLSTATE and named constraint diagnostics.
        for instance in session.new:
            if isinstance(instance, Patient):
                for field, value in forced.items():
                    setattr(instance, field, value)

    event.listen(db_session, "before_flush", force_storage_violation)
    try:
        response = client.post(url, json=PAYLOAD, headers=auth)
    finally:
        event.remove(db_session, "before_flush", force_storage_violation)
    assert response.status_code == status
    assert response.json() == {"detail": detail}
    assert_private(response, PAYLOAD["amka"], PAYLOAD["email"])
    assert db_session.scalar(select(func.count()).select_from(Patient)) == 0
    assert client.post(url, json=PAYLOAD, headers=auth).status_code == 201


def test_unknown_unique_constraint_is_not_amka_conflict(client, data, db_session):
    user, clinics, _, _ = data
    auth = headers(user)
    url = path(clinics[0])
    first = client.post(url, json=PAYLOAD, headers=auth)
    assert first.status_code == 201

    def force_duplicate_primary_key(session, context, instances):
        for instance in session.new:
            if isinstance(instance, Patient):
                instance.id = first.json()["id"]

    event.listen(db_session, "before_flush", force_duplicate_primary_key)
    try:
        response = client.post(url, json={"first_name": "Another", "last_name": "Synthetic"}, headers=auth)
    finally:
        event.remove(db_session, "before_flush", force_duplicate_primary_key)
    assert response.status_code == 500
    assert response.json() == {"detail": "Patient operation failed"}
    assert client.get(path(clinics[0], first.json()["id"]), headers=auth).json() == first.json()


@pytest.mark.parametrize("method", ["post", "get"])
def test_response_validation_failure_is_private(client, data, db_session, monkeypatch, caplog, method):
    from app.schemas.patient import PatientRead

    user, clinics, _, _ = data
    auth = headers(user)
    url = path(clinics[0])
    created = client.post(url, json=PAYLOAD, headers=auth)
    assert created.status_code == 201
    original_validate = PatientRead.model_validate

    def invalid_output(*args, **kwargs):
        # Includes AMKA in the raw Pydantic error input; it must never escape.
        return original_validate({"id": {"amka": PAYLOAD["amka"]}})

    with monkeypatch.context() as patch:
        patch.setattr(PatientRead, "model_validate", invalid_output)
        if method == "post":
            response = client.post(url, json={**PAYLOAD, "amka": None}, headers=auth)
        else:
            response = client.get(path(clinics[0], created.json()["id"]), headers=auth)
    assert response.status_code == 500
    assert response.json() == {"detail": "Patient operation failed"}
    assert_private(response, PAYLOAD["amka"], PAYLOAD["email"])
    assert PAYLOAD["amka"] not in caplog.text
    assert db_session.scalar(select(func.count()).select_from(Patient)) == 1
    assert client.get(path(clinics[0], created.json()["id"]), headers=auth).status_code == 200
