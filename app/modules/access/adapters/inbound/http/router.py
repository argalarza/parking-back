from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from uuid import UUID

from app.application.errors import NotFoundError, RepositoryError, ValidationError
from app.modules.access.application.use_cases import EnrollFaceUseCase, VerifyAccessUseCase
from app.modules.access.dependencies import (
    get_enroll_face_use_case,
    get_verify_access_use_case,
)


router = APIRouter(prefix="/acceso", tags=["acceso"])


@router.post("/enrolar/{person_id}")
async def enroll_face(
    person_id: UUID,
    file: UploadFile = File(...),
    use_case: EnrollFaceUseCase = Depends(get_enroll_face_use_case),
) -> dict:
    try:
        return use_case.execute(
            person_id=person_id,
            filename=file.filename,
            file_bytes=await file.read(),
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al procesar la imagen.") from exc
    finally:
        await file.close()


@router.post("/verificar")
async def verify_access(
    gate_id: UUID = Form(...),
    file: UploadFile = File(...),
    use_case: VerifyAccessUseCase = Depends(get_verify_access_use_case),
) -> dict:
    try:
        result = use_case.execute(
            gate_id=gate_id,
            filename=file.filename,
            file_bytes=await file.read(),
        )
        payload = {
            "acceso": result.access,
            "mensaje": result.message,
        }
        if result.access:
            payload["persona"] = result.person
            payload["vehiculo"] = result.vehicle
            payload["distancia"] = result.distance
        return payload
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al verificar el acceso con reconocimiento facial.") from exc
    finally:
        await file.close()
