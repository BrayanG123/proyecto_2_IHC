import { Link } from "react-router-dom";







export default function Dashboard({ user }) {
  return (
    <div className="row justify-content-center">
      <div className="col-lg-8">
        <div className="card border-0 shadow-sm">
          <div className="card-body p-4 p-md-5">
            <span className="badge text-bg-success mb-3">Ruta privada</span>
            <h1 className="fw-bold">Bienvenido, {user.nombre}</h1>
            <p className="text-secondary">
              Esta pantalla solo se puede abrir cuando existe una sesión válida.
            </p>

            <div className="list-group mt-4">
              <div className="list-group-item">
                <strong>Nombre:</strong> {user.nombre}
              </div>
              <div className="list-group-item">
                <strong>Correo:</strong> {user.email}
              </div>
              <div className="list-group-item">
                <strong>Sesión:</strong> autenticada
              </div>
            </div>

            {/* <div className="alert alert-info mt-4 mb-0">
              Si recargas esta página, StudyMatch vuelve a validar tu token y conserva la sesión mientras sea válido.
            </div> */}

            <p className="text-center mt-3 mb-0">
              <Link to="/new-study">
                Crear nueva sesion
              </Link>
            </p>
            <br />

            <p className="text-center mt-3 mb-0">
              <Link to="/sesions">
                Ir a Sesiones
              </Link>
            </p>
            <br />

            <p className="text-center mt-3 mb-0">
              <Link to="/historial" className="btn btn-primary">
                Mi historial
              </Link>
            </p>

          </div>
        </div>
      </div>
    </div>
  );
}