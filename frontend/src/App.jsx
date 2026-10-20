import { useEffect, useState } from "react";
import { BrowserRouter } from "react-router-dom";


import { apiRequest, TOKEN_KEY } from "./api";
import AppRoutes from "./AppRoutes";
import Layout from "./Layout";



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

    <Layout
      user={user}
      onLogout={() => setUser(null)}
    >

      <AppRoutes
        user = {user}
        checking = { checking }
        onLogin={setUser}
      />

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
