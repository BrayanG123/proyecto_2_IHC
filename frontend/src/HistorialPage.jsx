import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Alert, Loading } from "./Components";
import { apiRequest } from "./api";




function formatearFecha(fecha) {
  const [anio, mes, dia] = fecha.split("-");
  return `${dia}/${mes}/${anio}`;
}

function formatearFechaHora(fecha) {

  if (!fecha) return "Fecha no registrada";

  return new Date(fecha).toLocaleString("es-BO", {
    timeZone: "America/La_Paz",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });

}

export default function HistorialPage() {

  const [historial, setHistorial] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actualizacion, setActualizacion] = useState(0);


  useEffect(() => {
    let activo = true;

    async function cargarHistorial() {
      setLoading(true);
      setError("");

      try {

        const datos = await apiRequest("/historial-sesiones");
        if (activo)  setHistorial(datos);
        
      } catch (err) {
        if (activo) setError(err.message);
      } finally {
        if (activo)  setLoading(false);
        
      }
    }

    cargarHistorial();

    return () => {
      activo = false;
    };

  }, [actualizacion]);

  return (
    <div>
      <h1>Mi historial de sesiones</h1>

      <p className="text-secondary">
        Tus inscripciones con fecha registrada aparecen
        de la más reciente a la más antigua.
      </p>

      <div className="d-flex gap-2 flex-wrap mb-4">
        <Link to="/sesions" className="btn btn-primary">
          Buscar sesiones
        </Link>

        <Link to="/dashboard" className="btn btn-outline-secondary">
          Volver al panel
        </Link>
      </div>

      {loading && <Loading />}

      {!loading && error && (
        <div>
          <Alert type="danger" text={error} />

          <button
            type="button"
            className="btn btn-outline-primary"
            onClick={() => setActualizacion((valor) => valor + 1)}
          >
            Reintentar
          </button>
        </div>
      )}

      {!loading && !error && historial.length === 0 && (
        <div className="card card-body">
          <h2 className="h5">Todavía no tienes inscripciones</h2>

          <p className="mb-0">
            Usa «Buscar sesiones» para encontrar una y unirte.
          </p>
        </div>
      )}

      {!loading && !error && (
        <div className="d-grid gap-3">
          {historial.map((registro) => (
            <article className="card" key={registro.sesion_id}>
              <div className="card-body">
                <h2 className="h5">{registro.nombre}</h2>

                <p>
                  <strong>Materia:</strong> {registro.materia}
                </p>

                <p>
                  <strong>Modalidad:</strong> {registro.modalidad}
                </p>

                <p>
                  <strong>Fecha de la sesión:</strong>{" "}
                  {formatearFecha(registro.fecha_sesion)}
                </p>

                <p>
                  <strong>Te inscribiste:</strong>{" "}
                  {formatearFechaHora(registro.fecha_inscripcion)}
                </p>

                <p className="mb-0">
                  <strong>Resultado:</strong> {registro.resultado}
                </p>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}