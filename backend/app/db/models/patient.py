"""Clinic-owned demographics; no staff identity or clinical content.

Storage trim policy: ASCII space, HT, LF, CR, FF and VT only (codes
32, 9, 10, 13, 12, 11). Future input validation must use this explicit
set, not unrestricted Unicode str.strip(). Checks reject rather than trim.
"""

from sqlalchemy import (
    CheckConstraint, Column, Date, DateTime, ForeignKey, Index, Integer,
    String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


ASCII_WHITESPACE_SQL = "chr(32) || chr(9) || chr(10) || chr(13) || chr(12) || chr(11)"


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = (
        UniqueConstraint("clinic_id", "amka", name="uq_patients_clinic_id_amka"),
        CheckConstraint(
            "amka IS NULL OR (char_length(amka) = 11 AND amka !~ '[^0-9]')",
            name="ck_patients_amka_ascii_digits",
        ),
        CheckConstraint("first_name <> ''", name="ck_patients_first_name_nonblank"),
        CheckConstraint(
            f"first_name = btrim(first_name, {ASCII_WHITESPACE_SQL})",
            name="ck_patients_first_name_trimmed",
        ),
        CheckConstraint("last_name <> ''", name="ck_patients_last_name_nonblank"),
        CheckConstraint(
            f"last_name = btrim(last_name, {ASCII_WHITESPACE_SQL})",
            name="ck_patients_last_name_trimmed",
        ),
        CheckConstraint(
            "phone IS NULL OR phone <> ''", name="ck_patients_phone_nonblank",
        ),
        CheckConstraint(
            f"phone IS NULL OR phone = btrim(phone, {ASCII_WHITESPACE_SQL})",
            name="ck_patients_phone_trimmed",
        ),
        Index("ix_patients_clinic_id_id", "clinic_id", "id"),
    )

    id = Column(Integer, primary_key=True)
    clinic_id = Column(
        Integer,
        ForeignKey("clinics.id", name="fk_patients_clinic_id_clinics", ondelete="RESTRICT"),
        nullable=False,
    )
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    phone = Column(String(25), nullable=True)
    # Format and the approved 254-character input limit belong to future schemas.
    email = Column(Text, nullable=True)
    amka = Column(String(11), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    # SQLAlchemy update default, not a trigger: direct SQL must set this explicitly.
    updated_at = Column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

    clinic = relationship("Clinic", back_populates="patients")
