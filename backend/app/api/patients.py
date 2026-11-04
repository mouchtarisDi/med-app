"""Staff create/detail routes with route-local error privacy."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.db.models import ClinicMembership
from app.db.session import get_db
from app.schemas.patient import PatientCreate, PatientRead
from app.services.patient import PatientError, create_patient, get_patient


class PatientRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request: Request):
            try:
                return await original(request)
            except RequestValidationError:
                # Covers malformed JSON, body and path errors without reflecting
                # input, ctx, arbitrary field names or exception formatting.
                return JSONResponse(status_code=422, content={"detail": [{
                    "loc": ["request"], "type": "invalid_patient_request",
                    "msg": "Invalid patient request",
                }]})
            except PatientError as error:
                return JSONResponse(status_code=error.status_code, content={"detail": error.detail})
            except HTTPException:
                raise  # Preserve existing authentication/authorization semantics.
            except Exception:
                # Includes dependency DB failures and response validation errors.
                # Never format the exception: it may contain Patient values.
                return JSONResponse(status_code=500, content={"detail": "Patient operation failed"})

        return handler


router = APIRouter(prefix="/clinics/{clinic_id}/patients", tags=["Patients"], route_class=PatientRoute)


@router.post("", response_model=PatientRead, status_code=201)
def post_patient(
    data: PatientCreate,
    membership: Annotated[ClinicMembership, Depends(require_permission(Permission.PATIENTS_CREATE))],
    db: Annotated[Session, Depends(get_db)],
) -> PatientRead:
    return create_patient(db, membership, data)


@router.get("/{patient_id}", response_model=PatientRead)
def read_patient(
    patient_id: Annotated[int, Path(gt=0, le=2147483647)],
    membership: Annotated[ClinicMembership, Depends(require_permission(Permission.PATIENTS_READ))],
    db: Annotated[Session, Depends(get_db)],
) -> PatientRead:
    return get_patient(db, membership, patient_id)
