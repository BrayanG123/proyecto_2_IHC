import { Link } from "react-router-dom";





export default function Home({ user }) {
  return (
    <div className="row justify-content-center">
      <div className="col-lg-9">
        <div className="card shadow-sm border-0 hero-card">
          <div className="card-body p-4 p-md-5 text-center">
            <span className="badge text-bg-primary mb-3">StudyMatch</span>
            <h1 className="display-5 fw-bold">Encuentra compañeros y sesiones de estudio</h1>
            <p className="lead text-secondary mt-3">
              Una plataforma sencilla para crear una cuenta, iniciar sesión y acceder a tu espacio privado.
            </p>

            {user ? (
              <Link to="/dashboard" className="btn btn-primary btn-lg mt-3">
                Ir a mi espacio
              </Link>
            ) : (
              <div className="d-flex justify-content-center gap-2 mt-4 flex-wrap">
                <Link to="/register" className="btn btn-primary btn-lg">
                  Crear cuenta
                </Link>
                <Link to="/login" className="btn btn-outline-primary btn-lg">
                  Iniciar sesión
                </Link>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}