import { Link } from "react-router-dom";
import logoHero from "../assets/logoComercioTech.png";
import SearchBar from "./searchbar";
import LowerHeader from "./lowerHeader";

export default function MainHeader () {
    return (
        <>
            <header>
                <nav className="main_navbar">
                    <div className="logo_container">
                        <Link to="/">
                            <img src={logoHero} alt="Logo Hero" style={{ height: "130px", width: "auto" }} />
                        </Link>
                    </div>
                    <SearchBar />
                </nav>
                <LowerHeader />
            </header>
        </>
    );
};