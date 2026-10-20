# StudyMatch

Aplicación académica para **encontrar compañeros y sesiones de estudio**.

## Tecnologías

- React
- Vite
- Bootstrap
- React Router
- FastAPI
- JWT
- bcrypt

## Funcionalidades incluidas

- Registro de una cuenta nueva.
- Inicio de sesión.
- Cierre de sesión.
- Sesión conservada al recargar la aplicación.
- Ruta pública: `/`.
- Ruta privada: `/dashboard`.
- La ruta privada redirige al login cuando no existe una sesión válida.
- Validación del usuario autenticado mediante JWT y `/perfil`.
- Recuperación de contraseña.
- Cambio de contraseña mediante código de recuperación simulado.
- No se necesita enviar correos reales.
- Crear sesiones con materia, modalidad, fecha y capacidad total.
- Unirse a sesiones futuras con inscripciones abiertas y cupos libres.
- Buscar por nombre y combinar filtros de materia, modalidad, fechas y disponibilidad.
- Conservar los filtros en la URL y las inscripciones en SQLite al recargar.

## 1. Ejecutar el backend

Abre una terminal en la carpeta `backend`.

### Windows

```bash
cd backend
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Linux / macOS

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

El backend estará disponible en:

`http://127.0.0.1:8000`

Documentación automática de FastAPI:

`http://127.0.0.1:8000/docs`

## 2. Ejecutar el frontend

Abre otra terminal en la carpeta `frontend`.

```bash
cd frontend
npm install
npm run dev
```

La aplicación estará disponible normalmente en:

`http://localhost:5173`

## 3. Probar el sistema

1. Entra a `http://localhost:5173`.
2. Pulsa **Registrarse**.
3. Crea una cuenta.
4. Inicia sesión.
5. Entrarás a `/dashboard`, que es la ruta privada.
6. Recarga la página: la sesión seguirá activa.
7. Cierra sesión y vuelve a intentar entrar a `/dashboard`: serás enviado a `/login`.
8. Para probar recuperación, entra a **¿Olvidaste tu contraseña?**.
9. Introduce el correo de una cuenta existente.
10. El sistema mostrará un código simulado.
11. Introduce ese código y una nueva contraseña.

## Inscripciones y filtros

Para probar una inscripción, crea una sesión con una cuenta y entra con otra. El creador no puede inscribirse en su propia sesión. El listado muestra los cupos libres y explica los bloqueos.

`cupo` es la capacidad total. Los lugares libres se calculan restando las inscripciones. Solo se permite unirse si la fecha es posterior a hoy, usando la fecha de Bolivia. El filtro «Hoy» permite consultar esas sesiones, pero no inscribirse en ellas. «Próximos 7 días» va desde mañana hasta dentro de siete días, inclusive.

Los usuarios, sesiones e inscripciones se guardan en `backend/data/studymatch.db`. Al arrancar se agrega la columna `materia` si falta; las sesiones anteriores quedan con la materia «General». No se borran sus datos.

El listado y las inscripciones requieren un usuario autenticado. La recuperación de contraseña sigue siendo una demostración con código en pantalla.

Para estudiar el código:

- `backend/app/repositorio.py`: `motivo_para_unirse` contiene la regla; `unirse_a_sesion` guarda la inscripción; `buscar_sesiones` consulta y filtra los datos.
- `backend/app/routes.py`: recibe las peticiones y obtiene el usuario del token.
- `frontend/src/SesionsPage.jsx`: filtros, listado y botón «Unirme».
- `frontend/src/CreateSesionPage.jsx`: formulario para crear sesiones.

## Pruebas

Desde `backend`, con el entorno virtual activado:

```bash
python -m unittest discover -s tests -t . -v
```

Las pruebas usan bases aisladas. Comprueban acceso, inscripciones, cupos, filtros, persistencia y dos intentos simultáneos por el último cupo.
