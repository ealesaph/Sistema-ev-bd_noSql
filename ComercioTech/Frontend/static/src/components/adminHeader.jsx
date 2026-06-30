import { useState } from "react"; 
import { Link, useNavigate } from "react-router-dom";
import logoHero from "../assets/logoComercioTech.png";

export default function AdminHeader() {
    const navigate = useNavigate();
    
    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('usuario');
        navigate('/loginUsuario');
    };

    return (
        <>
            <header>
                <nav className="admin_navbar">
                    <div className="logo_container">
                        <img src={logoHero} alt="Logo ComercioTech" className="header-logo-img" />
                    </div>
                    <ul>
                        <li className="nav-cont">
                            <Link to="/admin/clientes">Clientes</Link>
                        </li>
                        <li className="nav-cont">
                            <Link to="/admin/stock">Stock</Link>
                        </li>
                        <li className="nav-cont">
                            <Link to="/admin/facturacion">Finanzas</Link>
                        </li>
                        <li className="nav_cont">
                            <Link to="/admin/proveedores">Proveedores</Link>
                        </li>
                        <li className="nav_cont">
                            <button 
                                onClick={handleLogout}
                                className="btn-logout-link"
                            >
                                Salir
                            </button>
                        </li>
                    </ul>
                </nav>
            </header>
        </>
    );
}
