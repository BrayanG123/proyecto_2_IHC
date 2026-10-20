import { Link, useNavigate } from "react-router-dom";
import { apiRequest, TOKEN_KEY } from "./api";





export default function Layout({ user, onLogout, children }) {
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      if (localStorage.getItem(TOKEN_KEY)) {
        await apiRequest("/logout", { method: "POST" });
      }
    } catch {
      // Aunque la API falle, eliminamos el token local para cerrar sesión.
    } finally {
      localStorage.removeItem(TOKEN_KEY);
      onLogout();
      navigate("/login");
    }
  }

  return (
    <>
      <nav className="navbar navbar-expand-lg bg-dark navbar-dark">
        <div className="container">
          <Link className="navbar-brand fw-bold" to="/">
            StudyMatch
          </Link>

          <div className="d-flex align-items-center gap-2">
            {user ? (
              <>
                <span className="text-white small d-none d-md-inline">
                  Hola, {user.nombre}
                </span>
                <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>
                  Cerrar sesión
                </button>
              </>
            ) : (
              <>
                <Link className="btn btn-outline-light btn-sm" to="/login">
                  Iniciar sesión
                </Link>
                <Link className="btn btn-primary btn-sm" to="/register">
                  Registrarse
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      <main className="container py-5">{children}</main>
    </>
  );
}