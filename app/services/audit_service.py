import csv
import json
import io
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.audit import Audit
from app.schemas.audit import AuditCreate

def log_audit(db: Session, user_id: str, action: str, username: str = None):
    """
    Registra una nueva acción de auditoría en la base de datos local.
    """
    audit_entry = Audit(user_id=user_id, action=action, username=username)
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry

def get_audits(db: Session, skip: int = 0, limit: int = 100):
    """
    Recupera una lista de auditorías paginada.
    """
    return db.query(Audit).order_by(Audit.timestamp.desc()).offset(skip).limit(limit).all()

def export_audits_csv(db: Session):
    """
    Exporta todas las auditorías a formato CSV.
    """
    audits = db.query(Audit).all()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir cabecera
    writer.writerow(['id', 'user_id', 'username', 'action', 'timestamp'])
    
    # Escribir filas
    for audit in audits:
        writer.writerow([audit.id, audit.user_id, audit.username, audit.action, audit.timestamp.isoformat()])
        
    return output.getvalue()

def export_audits_json(db: Session):
    """
    Exporta todas las auditorías a formato JSON.
    """
    audits = db.query(Audit).all()
    data = []
    for audit in audits:
        data.append({
            'id': audit.id,
            'user_id': audit.user_id,
            'username': audit.username,
            'action': audit.action,
            'timestamp': audit.timestamp.isoformat()
        })
    return json.dumps(data, indent=4)

def import_audits_csv(db: Session, file_content: str):
    """
    Importa auditorías desde un contenido CSV string.
    """
    stream = io.StringIO(file_content)
    reader = csv.DictReader(stream)
    
    count = 0
    for row in reader:
        # Intentamos parsear la fecha, si falla usamos la actual o dejamos que falle según requerimiento
        # El formato esperado es ISO 8601 que usamos en el export
        try:
            timestamp = datetime.fromisoformat(row['timestamp'])
        except ValueError:
            timestamp = datetime.now()

        # Creamos el objeto Audit. El ID lo ignoramos para que se autogenere o lo usamos si queremos restaurar backup exacto.
        # Si queremos restaurar backup exacto, deberíamos chequear si ya existe el ID.
        # Para simplificar, asumiremos que importamos como nuevas entradas o respetamos IDs si no existen.
        # Aquí vamos a crear nuevas entradas para evitar conflictos de Primary Key, 
        # pero mantenemos los datos históricos.
        
        audit = Audit(
            user_id=row['user_id'],
            username=row['username'],
            action=row['action'],
            timestamp=timestamp
        )
        db.add(audit)
        count += 1
    
    db.commit()
    return count

def import_audits_json(db: Session, json_content: str):
    """
    Importa auditorías desde un contenido JSON string.
    """
    data = json.loads(json_content)
    count = 0
    
    if isinstance(data, list):
        for item in data:
            try:
                timestamp = datetime.fromisoformat(item['timestamp'])
            except ValueError:
                timestamp = datetime.now()
                
            audit = Audit(
                user_id=item['user_id'],
                username=item.get('username'),
                action=item['action'],
                timestamp=timestamp
            )
            db.add(audit)
            count += 1
            
    db.commit()
    return count
