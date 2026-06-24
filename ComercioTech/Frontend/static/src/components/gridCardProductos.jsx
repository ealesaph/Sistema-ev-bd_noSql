import React, { useState, useEffect } from 'react';

export default function GridCard({ producto }) {
    const item = producto || {};

    // Si el producto no está activo, no hacemos append de la card en la página
    if (!item.activo) {
        return null;
    }

    const agregarProducto = () => {
        const carritoActual = JSON.parse(localStorage.getItem('carrito')) || [];
        carritoActual.push(item);
        localStorage.setItem('carrito', JSON.stringify(carritoActual));

        alert(`¡${item.nombre} añadido al carrito!`);
    };

    // Extraemos los datos según la estructura exacta de 'pruebas datos No Sql.py'
    const marca = item.especificaciones_fabricante?.fabricante || "General";
    
    // En el script, el nombre es f"{marca} {modelo}", así que le quitamos la marca si empieza con ella
    // para mostrar solo el modelo debajo de la imagen como pediste.
    const nombreCompleto = item.nombre || "Producto Sin Nombre";
    const modelo = nombreCompleto.toLowerCase().startsWith(marca.toLowerCase()) 
                   ? nombreCompleto.substring(marca.length).trim() 
                   : nombreCompleto;

    const precio = item.precio_actual || item.precio || 0;
    const etiqueta = item.etiqueta || "general";

    return (
        <div className="card h-100 shadow-sm border-0" style={{ transition: "transform 0.2s" }}>
            {/* 1. Marca en el tope de la card */}
            <div className="card-header bg-white border-bottom-0 pt-3 pb-0">
                <span className="text-muted fw-bold text-uppercase" style={{ fontSize: '0.8rem' }}>
                    {marca}
                </span>
            </div>

            {/* Ruteo hacia la pestaña correspondiente en /assets/ usando la etiqueta */}
            <a href={`/assets/${etiqueta}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                <img 
                    src="/placeholder.png" 
                    className="card-img-top p-3" 
                    alt={modelo} 
                    style={{ objectFit: 'contain', height: '180px' }} 
                />
                
                {/* 2. Modelo debajo de la imagen al medio */}
                <div className="card-body pt-0 pb-2">
                    <h5 className="card-title text-dark mb-1" style={{ fontSize: '1.1rem', lineHeight: '1.4' }}>
                        {modelo}
                    </h5>
                    {item.descripcion && (
                        <p className="card-text text-muted small text-truncate">
                            {item.descripcion}
                        </p>
                    )}
                </div>
            </a>
            
            {/* 3. Precio actual al final junto al botón */}
            <div className="card-footer bg-white border-top-0 pt-0 pb-3">
                <div className="d-flex flex-column align-items-start">
                    <span className="fs-4 fw-bold text-primary mb-2">
                        ${precio.toLocaleString('es-CL')}
                    </span>
                    <button onClick={agregarProducto} className="btn btn-primary w-100 JnsnButton fw-bold">
                        Añadir al Carrito
                    </button>
                </div>
            </div>
        </div>
    );
}
