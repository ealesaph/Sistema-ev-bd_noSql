import { useState, useEffect, useRef } from "react";

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

    // Cancela la petición anterior si todavía no respondió
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
    <div style={{ maxWidth: 400 }}>
      <input
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setPagina(1); // reinicia paginación en cada búsqueda nueva
        }}
        placeholder="Buscar productos..."
        style={{ width: "100%", padding: 8 }}
      />

      {cargando && <p>Buscando...</p>}

      <ul style={{ listStyle: "none", padding: 0 }}>
        {resultados.map((r) => (
          <li key={r.id} style={{ padding: "6px 0", borderBottom: "1px solid #eee" }}>
            <strong>{r.nombre}</strong>
            <p style={{ margin: 0, fontSize: 13, color: "#666" }}>{r.descripcion}</p>
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