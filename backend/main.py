
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.config import ALLOWED_ORIGINS, FRONTEND_DIR, INDEX_FILE
from app.database import inicializar_db

from app.routes import router


# ============================================================
# CONFIGURACIÓN
# ============================================================

@asynccontextmanager
async def lifespan(app):
    inicializar_db()
    yield


app = FastAPI(
    title="StudyMatch API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)



# ============================================================
# FRONTEND REACT
# ============================================================

@app.get("/")
def servir_inicio():
    """
    Sirve el index.html de React.
    """

    if not INDEX_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "No se encontró el frontend compilado. "
                "Ejecuta 'npm run build' en frontend."
            )
        )

    return FileResponse(INDEX_FILE)


@app.get("/{full_path:path}")
def servir_react(full_path: str):
    """
    Permite que React Router funcione.

    Por ejemplo:

    /login
    /register
    /recover
    /dashboard

    Todas estas rutas terminan cargando index.html.
    """

    # Primero comprobamos si existe un archivo físico.
    archivo = (FRONTEND_DIR / full_path).resolve()
    if not archivo.is_relative_to(FRONTEND_DIR.resolve()):
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")

    if archivo.is_file():
        return FileResponse(archivo)

    # Si no existe, devolvemos React.
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)

    raise HTTPException(
        status_code=404,
        detail="Frontend no encontrado."
    )




if __name__ == "__main__":
    import uvicorn
    import threading
    import webbrowser
    import time

    def abrir_navegador():
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:8000")

    threading.Thread(
        target=abrir_navegador,
        daemon=True
    ).start()

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )
