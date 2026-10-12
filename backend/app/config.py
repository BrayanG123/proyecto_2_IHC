# from anyio import Path
from pathlib import Path
import sys


SECRET_KEY         = "studymatch-clave-secreta-para-desarrollo"
ALGORITHM          = "HS256"
TOKEN_EXPIRE_HOURS = 24


ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]



# ubicacion del frontend
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend" / "dist"
INDEX_FILE   = FRONTEND_DIR / "index.html"
ASSETS_DIR   = FRONTEND_DIR / "assets"