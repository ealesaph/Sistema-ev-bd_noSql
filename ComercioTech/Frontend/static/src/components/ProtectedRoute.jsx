import React from 'react';
import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children, allowedRoles }) {
    const token = localStorage.getItem('token');
    const usuarioStr = localStorage.getItem('usuario');
    
    // Si no hay token o información de usuario, redirige al login
    if (!token || !usuarioStr) {
        return <Navigate to="/loginUsuario" replace />;
    }

    // Si se especificaron roles permitidos, verificar
    if (allowedRoles) {
        try {
            const usuarioObj = JSON.parse(usuarioStr);
            if (!allowedRoles.includes(usuarioObj.rol)) {
                // Redirigir a la página principal si no tiene privilegios para esta sección
                return <Navigate to="/" replace />;
            }
        } catch (e) {
            return <Navigate to="/loginUsuario" replace />;
        }
    }

    // Si está autenticado y tiene permisos, renderiza el componente hijo
    return children;
}
