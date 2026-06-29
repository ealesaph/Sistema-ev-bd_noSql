import React, { useState, useEffect } from 'react';
import GridCard from './gridCardProductos';

export default function ListaProductosPorCategoria({ etiqueta }) {
    const [productos, setProductos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const limit = 20;

    const fetchProductos = async (pageNum) => {
        try {
            setLoading(true);
            const response = await fetch(`/leo/productos?etiqueta=${etiqueta}&page=${pageNum}&limit=${limit}`);
            if (!response.ok) {
                throw new Error('Error en la red al obtener productos');
            }
            const data = await response.json();
            if (data.exito) {
                if (pageNum === 1) {
                    setProductos(data.productos);
                } else {
                    setProductos(prev => [...prev, ...data.productos]);
                }
                setHasMore(data.productos.length === limit);
            } else {
                setError(data.mensaje);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        setPage(1);
        setHasMore(true);
        fetchProductos(1);
    }, [etiqueta]);

    const handleVerMas = () => {
        const nextPage = page + 1;
        setPage(nextPage);
        fetchProductos(nextPage);
    };

    if (loading && page === 1) {
        return (
            <div className="text-center py-5">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Cargando...</span>
                </div>
            </div>
        );
    }
    
    if (error && page === 1) {
        return <div className="alert alert-danger mx-5">Error: {error}</div>;
    }
    
    if (productos.length === 0 && !loading) {
        return <div className="alert alert-info mx-5">No hay productos disponibles en esta categoría.</div>;
    }

    return (
        <div className="container mb-5">
            <div className="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
                {productos.map(producto => (
                    <div className="col" key={producto._id}>
                        <GridCard producto={producto} />
                    </div>
                ))}
            </div>
            
            {hasMore && (
                <div className="text-center mt-5">
                    <button 
                        className="btn btn-outline-primary px-5 py-2 fw-bold rounded-pill JnsnButton" 
                        onClick={handleVerMas}
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                Cargando...
                            </>
                        ) : (
                            'Ver más'
                        )}
                    </button>
                </div>
            )}
        </div>
    );
}
