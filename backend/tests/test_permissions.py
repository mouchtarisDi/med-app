import pytest

from app.core.permissions import Permission, get_permissions_for_roles
from app.db.models import MembershipRoleValue


# Independent business-policy expectations, not derived from ROLE_PERMISSIONS.
ALL_PERMISSIONS = frozenset({
    "patients.read", "patients.create", "patients.update_basic", "patients.delete",
    "medical_records.read", "medical_records.write",
    "appointments.read", "appointments.manage", "payments.read", "payments.manage",
    "clinic.manage_members", "clinic.settings",
})
DOCTOR_PERMISSIONS = frozenset({
    "patients.read", "patients.create", "patients.update_basic",
    "medical_records.read", "medical_records.write",
    "appointments.read", "appointments.manage",
})
SECRETARY_PERMISSIONS = frozenset({
    "patients.read", "patients.create", "patients.update_basic",
    "appointments.read", "appointments.manage", "payments.read", "payments.manage",
})
UNION_PERMISSIONS = frozenset({
    "patients.read", "patients.create", "patients.update_basic",
    "medical_records.read", "medical_records.write", "appointments.read",
    "appointments.manage", "payments.read", "payments.manage",
})


def test_permission_catalog_is_exact():
    assert {permission.value for permission in Permission} == ALL_PERMISSIONS
    assert len(Permission) == 12


@pytest.mark.parametrize("role, expected", [
    (MembershipRoleValue.OWNER, ALL_PERMISSIONS),
    (MembershipRoleValue.DOCTOR, DOCTOR_PERMISSIONS),
    (MembershipRoleValue.SECRETARY, SECRETARY_PERMISSIONS),
])
def test_exact_role_permissions(role, expected):
    result = get_permissions_for_roles([role])
    assert isinstance(result, frozenset)
    assert {permission.value for permission in result} == expected


def test_owner_receives_every_declared_permission():
    assert get_permissions_for_roles([MembershipRoleValue.OWNER]) == frozenset(Permission)


def test_multi_role_union_collapses_duplicates_and_excludes_owner_only():
    result = get_permissions_for_roles([
        MembershipRoleValue.DOCTOR, MembershipRoleValue.SECRETARY,
        MembershipRoleValue.DOCTOR,
    ])
    assert {permission.value for permission in result} == UNION_PERMISSIONS
    assert result.isdisjoint({Permission.PATIENTS_DELETE,
                              Permission.CLINIC_MANAGE_MEMBERS, Permission.CLINIC_SETTINGS})


def test_empty_roles_have_no_permissions():
    assert get_permissions_for_roles([]) == frozenset()
