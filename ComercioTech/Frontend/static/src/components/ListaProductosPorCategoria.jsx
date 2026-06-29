import React, { useState, useEffect } from 'react';
import GridCard from './gridCardProductos';

export default function ListaProductosPorCategoria({ etiqueta }) {
    const [productos, setProductos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchProductos = async () => {
            try {
                setLoading(true);
                const response = await fetch(`/leo/productos?etiqueta=${etiqueta}`);
                if (!response.ok) {
                    throw new Error('Error en la red al obtener productos');
                }
                const data = await response.json();
                if (data.exito) {
                    setProductos(data.productos);
                } else {
                    setError(data.mensaje);
                }
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchProductos();
    }, [etiqueta]);

    if (loading) {
        return (
            <div className="text-center py-5">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Cargando...</span>
                </div>
            </div>
        );
    }
    
    if (error) {
        return <div className="alert alert-danger mx-5">Error: {error}</div>;
    }
    
    if (productos.length === 0) {
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
        </div>
    );
}
