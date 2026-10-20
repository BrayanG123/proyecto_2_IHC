


const API_URL = "http://127.0.0.1:8000";
export const TOKEN_KEY = "studymatch_token";


export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY);

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (err) {
    if (err.name === "AbortError") throw err;
    throw new Error("No se pudo conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.");
  }

  let data = {};
  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail)
      ? detail.map((error) => `${error.loc.at(-1)}: ${error.msg}`).join(". ")
      : detail;
    throw new Error(message || "Ocurrió un error.");
  }

  return data;
}
