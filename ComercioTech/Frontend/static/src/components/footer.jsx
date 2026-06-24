import { Link } from "react-router-dom";

export default function MaFooter () {
    return (
        <>
        <section className="footer_main">
            <footer className="footer_settings">
            <div className="footer_top">
                <Link className="logo_link" to="/"><img src="/src/assets/logoComercioTech.png" alt="Paddock Style logo" /></Link>
                <div className="footer_columns">
                    <div className="footer_col">
                        <p className="col_title">Contáctanos</p>
                        <ul className="col_info">
                            <li><i className="bi bi-telephone"></i> +56 9 1405 3314</li>
                            <li><a href="https://www.instagram.com/" target="_blank" rel="noreferrer"><i className="bi bi-instagram"></i> Instagram</a>
                            </li>
                            <li><a href="mailto:juan.navarrete.fritz@gmail.com?subject=Consulta" rel="noreferrer"><i
                                    className="bi bi-envelope-at-fill"></i> contacto@comerciotech.cl</a></li>
                        </ul>
                    </div>
                    <div className="footer_col">
                        <p className="col_title">Oficinas</p>
                        <div className="col_info">
                            <div className="office_location" style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
                                <a href="https://maps.app.goo.gl/JxFjL1ubP11rrr3u6" target="_blank" rel="noreferrer"><i className="bi bi-geo-alt"></i> Av. Pedro Aguirre Cerda 2115, Valdivia, Los Ríos</a>
                                <span><i className="bi bi-telephone"></i> +56 63 212 3456</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
                <hr className="footer_line"/>
                <div className="footer_bottom">
                    <a href="https://github.com/JunoAlpha" target="_blank" rel="noreferrer" className="dev_link">Desarrollado por: JunoAlpha</a>
                </div>
            </footer>
        </section>
        </>
    );
};