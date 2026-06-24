import { useState, useEffect, useRef } from "react";

// Envuelve las coincidencias de "term" dentro de "text" en <mark>
function resaltarCoincidencias(text, term) {
  if (!term.trim()) return text;

  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`(${escaped})`, "gi");
  const partes = text.split(regex);

  return partes.map((parte, i) =>
    parte.toLowerCase() === term.toLowerCase() ? (
      <mark key={i} style={{ backgroundColor: "#fff176", padding: 0 }}>
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
  const [total, setTotal] = useState(0);
  const [pagina, setPagina] = useState(1);
  const [cargando, setCargando] = useState(false);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    if (!query.trim()) {
      setResultados([]);
      setTotal(0);
      return;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const timeoutId = setTimeout(() => {
      const controller = new AbortController();
      abortControllerRef.current = controller;
      setCargando(true);

      fetch(
        `/api/buscar?q=${encodeURIComponent(query)}&pagina=${pagina}&limite=10`,
        { signal: controller.signal }
      )
        .then((res) => res.json())
        .then((data) => {
          setResultados(data.resultados);
          setTotal(data.total);
        })
        .catch((err) => {
          if (err.name !== "AbortError") console.error(err);
        })
        .finally(() => setCargando(false));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query, pagina]);

  return (
    <div style={{ maxWidth: 450 }}>
      <div className="d-flex gap-2">
        <div className="input-group">
          <input
            type="text"
            className="form-control"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setPagina(1);
            }}
            placeholder="Buscar productos..."
          />
          <button className="btn btn-primary JnsnButton" type="button">
            <i className="bi bi-search"></i>
          </button>
        </div>
        
        {/* Botón de Carrito agregado */}
        <a href="/carritoCliente" className="btn btn-secondary d-flex align-items-center" title="Ir al Carrito">
          <i className="bi bi-cart"></i>
        </a>
      </div>

      {cargando && <p className="mt-2 text-muted">Buscando...</p>}

      <ul style={{ listStyle: "none", padding: 0 }}>
        {resultados.map((r) => (
          <li key={r.id} style={{ padding: "6px 0", borderBottom: "1px solid #eee" }}>
            <strong>{resaltarCoincidencias(r.nombre, query)}</strong>
            <p style={{ margin: 0, fontSize: 13, color: "#666" }}>
              {resaltarCoincidencias(r.descripcion, query)}
            </p>
          </li>
        ))}
      </ul>

      {total > 10 && (
        <div>
          <button disabled={pagina === 1} onClick={() => setPagina((p) => p - 1)}>
            Anterior
          </button>
          <span style={{ margin: "0 8px" }}>Página {pagina}</span>
          <button
            disabled={pagina * 10 >= total}
            onClick={() => setPagina((p) => p + 1)}
          >
            Siguiente
          </button>
        </div>
      )}
    </div>
  );
}

export default SearchBar;