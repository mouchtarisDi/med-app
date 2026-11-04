"""Clinic-scoped Patient operations; callers pass an authorized membership."""

from sqlalchemy import func, or_, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.db.models import ClinicMembership, Patient
from app.schemas.patient import ASCII_WHITESPACE, PatientCreate, PatientList, PatientRead, PatientSummary


class PatientError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


INPUT_CHECKS = frozenset({
    "ck_patients_amka_ascii_digits",
    "ck_patients_first_name_nonblank", "ck_patients_first_name_trimmed",
    "ck_patients_last_name_nonblank", "ck_patients_last_name_trimmed",
    "ck_patients_phone_nonblank", "ck_patients_phone_trimmed",
})


def classify_write_error(error: DBAPIError) -> PatientError:
    original = error.orig
    state = getattr(original, "pgcode", None)
    diagnostic = getattr(original, "diag", None)
    constraint = getattr(diagnostic, "constraint_name", None)
    if state == "23505" and constraint == "uq_patients_clinic_id_amka":
        return PatientError(409, "Patient data conflict")
    if state == "23514" and constraint in INPUT_CHECKS:
        return PatientError(422, "Invalid patient data")
    if state == "23502" and getattr(diagnostic, "table_name", None) == "patients" and getattr(
        diagnostic, "column_name", None
    ) in {"first_name", "last_name"}:
        return PatientError(422, "Invalid patient data")
    if state == "23503" and constraint == "fk_patients_clinic_id_clinics":
        return PatientError(404, "Clinic not found or inaccessible")
    # 22001 has no reliable column/constraint diagnostic: do not guess its source.
    return PatientError(500, "Patient operation failed")


def create_patient(db: Session, membership: ClinicMembership, data: PatientCreate) -> PatientRead:
    patient = Patient(
        clinic_id=membership.clinic_id,
        first_name=data.first_name, last_name=data.last_name,
        phone=data.phone, email=data.email, amka=data.amka,
        date_of_birth=data.date_of_birth,
    )
    try:
        db.add(patient)
        db.flush()
        db.refresh(patient)
        # Materialize the allowlisted DTO before commit expires ORM attributes.
        result = PatientRead.model_validate(patient)
        db.commit()
    except DBAPIError as error:
        db.rollback()
        raise classify_write_error(error) from None
    except Exception:
        db.rollback()
        raise
    return result


def get_patient(db: Session, membership: ClinicMembership, patient_id: int) -> PatientRead:
    patient = db.execute(select(Patient).where(
        Patient.id == patient_id,
        Patient.clinic_id == membership.clinic_id,
    )).scalar_one_or_none()
    if patient is None:
        raise PatientError(404, "Patient not found or inaccessible")
    return PatientRead.model_validate(patient)


def list_patients(
    db: Session, membership: ClinicMembership, q: str | None, limit: int, offset: int,
) -> PatientList:
    predicates = [Patient.clinic_id == membership.clinic_id]
    query = q.strip(ASCII_WHITESPACE) if q is not None else ""
    if query:
        escaped = query.replace("!", "!!").replace("%", "!%").replace("_", "!_")
        pattern = "%" + escaped + "%"
        predicates.append(or_(
            Patient.first_name.ilike(pattern, escape="!"),
            Patient.last_name.ilike(pattern, escape="!"),
            Patient.phone.ilike(pattern, escape="!"),
        ))
    total = db.scalar(select(func.count()).select_from(Patient).where(*predicates))
    # Select only summary columns, without loading sensitive fields/relationships.
    rows = db.execute(select(Patient.id, Patient.first_name, Patient.last_name)
                      .where(*predicates).order_by(Patient.id.asc()).limit(limit).offset(offset))
    return PatientList(
        items=[PatientSummary(id=row.id, first_name=row.first_name, last_name=row.last_name)
               for row in rows],
        total=total, limit=limit, offset=offset,
    )
