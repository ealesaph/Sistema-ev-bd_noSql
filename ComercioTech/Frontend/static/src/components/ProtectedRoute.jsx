import React from 'react';
import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
    const token = localStorage.getItem('token');
    const usuario = localStorage.getItem('usuario');
    
    // Si no hay token o información de usuario, redirige al login
    if (!token || !usuario) {
        return <Navigate to="/loginUsuario" replace />;
    }

    // Si está autenticado, renderiza el componente hijo (la ruta protegida)
    return children;
}
