"""List/search HTTP coverage against the isolated PostgreSQL fixtures."""

from datetime import timedelta

import pytest
from sqlalchemy import event, select

from app.core.security import create_access_token
from app.db.models import MembershipRole, MembershipRoleValue, Patient
from test_patient_api import client, data, headers, path


@pytest.fixture
def patients(db_session, data):
    _, clinics, memberships, _ = data
    db_session.add(MembershipRole(membership_id=memberships[1].id, role=MembershipRoleValue.SECRETARY))
    values = [
        ("Alice", "Sample", "+44 123", "emailonly@example.com", "01234567890"),
        ("Other", "NeedleFamily", "555", None, None),
        ("Phone", "Sample", "PHONEneedle", None, None),
        ("Percent%Name", "Sample", None, None, None),
        ("Under_score", "Sample", None, None, None),
        ("Bang!Name", "Sample", None, None, None),
        ("Literal!%_Mark", "Sample", None, None, None),
        ("Mary Jane", "Sample", None, None, None),
        ("Mary Other Jane", "Sample", None, None, None),
        ("ΓΙΩΡΓΟΣ", "Sample", None, None, None),
    ]
    records = []
    for clinic in clinics:
        for first, last, phone, email, amka in values:
            patient = Patient(clinic_id=clinic.id, first_name=first, last_name=last,
                              phone=phone, email=email, amka=amka)
            db_session.add(patient)
            records.append(patient)
    db_session.commit()
    return records[:len(values)], records[len(values):]


@pytest.mark.parametrize("role_value", list(MembershipRoleValue))
def test_roles_scoped_list_and_minimal_response(client, data, patients, db_session, role_value):
    user, clinics, _, role = data
    role.role = role_value
    db_session.commit()
    a, b = patients
    for clinic, expected in zip(clinics, (a, b)):
        response = client.get(path(clinic), headers=headers(user))
        assert response.status_code == 200
        body = response.json()
        assert set(body) == {"items", "total", "limit", "offset"}
        assert body["total"] == len(expected)
        assert body["limit"] == 20 and body["offset"] == 0
        assert [row["id"] for row in body["items"]] == [p.id for p in expected]
        assert all(set(row) == {"id", "first_name", "last_name"} for row in body["items"])
        assert "01234567890" not in response.text
        assert "emailonly@example.com" not in response.text
        assert "+44 123" not in response.text


@pytest.mark.parametrize("credential", ["missing", "invalid", "expired"])
def test_list_authentication(client, data, credential):
    user, clinics, _, _ = data
    auth = {}
    if credential == "invalid":
        auth = {"Authorization": "Bearer invalid-jwt"}
    elif credential == "expired":
        auth = {"Authorization": "Bearer " + create_access_token(
            {"sub": str(user.id)}, expires_delta=timedelta(minutes=-1))}
    response = client.get(path(clinics[0]), headers=auth)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_list_current_authorization_and_no_bypass(client, data, db_session):
    user, clinics, memberships, role = data
    auth = headers(user)
    url = path(clinics[0])
    assert client.get(url, headers=auth).status_code == 200
    user.is_active = False
    db_session.commit()
    assert client.get(url, headers=auth).status_code == 403
    user.is_active = True
    user.is_superuser = True
    db_session.delete(role)
    db_session.commit()
    response = client.get(url, headers=auth)
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
    db_session.delete(memberships[0])
    db_session.commit()
    response = client.get(url, headers=auth)
    assert response.status_code == 404
    assert response.json() == {"detail": "Clinic not found or inaccessible"}


@pytest.mark.parametrize("query,index", [
    ("lic", 0), ("needlefamily", 1), ("phoneneedle", 2),
    ("%", 3), ("_score", 4), ("!Name", 5), ("!%_", 6),
    ("mary jane", 7), (" \t\n\r\f\vALICE \t", 0), ("γιωργο", 9),
])
def test_literal_search_is_scoped(client, data, patients, query, index):
    user, clinics, _, _ = data
    a, _ = patients
    response = client.get(path(clinics[0]), params={"q": query}, headers=headers(user))
    assert response.status_code == 200
    expected = [a[index].id]
    # A bare literal percent is also present in the combined wildcard example.
    if query == "%":
        expected.append(a[6].id)
    assert response.json()["total"] == len(expected)
    assert [p["id"] for p in response.json()["items"]] == expected


@pytest.mark.parametrize("query", ["emailonly", "01234567890", "Mary%Jane", "ΓΙΩΡΓΌΣ", "+44123"])
def test_excluded_fields_and_no_extra_normalization(client, data, patients, query):
    user, clinics, _, _ = data
    response = client.get(path(clinics[0]), params={"q": query}, headers=headers(user))
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


def test_greek_final_sigma_follows_postgresql_collation(client, data, patients, db_session):
    from sqlalchemy import literal

    user, clinics, _, _ = data
    # Do not assume Unicode casefold semantics or change the database collation.
    supported = db_session.scalar(select(literal("ΓΙΩΡΓΟΣ").ilike("%γιωργος%", escape="!")))
    response = client.get(path(clinics[0]), params={"q": "γιωργος"}, headers=headers(user))
    assert response.status_code == 200
    assert response.json()["total"] == int(supported)
    assert [p["id"] for p in response.json()["items"]] == ([patients[0][9].id] if supported else [])


@pytest.mark.parametrize("query", [None, "", " \t\n\r\f\v"])
def test_blank_search_is_unfiltered(client, data, patients, query):
    user, clinics, _, _ = data
    params = {} if query is None else {"q": query}
    response = client.get(path(clinics[0]), params=params, headers=headers(user))
    assert response.status_code == 200
    assert response.json()["total"] == len(patients[0])


@pytest.mark.parametrize("params", [
    {"q": "SensitiveSearch" * 8}, {"q": " " * 101},
    *[{"limit": value} for value in ("0", "-1", "101", "1.5", "secret-limit", "")],
    *[{"offset": value} for value in ("-1", "2147483648", "1.5", "secret-offset", "")],
])
def test_invalid_query_is_sanitized(client, data, params):
    user, clinics, _, _ = data
    response = client.get(path(clinics[0]), params=params, headers=headers(user))
    assert response.status_code == 422
    assert response.json() == {"detail": [{"loc": ["request"], "type": "invalid_patient_request",
                                          "msg": "Invalid patient request"}]}
    assert "SensitiveSearch" not in response.text
    assert "secret-limit" not in response.text
    assert "secret-offset" not in response.text


def test_pagination_and_order(client, data, db_session):
    user, clinics, _, _ = data
    records = [Patient(clinic_id=clinics[0].id, first_name="Synthetic", last_name=f"Entry{i}")
               for i in range(105)]
    db_session.add_all(records)
    db_session.add(Patient(clinic_id=clinics[1].id, first_name="Other", last_name="Tenant"))
    db_session.commit()
    ids = sorted(p.id for p in records)
    auth = headers(user)
    url = path(clinics[0])
    default = client.get(url, headers=auth).json()
    assert default["total"] == 105 and default["limit"] == 20 and default["offset"] == 0
    assert [p["id"] for p in default["items"]] == ids[:20]
    page = client.get(url, params={"limit": 100, "offset": 3}, headers=auth).json()
    assert page["total"] == 105 and page["limit"] == 100 and page["offset"] == 3
    assert [p["id"] for p in page["items"]] == ids[3:103]
    for offset in (105, 2147483647):
        body = client.get(url, params={"offset": offset}, headers=auth).json()
        assert body == {"items": [], "total": 105, "limit": 20, "offset": offset}


def test_matching_total_before_pagination_and_raw_query_boundary(client, data, patients):
    user, clinics, _, _ = data
    auth = headers(user)
    response = client.get(path(clinics[0]), params={"q": "Sample", "limit": 1, "offset": 1}, headers=auth)
    expected = [p for p in patients[0] if p.last_name == "Sample"]
    assert response.status_code == 200
    assert response.json()["total"] == len(expected)
    assert [p["id"] for p in response.json()["items"]] == [expected[1].id]
    assert client.get(path(clinics[0]), params={"q": " " * 100}, headers=auth).status_code == 200


def test_list_does_not_mutate_or_commit_and_uses_two_patient_queries(client, data, patients, db_session, monkeypatch):
    user, clinics, _, _ = data
    auth = headers(user)
    url = path(clinics[0])
    # Include all stored columns and both tenants in before/after comparison.
    snapshot = list(db_session.execute(select(Patient.__table__).order_by(Patient.id)))
    statements = []
    connection = db_session.connection()

    def capture(conn, cursor, statement, parameters, context, executemany):
        if "FROM patients" in statement:
            statements.append(statement)

    def forbidden_commit():
        pytest.fail("A list request must not commit")

    event.listen(connection, "before_cursor_execute", capture)
    try:
        with monkeypatch.context() as patch:
            patch.setattr(db_session, "commit", forbidden_commit)
            response = client.get(url, params={"q": "Sample"}, headers=auth)
    finally:
        event.remove(connection, "before_cursor_execute", capture)
    assert response.status_code == 200
    assert len(statements) == 2
    assert "count(" in statements[0]
    assert "patients.amka" not in statements[1] and "patients.email" not in statements[1]
    assert list(db_session.execute(select(Patient.__table__).order_by(Patient.id))) == snapshot


def test_empty_clinic(client, data):
    user, clinics, _, _ = data
    response = client.get(path(clinics[0]), headers=headers(user))
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 20, "offset": 0}
