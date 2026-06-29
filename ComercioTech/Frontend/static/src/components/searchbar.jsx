import { useState, useEffect, useRef } from "react";

// Envuelve las coincidencias de "term" dentro de "text" en <mark>
function resaltarCoincidencias(text, term) {
  if (!term.trim()) return text;

  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`(${escaped})`, "gi");
  const partes = text.split(regex);

  return partes.map((parte, i) =>
    parte.toLowerCase() === term.toLowerCase() ? (
      <mark key={i} className="search-mark">
        {parte}
      </mark>
    ) : (
      parte
    )
  );
}

function SearchBar() {
  const [query, setQuery] = useState("");
  const [resultados, setResultados] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [mostrarResultados, setMostrarResultados] = useState(false);
  const abortControllerRef = useRef(null);
  const searchContainerRef = useRef(null);

  // Cerrar resultados al hacer clic fuera
  useEffect(() => {
    function handleClickOutside(event) {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target)) {
        setMostrarResultados(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      setResultados([]);
      return;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const timeoutId = setTimeout(() => {
      const controller = new AbortController();
      abortControllerRef.current = controller;
      setCargando(true);

      // Límite de 6 resultados
      fetch(
        `/leo/productos/buscar?q=${encodeURIComponent(query)}&pagina=1&limite=6`,
        { signal: controller.signal }
      )
        .then((res) => res.json())
        .then((data) => {
          setResultados(data.resultados || data.productos || []);
          setMostrarResultados(true);
        })
        .catch((err) => {
          if (err.name !== "AbortError") {
            console.error(err);
            setResultados([]);
          }
        })
        .finally(() => setCargando(false));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

  return (
    <div className="flex-grow-1 position-relative mx-3" ref={searchContainerRef}>
      <div className="d-flex gap-2">
        <div className="input-group">
          <input
            type="text"
            className="form-control"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setMostrarResultados(true);
            }}
            onFocus={() => {
                if (query.trim()) setMostrarResultados(true);
            }}
            placeholder="Buscar productos..."
          />
          <button className="btn btn-primary JnsnButton" type="button">
            <i className="bi bi-search"></i>
          </button>
        </div>
        
        {/* Botón de Carrito agregado */}
        <a href="/carritoCliente" className="btn btn-secondary d-flex align-items-center flex-shrink-0" title="Ir al Carrito">
          <i className="bi bi-cart"></i>
        </a>
      </div>

      {cargando && mostrarResultados && (
        <div className="search-dropdown loading-dropdown p-2">
            <p className="text-muted mb-0">Buscando...</p>
        </div>
      )}

      {!cargando && mostrarResultados && resultados.length > 0 && (
        <div className="search-dropdown">
          <ul className="search-results-list">
            {resultados.map((r) => (
              <li key={r._id || r.id} className="search-result-item">
                <a href={`/producto/${r._id || r.id}`} className="search-result-link">
                    <strong>{resaltarCoincidencias(r.nombre || "", query)}</strong>
                    <p className="search-result-desc">
                      {resaltarCoincidencias(r.descripcion || "", query)}
                    </p>
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default SearchBar;