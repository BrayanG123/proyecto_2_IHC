import { useState } from "react";
import { Alert, AuthCard, Input } from "./Components";
import { Link } from "react-router-dom";
import { apiRequest } from "./api";






export default function CreateSesionPage() {
  const [nombre, setNombre] = useState("");
  const [materia, setMateria] = useState("");
  const [modalidad, setModalidad] = useState("presencial");
  const [cupo, setCupo] = useState(1);
  const [fecha, setFecha] = useState("");
  const [inscripciones, setInscripciones] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");


  async function createNew(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      const data = await apiRequest("/guardar-nuevo", {
        method: "POST",
        body: JSON.stringify({ nombre, materia, modalidad, cupo, fecha, inscripciones }),
      });
      setMessage(data.mensaje);
      setNombre("");
      setMateria("");
      setModalidad("presencial");
      setCupo(1);
      setFecha("");
      setInscripciones(true);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <AuthCard title="Nueva sesion de estudio"
    >
      {error && <Alert type="danger" text={error} />}
      {message && <Alert type="success" text={message} />}

      <form onSubmit={createNew}>
        <Input
            label="nombre"
            name="nombre"
            value={nombre}
            type="text"
            onChange={(e) => setNombre(e.target.value)}
            required
        />

        <Input
            label="Materia"
            name="materia"
            value={materia}
            onChange={(e) => setMateria(e.target.value)}
            required
        />
        <div className="mb-3">
          <label htmlFor="modalidad" className="form-label fw-semibold">Modalidad</label>
          <select id="modalidad" className="form-select" value={modalidad}
                  onChange={(e) => setModalidad(e.target.value)}>
            <option value="presencial">Presencial</option>
            <option value="virtual">Virtual</option>
          </select>
        </div>
        <Input
            label="cupo"
            name="cupo"
            value={cupo}
            type="number"
            min="1"
            step="1"
            onChange={(e) => setCupo(e.target.value)}
            required
        />

        <Input
            label="fecha"
            name="fecha"
            type="date"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
            required
        />
        <label >Inscripciones:</label>
        <br />
        <label>
          <input
            name="checkdeinscripciones"
            type="radio"
            value="valorAbiertas"
            checked={inscripciones===true}
            onChange={(e) => setInscripciones(true)}
          >
          </input>
          Abiertas
        </label>

        <label>
          <input
            name="checkdeinscripciones"
            type="radio"
            value="valorCerradas"
            checked={inscripciones===false}
            onChange={(e) => setInscripciones(false)}
          >
          </input>
          Cerradas
        </label>




        <button className="btn btn-primary w-100">Crear sesión</button>
      </form>

      <p className="text-center mt-3 mb-0">
        <Link to="/sesions">Ver sesiones</Link>
      </p>
    </AuthCard>
  );
}
