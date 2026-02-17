from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db_sql import get_db_sql
from app.schemas.audit import Audit, AuditCreate
from app.services import audit_service
from fastapi.responses import Response

router = APIRouter(
    prefix="/audits",
    tags=["audits"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[Audit])
def read_audits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_sql)):
    """
    Obtiene lista de auditorías paginada.
    """
    audits = audit_service.get_audits(db, skip=skip, limit=limit)
    return audits

@router.post("/", response_model=Audit)
def create_audit_manual(audit: AuditCreate, db: Session = Depends(get_db_sql)):
    """
    Endpoint para probar la creación manual de logs (útil para debug).
    """
    return audit_service.log_audit(db, user_id=audit.user_id, action=audit.action, username=audit.username)

@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db_sql)):
    """
    Descarga todas las auditorías en formato CSV.
    """
    csv_content = audit_service.export_audits_csv(db)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audits.csv"}
    )

@router.get("/export/json")
def export_json(db: Session = Depends(get_db_sql)):
    """
    Descarga todas las auditorías en formato JSON.
    """
    json_content = audit_service.export_audits_json(db)
    return Response(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=audits.json"}
    )

@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db_sql)):
    """
    Importa auditorías desde un archivo CSV.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser CSV")
    
    content = await file.read()
    # Decodificar bytes a string
    text_content = content.decode('utf-8')
    
    count = audit_service.import_audits_csv(db, text_content)
    return {"message": f"Se han importado {count} registros correctamente via CSV."}

@router.post("/import/json")
async def import_json(file: UploadFile = File(...), db: Session = Depends(get_db_sql)):
    """
    Importa auditorías desde un archivo JSON.
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="El archivo debe ser JSON")
    
    content = await file.read()
    text_content = content.decode('utf-8')
    
    try:
        count = audit_service.import_audits_json(db, text_content)
        return {"message": f"Se han importado {count} registros correctamente via JSON."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar JSON: {str(e)}")
