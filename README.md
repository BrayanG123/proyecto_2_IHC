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

## Importante

Este proyecto usa una estructura de usuarios **en memoria** para que sea sencillo de ejecutar y entender. Si reinicias FastAPI, los usuarios registrados se borran.

Para un proyecto real, los usuarios deberían guardarse en una base de datos y la recuperación de contraseña debería utilizar un sistema seguro de tokens enviados por correo.
