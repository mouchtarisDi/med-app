"""Central staff permission policy; callers supply roles from one membership."""

from collections.abc import Iterable, Mapping
from enum import Enum
from types import MappingProxyType

from app.db.models.membership_role import MembershipRoleValue


class Permission(str, Enum):
    PATIENTS_READ = "patients.read"
    PATIENTS_CREATE = "patients.create"
    PATIENTS_UPDATE_BASIC = "patients.update_basic"
    PATIENTS_DELETE = "patients.delete"
    MEDICAL_RECORDS_READ = "medical_records.read"
    MEDICAL_RECORDS_WRITE = "medical_records.write"
    APPOINTMENTS_READ = "appointments.read"
    APPOINTMENTS_MANAGE = "appointments.manage"
    PAYMENTS_READ = "payments.read"
    PAYMENTS_MANAGE = "payments.manage"
    CLINIC_MANAGE_MEMBERS = "clinic.manage_members"
    CLINIC_SETTINGS = "clinic.settings"


ROLE_PERMISSIONS: Mapping[MembershipRoleValue, frozenset[Permission]] = MappingProxyType({
    MembershipRoleValue.OWNER: frozenset(Permission),
    MembershipRoleValue.DOCTOR: frozenset({
        Permission.PATIENTS_READ,
        Permission.PATIENTS_CREATE,
        Permission.PATIENTS_UPDATE_BASIC,
        Permission.MEDICAL_RECORDS_READ,
        Permission.MEDICAL_RECORDS_WRITE,
        Permission.APPOINTMENTS_READ,
        Permission.APPOINTMENTS_MANAGE,
    }),
    MembershipRoleValue.SECRETARY: frozenset({
        Permission.PATIENTS_READ,
        Permission.PATIENTS_CREATE,
        Permission.PATIENTS_UPDATE_BASIC,
        Permission.APPOINTMENTS_READ,
        Permission.APPOINTMENTS_MANAGE,
        Permission.PAYMENTS_READ,
        Permission.PAYMENTS_MANAGE,
    }),
})


def get_permissions_for_roles(
    roles: Iterable[MembershipRoleValue],
) -> frozenset[Permission]:
    """Return the additive permissions for the supplied role values."""
    return frozenset(
        permission for role in roles for permission in ROLE_PERMISSIONS[role]
    )
