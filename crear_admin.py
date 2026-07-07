from passlib.context import CryptContext
from sqlalchemy import text
from app.infrastructure.database import SessionLocal

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERNAME = "admin"
PASSWORD = "Admin1234"   # cámbiala luego

db = SessionLocal()
db.execute(
    text("""INSERT INTO public.users (username, password_hash, role)
            VALUES (:u, :p, 'admin')
            ON CONFLICT (username) DO NOTHING"""),
    {"u": USERNAME, "p": pwd.hash(PASSWORD)},
)
db.commit()
db.close()
print(f"Admin creado: {USERNAME} / {PASSWORD}")