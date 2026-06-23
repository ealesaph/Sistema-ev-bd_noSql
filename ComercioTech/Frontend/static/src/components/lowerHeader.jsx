import { Link } from "react-router-dom";

export default function LowerHeader () {
    return (
        <>
            <nav className="lower_navbar">
                <div className="lower_nav_container">
                    <ul>
                        <li className="nav-cont">
                            <Link to="/computadores">Computadores</Link>
                        </li>
                        <li className="nav-cont">
                            <Link to="/hogarOficina">Hogar/Oficina</Link>
                        </li>
                        <li className="nav-cont">
                            <Link to="/perifericos">Periféricos</Link>
                        </li>
                        <li className="nav-cont">
                            <Link to="/componentes">Componentes</Link>
                        </li>
                        <li className="nav-cont">
                            <Link to="/conectividadRedes">Conectividad/Redes</Link>
                        </li>
                        <li className="nav-cont">
                            <Link to="/electronica">Electrónica</Link>
                        </li>
                        <li className="nav-cont">
                            <Link to="/software">Software</Link>
                        </li>
                    </ul>
                </div>
            </nav>
        </>
    );
};
