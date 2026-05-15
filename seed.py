from database import SessionLocal, engine
from models import Base, Guest

# Crear tablas
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# limpiar registros
db.query(Guest).delete()
db.commit()

# crear invitados
guest1 = Guest(
    name="Erick",
    code="ABC123",
    guests_allowed=3,
    guests_confirmed=0,
    guest_names=""
)

guest2 = Guest(
    name="Juan",
    code="XYZ789",
    guests_allowed=2,
    guests_confirmed=0,
    guest_names=""
)

guest3 = Guest(
    name="Maria",
    code="TEST456",
    guests_allowed=4,
    guests_confirmed=0,
    guest_names=""
)

# guardar
db.add_all([guest1, guest2, guest3])
db.commit()

# cerrar conexión
db.close()

