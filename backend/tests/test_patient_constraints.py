"""PostgreSQL storage invariants, independently of future API validators."""

from datetime import date, datetime, timezone

import pytest
from sqlalchemy import Date, DateTime, Integer, String, Text, inspect, select, text
from sqlalchemy.exc import DataError, IntegrityError

from app.db.models import Clinic, Patient


@pytest.fixture
def clinic(db_session):
    clinic = Clinic(name="Synthetic Patient Clinic")
    db_session.add(clinic)
    db_session.flush()
    return clinic


def insert_patient(db_session, clinic_id, **changes):
    values = dict(clinic_id=clinic_id, first_name="Synthetic", last_name="Patient")
    values.update(changes)
    # Parameterized Core insert bypasses ORM/application normalization.
    return db_session.execute(
        Patient.__table__.insert().values(**values).returning(Patient.id)
    ).scalar_one()


def assert_rejected(db_session, operation, state, constraint=None):
    with pytest.raises((IntegrityError, DataError)) as error:
        with db_session.begin_nested():
            operation()
    assert error.value.orig.pgcode == state
    if constraint:
        assert error.value.orig.diag.constraint_name == constraint
    # Failed writes must not poison the outer fixture transaction.
    assert db_session.scalar(text("SELECT 1")) == 1


def test_minimal_patient_defaults_and_relationships(db_session, clinic):
    patient = Patient(clinic=clinic, first_name="Synthetic", last_name="Patient")
    db_session.add(patient)
    db_session.flush()
    db_session.refresh(patient)
    assert patient.id > 0
    assert patient.clinic is clinic
    assert patient in clinic.patients
    assert patient.created_at.utcoffset() is not None
    assert patient.updated_at == patient.created_at
    for field in ("date_of_birth", "phone", "email", "amka"):
        assert getattr(patient, field) is None


@pytest.mark.parametrize("field", ["clinic_id", "first_name", "last_name", "created_at", "updated_at"])
def test_required_fields_reject_null(db_session, clinic, field):
    assert_rejected(db_session, lambda: insert_patient(
        db_session, clinic.id, **{field: None}
    ) if field != "clinic_id" else insert_patient(db_session, None), "23502")


@pytest.mark.parametrize("field,limit", [("first_name", 100), ("last_name", 100), ("phone", 25)])
def test_string_length_boundaries(db_session, clinic, field, limit):
    patient_id = insert_patient(db_session, clinic.id, **{field: "X" * limit})
    assert getattr(db_session.get(Patient, patient_id), field) == "X" * limit
    assert_rejected(db_session, lambda: insert_patient(
        db_session, clinic.id, **{field: "X" * (limit + 1)}
    ), "22001")


@pytest.mark.parametrize("field", ["first_name", "last_name", "phone"])
@pytest.mark.parametrize("value", ["", " ", "\t", "\n", "\r", "\f", "\v", " X", "X ", "\tX", "X\n"])
def test_blank_and_untrimmed_values_rejected(db_session, clinic, field, value):
    suffix = "nonblank" if value == "" else "trimmed"
    assert_rejected(db_session, lambda: insert_patient(
        db_session, clinic.id, **{field: value}
    ), "23514", f"ck_patients_{field}_{suffix}")


def test_explicit_ascii_policy_does_not_strip_unicode(db_session, clinic):
    # NBSP is intentionally outside the six-character ASCII trim set.
    patient_id = insert_patient(db_session, clinic.id, first_name="\u00a0Synthetic\u00a0")
    assert db_session.get(Patient, patient_id).first_name == "\u00a0Synthetic\u00a0"


def test_invalid_clinic_fk(db_session):
    assert db_session.get(Clinic, -1) is None
    assert_rejected(db_session, lambda: insert_patient(db_session, -1),
                    "23503", "fk_patients_clinic_id_clinics")


@pytest.mark.parametrize("orm_delete", [False, True])
def test_clinic_delete_restricted(db_session, clinic, orm_delete):
    patient_id = insert_patient(db_session, clinic.id)
    # Load collection too: ORM must not null FKs or cascade even when loaded.
    assert len(clinic.patients) == 1

    def delete_clinic():
        if orm_delete:
            db_session.delete(clinic)
            db_session.flush()
        else:
            db_session.execute(text("DELETE FROM clinics WHERE id = :id"), {"id": clinic.id})

    assert_rejected(db_session, delete_clinic, "23503", "fk_patients_clinic_id_clinics")
    assert db_session.get(Patient, patient_id).clinic_id == clinic.id
    db_session.refresh(clinic)


def test_valid_optional_fields_and_leading_zero(db_session, clinic):
    patient_id = insert_patient(db_session, clinic.id, amka="01234567890",
                                phone="+44 123 456", email="synthetic@example.invalid",
                                date_of_birth=date(2000, 1, 1))
    patient = db_session.get(Patient, patient_id)
    assert patient.amka == "01234567890"
    assert patient.date_of_birth == date(2000, 1, 1)
    assert patient.phone == "+44 123 456"


@pytest.mark.parametrize("amka,state", [
    ("", "23514"), ("1234567890", "23514"), ("123456789012", "22001"),
    ("０１２３４５６７８９０", "23514"), ("0123456789X", "23514"),
    (" 1234567890", "23514"), ("0123456789 ", "23514"),
    ("01234\t67890", "23514"), ("0123456789\n", "23514"),
])
def test_invalid_amka(db_session, clinic, amka, state):
    assert_rejected(db_session, lambda: insert_patient(db_session, clinic.id, amka=amka),
                    state, "ck_patients_amka_ascii_digits" if state == "23514" else None)


def test_nullable_and_clinic_local_amka_uniqueness(db_session, clinic):
    first = insert_patient(db_session, clinic.id)
    second = insert_patient(db_session, clinic.id)
    assert first != second
    original = insert_patient(db_session, clinic.id, amka="01234567890")
    assert_rejected(db_session, lambda: insert_patient(
        db_session, clinic.id, amka="01234567890"
    ), "23505", "uq_patients_clinic_id_amka")
    other = Clinic(name="Synthetic Other Clinic")
    db_session.add(other)
    db_session.flush()
    other_patient = insert_patient(db_session, other.id, amka="01234567890")
    assert other_patient != original


def test_failed_update_rolls_back_all_fields(db_session, clinic):
    insert_patient(db_session, clinic.id, amka="01234567890")
    patient_id = insert_patient(db_session, clinic.id, amka="01234567891")

    def invalid_update():
        db_session.execute(text(
            "UPDATE patients SET amka = :amka, first_name = :name WHERE id = :id"
        ), {"amka": "01234567890", "name": "Changed", "id": patient_id})

    assert_rejected(db_session, invalid_update, "23505", "uq_patients_clinic_id_amka")
    patient = db_session.get(Patient, patient_id)
    assert patient.amka == "01234567891"
    assert patient.first_name == "Synthetic"
    insert_patient(db_session, clinic.id)  # Outer transaction still accepts writes.


def test_sqlalchemy_updated_at_and_direct_sql_limit(db_session, clinic):
    # now() is transaction-scoped: use a past sentinel, not sleep or a second commit.
    sentinel = datetime(2000, 1, 1, tzinfo=timezone.utc)
    patient_id = insert_patient(db_session, clinic.id, updated_at=sentinel)
    patient = db_session.get(Patient, patient_id)
    created_at = patient.created_at
    db_session.execute(text("UPDATE patients SET first_name = :name WHERE id = :id"),
                       {"name": "Raw", "id": patient_id})
    db_session.refresh(patient)
    assert patient.updated_at == sentinel  # No trigger.
    patient.first_name = "ORM"
    db_session.flush()
    db_session.refresh(patient)
    assert patient.updated_at > sentinel
    assert patient.updated_at.utcoffset() is not None
    assert patient.created_at == created_at


def test_patient_schema(db_session):
    schema = inspect(db_session.connection())
    columns = {column["name"]: column for column in schema.get_columns("patients")}
    assert set(columns) == {"id", "clinic_id", "first_name", "last_name", "date_of_birth",
                            "phone", "email", "amka", "created_at", "updated_at"}
    for field in ("id", "clinic_id", "first_name", "last_name", "created_at", "updated_at"):
        assert columns[field]["nullable"] is False
    for field in ("date_of_birth", "phone", "email", "amka"):
        assert columns[field]["nullable"] is True
    assert isinstance(columns["id"]["type"], Integer)
    assert columns["id"]["default"] is not None
    assert isinstance(columns["clinic_id"]["type"], Integer)
    for field, length in (("first_name", 100), ("last_name", 100), ("phone", 25), ("amka", 11)):
        assert isinstance(columns[field]["type"], String)
        assert columns[field]["type"].length == length
    assert isinstance(columns["email"]["type"], Text)
    assert isinstance(columns["date_of_birth"]["type"], Date)
    for field in ("created_at", "updated_at"):
        assert isinstance(columns[field]["type"], DateTime)
        assert columns[field]["type"].timezone is True
        assert "now()" in columns[field]["default"]
    assert schema.get_pk_constraint("patients")["constrained_columns"] == ["id"]
    foreign_keys = schema.get_foreign_keys("patients")
    assert len(foreign_keys) == 1
    fk = foreign_keys[0]
    assert fk["name"] == "fk_patients_clinic_id_clinics"
    assert fk["constrained_columns"] == ["clinic_id"]
    assert fk["referred_table"] == "clinics"
    assert fk["referred_columns"] == ["id"]
    assert fk["options"]["ondelete"] == "RESTRICT"
    uniques = schema.get_unique_constraints("patients")
    assert [(u["name"], u["column_names"]) for u in uniques] == [
        ("uq_patients_clinic_id_amka", ["clinic_id", "amka"])
    ]
    assert {c["name"] for c in schema.get_check_constraints("patients")} == {
        "ck_patients_amka_ascii_digits", "ck_patients_first_name_nonblank",
        "ck_patients_first_name_trimmed", "ck_patients_last_name_nonblank",
        "ck_patients_last_name_trimmed", "ck_patients_phone_nonblank",
        "ck_patients_phone_trimmed",
    }
    indexes = schema.get_indexes("patients")
    explicit = [i for i in indexes if not i.get("duplicates_constraint")]
    assert [(i["name"], i["column_names"], i["unique"]) for i in explicit] == [
        ("ix_patients_clinic_id_id", ["clinic_id", "id"], False)
    ]
    assert "delete" not in inspect(Clinic).relationships.patients.cascade
    assert "delete-orphan" not in inspect(Clinic).relationships.patients.cascade
    assert db_session.scalars(select(Patient)).all() == []
