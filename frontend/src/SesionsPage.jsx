import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Alert, Input, Loading } from "./Components";
import { apiRequest } from "./api";

const nombresFiltros = {
  nombre: "Nombre", materia: "Materia", modalidad: "Modalidad",
  periodo: "Fecha", desde: "Desde", hasta: "Hasta", disponible: "Disponibilidad",
};

function formatearFecha(fecha) {
  const [anio, mes, dia] = fecha.split("-");
  return `${dia}/${mes}/${anio}`;
}

function leerFiltros(parametros) {
  return {
    nombre: parametros.get("nombre") || "",
    materia: parametros.get("materia") || "",
    modalidad: parametros.get("modalidad") || "",
    periodo: parametros.get("periodo") || "",
    desde: parametros.get("desde") || "",
    hasta: parametros.get("hasta") || "",
    disponible: parametros.get("disponible") === "true",
  };
}

export default function SesionsPage() {
  // Los filtros aplicados quedan en la URL para conservarlos al recargar.
  const [parametros, setParametros] = useSearchParams();
  const consulta = parametros.toString();
  const [filtros, setFiltros] = useState(() => leerFiltros(parametros));
  const [sesiones, setSesiones] = useState([]);
  const [materias, setMaterias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [errorInscripcion, setErrorInscripcion] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [inscribiendo, setInscribiendo] = useState(null);
  const [actualizacion, setActualizacion] = useState(0);

  useEffect(() => {
    let activo = true;
    const controlador = new AbortController();
    setFiltros(leerFiltros(new URLSearchParams(consulta)));

    async function cargarSesiones() {
      setLoading(true);
      setError("");
      try {
        const [lista, listaMaterias] = await Promise.all([
          apiRequest(`/all-sesions?${consulta}`, { signal: controlador.signal }),
          apiRequest("/materias", { signal: controlador.signal }),
        ]);
        if (activo) {
          setSesiones(lista);
          setMaterias(listaMaterias);
        }
      } catch (err) {
        if (activo) setError(err.message);
      } finally {
        if (activo) setLoading(false);
      }
    }

    cargarSesiones();
    return () => {
      activo = false;
      controlador.abort();
    };
  }, [consulta, actualizacion]);

  function cambiarFiltro(event) {
    const { name, value, type, checked } = event.target;
    setFiltros({ ...filtros, [name]: type === "checkbox" ? checked : value });
  }

  function aplicarFiltros(event) {
    event.preventDefault();
    const nuevos = new URLSearchParams();
    for (const [nombre, valor] of Object.entries(filtros)) {
      if ((nombre === "desde" || nombre === "hasta") && filtros.periodo !== "rango") continue;
      if (valor) nuevos.set(nombre, String(valor).trim());
    }
    setMensaje("");
    setErrorInscripcion("");
    setParametros(nuevos);
  }

  function quitarFiltro(nombre) {
    const nuevos = new URLSearchParams(parametros);
    nuevos.delete(nombre);
    if (["periodo", "desde", "hasta"].includes(nombre)) {
      nuevos.delete("periodo");
      nuevos.delete("desde");
      nuevos.delete("hasta");
    }
    setMensaje("");
    setErrorInscripcion("");
    setParametros(nuevos);
  }

  async function unirse(sesionId) {
    setInscribiendo(sesionId);
    setErrorInscripcion("");
    setMensaje("");
    try {
      const respuesta = await apiRequest(`/sesiones/${sesionId}/inscribirse`, { method: "POST" });
      setMensaje(respuesta.mensaje);
    } catch (err) {
      setErrorInscripcion(err.message);
    } finally {
      setInscribiendo(null);
      // Volvemos a consultar por si otra persona ocupó el último cupo.
      setActualizacion((valor) => valor + 1);
    }
  }

  function textoFiltro(nombre, valor) {
    if (nombre === "disponible") return "Puedo unirme";
    if (nombre === "desde" || nombre === "hasta") return formatearFecha(valor);
    if (nombre === "periodo") return { hoy: "Hoy", proximos7: "Próximos 7 días", rango: "Rango de fechas" }[valor] || valor;
    return valor;
  }

  return (
    <div>
      <h1>Sesiones de estudio</h1>
      <p><Link to="/new-study">Crear nueva sesión</Link></p>

      <form className="card card-body mb-3" onSubmit={aplicarFiltros}>
        <div className="row">
          <div className="col-md-6">
            <Input label="Buscar por nombre" name="nombre" value={filtros.nombre} onChange={cambiarFiltro} />
          </div>
          <div className="col-md-6 mb-3">
            <label htmlFor="materia" className="form-label fw-semibold">Materia</label>
            <select id="materia" name="materia" className="form-select" value={filtros.materia} onChange={cambiarFiltro}>
              <option value="">Todas</option>
              {materias.map((materia) => <option key={materia} value={materia}>{materia}</option>)}
            </select>
          </div>
          <div className="col-md-6 mb-3">
            <label htmlFor="modalidad" className="form-label fw-semibold">Modalidad</label>
            <select id="modalidad" name="modalidad" className="form-select" value={filtros.modalidad} onChange={cambiarFiltro}>
              <option value="">Todas</option>
              <option value="presencial">Presencial</option>
              <option value="virtual">Virtual</option>
            </select>
          </div>
          <div className="col-md-6 mb-3">
            <label htmlFor="periodo" className="form-label fw-semibold">Fecha</label>
            <select id="periodo" name="periodo" className="form-select" value={filtros.periodo} onChange={cambiarFiltro} aria-describedby="ayuda-fecha">
              <option value="">Todas</option>
              <option value="hoy">Hoy</option>
              <option value="proximos7">Próximos 7 días</option>
              <option value="rango">Rango de fechas</option>
            </select>
            <p id="ayuda-fecha" className="form-text mb-0">
              «Próximos 7 días» cuenta desde mañana hasta dentro de 7 días.
              Solo puedes unirte a sesiones con fecha futura.
            </p>
          </div>
          {filtros.periodo === "rango" && <>
            <div className="col-md-6">
              <Input label="Desde" name="desde" type="date" value={filtros.desde} onChange={cambiarFiltro} required />
            </div>
            <div className="col-md-6">
              <Input label="Hasta" name="hasta" type="date" min={filtros.desde} value={filtros.hasta} onChange={cambiarFiltro} required />
            </div>
          </>}
        </div>
        <label className="mb-3">
          <input type="checkbox" name="disponible" checked={filtros.disponible} onChange={cambiarFiltro} />
          {" "}Solo sesiones a las que puedo unirme
        </label>
        <div className="d-flex gap-2 flex-wrap">
          <button className="btn btn-primary" type="submit">Buscar</button>
          <button className="btn btn-outline-secondary" type="button" onClick={() => {
            setFiltros(leerFiltros(new URLSearchParams()));
            setParametros({});
            setMensaje("");
            setErrorInscripcion("");
          }}>Limpiar filtros</button>
        </div>
      </form>

      {consulta && <div className="mb-3 d-flex gap-2 flex-wrap" aria-label="Filtros activos">
        {Array.from(parametros).filter(([nombre]) => nombresFiltros[nombre]).map(([nombre, valor]) => (
          <button key={nombre} className="btn btn-outline-secondary btn-sm" onClick={() => quitarFiltro(nombre)}
                  aria-label={`Quitar filtro ${nombresFiltros[nombre]}`}>
            {nombresFiltros[nombre]}: {textoFiltro(nombre, valor)} ×
          </button>
        ))}
      </div>}

      {error && <div className="mb-3">
        <Alert type="danger" text={error} />
        <button type="button" className="btn btn-outline-primary"
                onClick={() => setActualizacion((valor) => valor + 1)}>
          Reintentar
        </button>
      </div>}
      {errorInscripcion && <Alert type="danger" text={errorInscripcion} />}
      {mensaje && <Alert type="success" text={mensaje} />}
      {loading ? <Loading /> : !error && <>
        {sesiones.length === 0 && <p>
          {consulta ? "Ninguna sesión coincide con los filtros. Prueba quitarlos."
            : "Todavía no hay sesiones. Puedes crear una para empezar."}
        </p>}
        <div className="row g-3">
          {sesiones.map((sesion) => (
            <div key={sesion.id} className="col-12 col-md-6 col-lg-4">
              <div className="card h-100">
                <div className="card-body d-flex flex-column">
                  <h2 className="h5">{sesion.nombre}</h2>
                  <p>Materia: {sesion.materia}</p>
                  <p>Modalidad: {sesion.modalidad}</p>
                  <p>Cupos disponibles: {sesion.cupos_disponibles} de {sesion.cupo}</p>
                  <p>Fecha: {formatearFecha(sesion.fecha)}</p>
                  <p>{sesion.inscripciones_abiertas ? "Inscripciones abiertas" : "Inscripciones cerradas"}</p>
                  {sesion.motivo && <p className="text-secondary">{sesion.motivo}</p>}
                  <button className="btn btn-primary mt-auto" disabled={!sesion.puede_unirse || inscribiendo !== null}
                          onClick={() => unirse(sesion.id)}>
                    {inscribiendo === sesion.id ? "Inscribiendo..." : sesion.inscrito ? "Ya estás inscrito" : "Unirme"}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </>}
      <p className="text-center mt-3"><Link to="/dashboard">Volver al panel</Link></p>
    </div>
  );
}
