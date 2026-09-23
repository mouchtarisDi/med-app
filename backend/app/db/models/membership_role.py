from enum import Enum

from sqlalchemy import Column, Enum as SQLAlchemyEnum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.session import Base


class MembershipRoleValue(str, Enum):
    """Roles that can be assigned to a clinic membership."""

    OWNER = "OWNER"
    DOCTOR = "DOCTOR"
    SECRETARY = "SECRETARY"


class MembershipRole(Base):
    """Assigns one role to a clinic membership."""

    __tablename__ = "membership_roles"
    __table_args__ = (
        UniqueConstraint(
            "membership_id",
            "role",
            name="uq_membership_roles_membership_id_role",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    membership_id = Column(
        Integer,
        ForeignKey("clinic_memberships.id"),
        nullable=False,
    )
    role = Column(
        SQLAlchemyEnum(MembershipRoleValue, name="membership_role"),
        nullable=False,
    )

    membership = relationship("ClinicMembership", back_populates="roles")
