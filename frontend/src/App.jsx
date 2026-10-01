import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
  useNavigate,
} from "react-router-dom";

const API_URL = "http://127.0.0.1:8000";
const TOKEN_KEY = "studymatch_token";

async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY);

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  let data = {};
  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    throw new Error(data.detail || "Ocurrió un error.");
  }

  return data;
}

function PrivateRoute({ user, checking, children }) {
  if (checking) {
    return <Loading />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function Layout({ user, onLogout, children }) {
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

function Home({ user }) {
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

        <div className="row g-3 mt-3">
          <Feature title="Registro" text="Crea una cuenta nueva con tu nombre, correo y contraseña." />
          <Feature title="Sesión persistente" text="La sesión se conserva aunque recargues la aplicación." />
          <Feature title="Ruta privada" text="Tu panel requiere una sesión autenticada para entrar." />
        </div>
      </div>
    </div>
  );
}

function Feature({ title, text }) {
  return (
    <div className="col-md-4">
      <div className="card h-100 border-0 shadow-sm">
        <div className="card-body">
          <h5 className="fw-bold">{title}</h5>
          <p className="text-secondary mb-0">{text}</p>
        </div>
      </div>
    </div>
  );
}

function Login({ onLogin }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await apiRequest("/login", {
        method: "POST",
        body: JSON.stringify(form),
      });

      localStorage.setItem(TOKEN_KEY, data.token);
      onLogin(data.usuario);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard title="Iniciar sesión" subtitle="Ingresa a tu cuenta de StudyMatch.">
      {error && <Alert type="danger" text={error} />}

      <form onSubmit={handleSubmit}>
        <Input label="Correo electrónico" name="email" type="email" value={form.email} onChange={handleChange} required />
        <Input label="Contraseña" name="password" type="password" value={form.password} onChange={handleChange} required />

        <button className="btn btn-primary w-100" disabled={loading}>
          {loading ? "Ingresando..." : "Iniciar sesión"}
        </button>
      </form>

      <div className="text-center mt-3">
        <Link to="/recover">¿Olvidaste tu contraseña?</Link>
      </div>
      <p className="text-center text-secondary mt-3 mb-0">
        ¿No tienes cuenta? <Link to="/register">Regístrate</Link>
      </p>
    </AuthCard>
  );
}

function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ nombre: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const data = await apiRequest("/registro", {
        method: "POST",
        body: JSON.stringify(form),
      });

      setSuccess(data.mensaje);
      setTimeout(() => navigate("/login"), 1000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard title="Crear cuenta" subtitle="Regístrate para comenzar a usar StudyMatch.">
      {error && <Alert type="danger" text={error} />}
      {success && <Alert type="success" text={`${success} Redirigiendo al inicio de sesión...`} />}

      <form onSubmit={handleSubmit}>
        <Input label="Nombre" name="nombre" value={form.nombre} onChange={handleChange} required />
        <Input label="Correo electrónico" name="email" type="email" value={form.email} onChange={handleChange} required />
        <Input label="Contraseña" name="password" type="password" value={form.password} onChange={handleChange} required />

        <button className="btn btn-primary w-100" disabled={loading}>
          {loading ? "Creando cuenta..." : "Registrarse"}
        </button>
      </form>

      <p className="text-center text-secondary mt-3 mb-0">
        ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
      </p>
    </AuthCard>
  );
}

function Recover() {
  const [email, setEmail] = useState("");
  const [codigo, setCodigo] = useState("");
  const [nuevaPassword, setNuevaPassword] = useState("");
  const [codeSent, setCodeSent] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function requestCode(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      const data = await apiRequest("/recuperar-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setCodigo(data.codigo);
      setCodeSent(true);
      setMessage(`Código simulado: ${data.codigo}`);
    } catch (err) {
      setError(err.message);
    }
  }

  async function changePassword(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      const data = await apiRequest("/cambiar-password", {
        method: "POST",
        body: JSON.stringify({ email, codigo, nueva_password: nuevaPassword }),
      });
      setMessage(`${data.mensaje} Ya puedes iniciar sesión con tu nueva contraseña.`);
      setCodeSent(false);
      setCodigo("");
      setNuevaPassword("");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <AuthCard title="Recuperar contraseña" subtitle="No se envía un correo real: el código se muestra en pantalla para la demostración.">
      {error && <Alert type="danger" text={error} />}
      {message && <Alert type="success" text={message} />}

      {!codeSent ? (
        <form onSubmit={requestCode}>
          <Input label="Correo electrónico" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <button className="btn btn-primary w-100">Generar código</button>
        </form>
      ) : (
        <form onSubmit={changePassword}>
          <Input label="Código de recuperación" value={codigo} onChange={(e) => setCodigo(e.target.value)} required />
          <Input label="Nueva contraseña" type="password" value={nuevaPassword} onChange={(e) => setNuevaPassword(e.target.value)} required />
          <button className="btn btn-primary w-100">Cambiar contraseña</button>
        </form>
      )}

      <p className="text-center mt-3 mb-0">
        <Link to="/login">Volver al inicio de sesión</Link>
      </p>
    </AuthCard>
  );
}

function Dashboard({ user }) {
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

            <div className="alert alert-info mt-4 mb-0">
              Si recargas esta página, StudyMatch vuelve a validar tu token y conserva la sesión mientras sea válido.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AuthCard({ title, subtitle, children }) {
  return (
    <div className="row justify-content-center">
      <div className="col-sm-10 col-md-7 col-lg-5">
        <div className="card border-0 shadow-sm">
          <div className="card-body p-4">
            <h1 className="h3 fw-bold">{title}</h1>
            <p className="text-secondary">{subtitle}</p>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

function Input({ label, ...props }) {
  return (
    <div className="mb-3">
      <label className="form-label fw-semibold">{label}</label>
      <input className="form-control" {...props} />
    </div>
  );
}

function Alert({ type, text }) {
  return <div className={`alert alert-${type}`}>{text}</div>;
}

function Loading() {
  return (
    <div className="d-flex justify-content-center align-items-center py-5">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Cargando...</span>
      </div>
    </div>
  );
}

function AppContent() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    async function validateSession() {
      const token = localStorage.getItem(TOKEN_KEY);

      if (!token) {
        setChecking(false);
        return;
      }

      try {
        const data = await apiRequest("/perfil");
        setUser(data);
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        setUser(null);
      } finally {
        setChecking(false);
      }
    }

    validateSession();
  }, []);

  return (
    <Layout user={user} onLogout={() => setUser(null)}>
      <Routes>
        <Route path="/" element={<Home user={user} />} />
        <Route path="/login" element={<Login onLogin={setUser} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/recover" element={<Recover />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute user={user} checking={checking}>
              <Dashboard user={user} />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
