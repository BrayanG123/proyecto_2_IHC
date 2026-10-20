

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom" 
import { apiRequest, TOKEN_KEY } from "./api";
import { Alert, AuthCard, Input } from "./Components";




export function Login({ onLogin }) {
    const navigate = useNavigate();
    const [form, setForm] = useState({
        email: "", 
        password: ""
    });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);


    function handleChange(event) {
        setForm({ 
            ...form,
            [event.target.name]: event.target.value
        })
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
        <AuthCard 
            title="Iniciar sesion"
            subtitle="Ingresa a tu cuenta de studmatch"
        >
            {error && <Alert type="danger" text={error}/>}

            <form onSubmit={handleSubmit}>

                <Input 
                    label="Email"
                    name="email"
                    type="email"
                    value = {form.email}
                    onChange = {handleChange}
                    required
                />

                <Input 
                    label="Password"
                    name="password"
                    type="password"
                    value = {form.password}
                    onChange = {handleChange}
                    required
                />

                <button 
                    className="btn btn-primary w-100" 
                    disabled={loading}
                >
                    {loading ? "Ingresando..." : "Iniciar Sesion"}
                </button>
            </form>

            <div className="text-center mt-3">
                <Link to="/recover">¿Olvidaste la contraseña?</Link>
            </div>

            <p className="text-center text-secondary mt-3 mb-0">
                ¿No tienes cuenta? <Link to="/register">Regístrate</Link>
            </p>

        </AuthCard> 
    );
}


export function Register() {

    const navigate = useNavigate();
    const [form, setForm] = useState({
        nombre: "",
        email: "",
        password: "",
    });
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [loading, setLoading] = useState(false);

    
    function handleChange(event) {
        setForm({ 
            ...form,
            [event.target.name]: event.target.value
        })
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
        }catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <AuthCard 
            title= "Crear cuenta"
            subtitle = "Registrate para empezar a usar StudyMatch"
        >
            {error && <Alert type="danger" text={error} />}

            { success && (
                <Alert 
                    type="success"
                    text= {`${success} Redirigiendo al inicio de sesion...`}
                />
            )}

            <form onSubmit={handleSubmit}>
                <Input 
                    label="Nombre"
                    name="nombre"
                    type="text"
                    value = {form.nombre}
                    onChange = {handleChange}
                    required
                />

                <Input 
                    label="Email"
                    name="email"
                    type="email"
                    value = {form.email}
                    onChange = {handleChange}
                    required
                />

                <Input 
                    label="Password"
                    name="password"
                    type="password"
                    value = {form.password}
                    onChange = {handleChange}
                    required
                />

                <button 
                    className="btn btn-primary w-100"
                    disabled= {loading}
                >
                    {loading ? "Creando cuenta..." : "Registrarse"}
                </button>
            </form>
            
            <p className="text-center text-secondary mt-3 mb-0">
                ¿Ya tienes cuenta? <Link to="/login">Inicia sesion</Link>
            </p>
        </AuthCard>
    );
}
