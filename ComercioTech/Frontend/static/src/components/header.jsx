import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import logoHero from "../assets/logoComercioTech.png";
import SearchBar from "./searchbar";
import LowerHeader from "./lowerHeader";

export default function MainHeader () {
    const [usuario, setUsuario] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const u = localStorage.getItem('usuario');
        const token = localStorage.getItem('token');
        
        if (u && token) {
            fetch('/leo/auth/verify', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(res => {
                if (res.ok) {
                    setUsuario(JSON.parse(u));
                } else {
                    localStorage.removeItem('token');
                    localStorage.removeItem('usuario');
                    setUsuario(null);
                }
            })
            .catch(err => {
                console.error('Error al verificar token:', err);
                try {
                    setUsuario(JSON.parse(u));
                } catch (e) {
                    console.error(e);
                }
            });
        }
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('usuario');
        localStorage.removeItem('carrito');
        setUsuario(null);
        alert('Has cerrado sesión correctamente.');
        navigate('/');
    };

    return (
        <>
            <header>
                <nav className="main_navbar d-flex justify-content-between align-items-center px-4">
                    <div className="logo_container">
                        <Link to="/">
                            <img src={logoHero} alt="Logo Hero" className="header-logo-img" />
                        </Link>
                    </div>
                    <SearchBar />
                    <div className="d-flex align-items-center gap-3">
                        {usuario ? (
                            <div className="d-flex align-items-center gap-2 bg-light p-2 rounded shadow-sm">
                                <span className="text-secondary fw-bold header-user-status-text me-2">
                                    <i className="bi bi-person-fill me-1 text-primary"></i>
                                    {usuario.nombre}
                                </span>
                                {usuario.rol === 'Administrador' ? (
                                    <>
                                        <Link to="/admin/clientes" className="btn btn-sm btn-outline-secondary rounded-pill px-2 fw-bold me-1">
                                            Clientes
                                        </Link>
                                        <Link to="/admin/stock" className="btn btn-sm btn-outline-secondary rounded-pill px-2 fw-bold me-1">
                                            Stock
                                        </Link>
                                        <Link to="/admin/facturacion" className="btn btn-sm btn-outline-secondary rounded-pill px-2 fw-bold me-1">
                                            Finanzas
                                        </Link>
                                        <Link to="/admin/proveedores" className="btn btn-sm btn-outline-secondary rounded-pill px-2 fw-bold me-1">
                                            Proveedores
                                        </Link>
                                    </>
                                ) : (
                                    <Link to="/pedidosCliente" className="btn btn-sm btn-outline-primary rounded-pill px-3 fw-bold me-1">
                                        Mis Pedidos
                                    </Link>
                                )}
                                <button className="btn btn-sm btn-outline-danger rounded-pill px-3" onClick={handleLogout}>
                                    Salir
                                </button>
                            </div>
                        ) : (
                            <Link to="/loginUsuario" className="btn btn-sm btn-outline-primary rounded-pill px-3 fw-bold JnsnButton">
                                Iniciar Sesión
                            </Link>
                        )}
                    </div>
                </nav>
                <LowerHeader />
            </header>
        </>
    );
};