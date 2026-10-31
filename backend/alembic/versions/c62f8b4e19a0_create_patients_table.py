"""Create clinic-owned patients.

Revision ID: c62f8b4e19a0
Revises: a807f733a8e3
"""

from alembic import op
import sqlalchemy as sa


revision = "c62f8b4e19a0"
down_revision = "a807f733a8e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Frozen ASCII trim set: space, HT, LF, CR, FF, VT. Not Unicode strip().
    whitespace = "chr(32) || chr(9) || chr(10) || chr(13) || chr(12) || chr(11)"
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("clinic_id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("phone", sa.String(25), nullable=True),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("amka", sa.String(11), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["clinic_id"], ["clinics.id"], name="fk_patients_clinic_id_clinics",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("clinic_id", "amka", name="uq_patients_clinic_id_amka"),
        sa.CheckConstraint(
            "amka IS NULL OR (char_length(amka) = 11 AND amka !~ '[^0-9]')",
            name="ck_patients_amka_ascii_digits",
        ),
        sa.CheckConstraint("first_name <> ''", name="ck_patients_first_name_nonblank"),
        sa.CheckConstraint(f"first_name = btrim(first_name, {whitespace})",
                           name="ck_patients_first_name_trimmed"),
        sa.CheckConstraint("last_name <> ''", name="ck_patients_last_name_nonblank"),
        sa.CheckConstraint(f"last_name = btrim(last_name, {whitespace})",
                           name="ck_patients_last_name_trimmed"),
        sa.CheckConstraint("phone IS NULL OR phone <> ''", name="ck_patients_phone_nonblank"),
        sa.CheckConstraint(f"phone IS NULL OR phone = btrim(phone, {whitespace})",
                           name="ck_patients_phone_trimmed"),
    )
    op.create_index("ix_patients_clinic_id_id", "patients", ["clinic_id", "id"])


def downgrade() -> None:
    op.drop_index("ix_patients_clinic_id_id", table_name="patients")
    op.drop_table("patients")
