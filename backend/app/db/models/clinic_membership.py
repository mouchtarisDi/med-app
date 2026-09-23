from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class ClinicMembership(Base):
    """Associates a staff user with a clinic tenant."""

    __tablename__ = "clinic_memberships"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "clinic_id",
            name="uq_clinic_memberships_user_id_clinic_id",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="memberships")
    clinic = relationship("Clinic", back_populates="memberships")
    roles = relationship("MembershipRole", back_populates="membership")
