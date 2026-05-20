from fastapi import FastAPI, Depends, HTTPException, Body, Header
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import pandas as pd
import random
import string

from database import SessionLocal, engine
from models import Base, Guest

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dase de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Admin login
ADMIN_USER = "GLYAREJAVI"
ADMIN_PASS = "GLYAREJAVI/%"

@app.post("/admin/login")
def login(data: dict = Body(...)):
    username = data.get("username")
    password = data.get("password")

    if username == ADMIN_USER and password == ADMIN_PASS:
        return {"token": "admin-token"}

    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

# auth admin
def verify_admin(token: str = Header(...)):
    if token != "admin-token":
        raise HTTPException(status_code=401, detail="No autorizado")

# generar código
def generate_code(length=6):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))

# crear invitado
@app.post("/admin/create_guest")
def create_guest(
    data: dict,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin)
):
    name = data.get("name")
    guests_allowed = data.get("guests_allowed")

    if not name or not guests_allowed:
        raise HTTPException(status_code=400, detail="Datos incompletos")

    code = generate_code()

    # evitar código duplicado
    while db.query(Guest).filter(Guest.code == code).first():
        code = generate_code()

    new_guest = Guest(
        name=name,
        code=code,
        guests_allowed=guests_allowed,
        guests_confirmed=0,
        guest_names=""
    )

    db.add(new_guest)
    db.commit()

    return {
        "message": "Invitado creado",
        "code": code
    }

# get invitado
@app.get("/guest/{code}")
def get_guest(code: str, db: Session = Depends(get_db)):
    guest = db.query(Guest).filter(Guest.code == code).first()

    if not guest:
        raise HTTPException(status_code=404, detail="Invitado no encontrado")

    return {
        "name": guest.name,
        "code": guest.code,
        "guests_allowed": guest.guests_allowed,
        "guests_confirmed": guest.guests_confirmed,
        "guest_names": guest.guest_names
    }

# Confirmar asistencia
@app.post("/confirm")
def confirm_guest(data: dict, db: Session = Depends(get_db)):

    guest = db.query(Guest).filter(Guest.code == data["code"]).first()

    if not guest:
        raise HTTPException(status_code=404, detail="Invitado no encontrado")

    # Bloqueo si ya confirmó
    if guest.guests_confirmed > 0:
        raise HTTPException(
            status_code=400,
            detail="Este invitado ya confirmó asistencia"
        )

    names = data.get("names", [])

    if len(names) > guest.guests_allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Solo puedes registrar {guest.guests_allowed} personas"
        )

    guest.guests_confirmed = len(names)
    guest.guest_names = ", ".join(names)

    db.commit()

    return {"message": "Confirmación guardada"}

# admin listar invitados
@app.get("/admin/guests")
def get_all_guests(
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin)
):
    return db.query(Guest).all()

# admin exportar excel
@app.get("/admin/export")
def export_excel(
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin)
):

    guests = db.query(Guest).all()

    data = []

    for g in guests:
        data.append({
            "Nombre": g.name,
            "Código": g.code,
            "Asignados": g.guests_allowed,
            "Confirmados": g.guests_confirmed,
            "Invitados": g.guest_names
        })

    df = pd.DataFrame(data)

    file_path = "invitados.xlsx"
    df.to_excel(file_path, index=False)

    return FileResponse(file_path, filename="invitados.xlsx")

@app.delete("/admin/delete/{id}")
def delete_guest(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin)
):
    guest = db.query(Guest).filter(Guest.id == id).first()

    if not guest:
        raise HTTPException(status_code=404, detail="No encontrado")

    db.delete(guest)
    db.commit()

    return {"message": "Eliminado"}
