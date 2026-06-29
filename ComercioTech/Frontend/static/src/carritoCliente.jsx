import React, { useState, useEffect } from 'react';
import MainHeader from './components/header'
import MainFooter from './components/footer'

export default function CarritoCliente() {
  const [carrito, setCarrito] = useState([]);

  useEffect(() => {
    const carritoGuardado = JSON.parse(localStorage.getItem('carrito')) || [];
    setCarrito(carritoGuardado);
  }, []);

  const actualizarCantidad = (id, delta) => {
    const nuevoCarrito = carrito.map(item => {
      if ((item._id || item.id) === id) {
        const nuevaCantidad = Math.max(1, (item.cantidad || 1) + delta);
        return { ...item, cantidad: nuevaCantidad };
      }
      return item;
    });
    setCarrito(nuevoCarrito);
    localStorage.setItem('carrito', JSON.stringify(nuevoCarrito));
  };

  const eliminarProducto = (id) => {
    const nuevoCarrito = carrito.filter(item => (item._id || item.id) !== id);
    setCarrito(nuevoCarrito);
    localStorage.setItem('carrito', JSON.stringify(nuevoCarrito));
  };

  const vaciarCarrito = () => {
    if(window.confirm('¿Estás seguro de que quieres vaciar el carrito?')) {
      setCarrito([]);
      localStorage.removeItem('carrito');
    }
  };

  const calcularTotal = () => {
    return carrito.reduce((total, item) => total + ((item.precio_actual || item.precio || 0) * (item.cantidad || 1)), 0);
  };

  return (
    <>
      <MainHeader />
      <div className="container carrito-container my-5">
        <h1 className="text-center py-3 mb-4 rounded page_title">Carrito de Compras</h1>
        
        {carrito.length === 0 ? (
          <div className="carrito-vacio text-center py-5 bg-white rounded shadow-sm border-top border-4 border-primary">
            <i className="bi bi-cart-x text-muted" style={{ fontSize: '4rem' }}></i>
            <h3 className="mt-3 text-muted">Tu carrito está vacío</h3>
            <p className="text-muted mb-4">¿No sabes qué comprar? ¡Miles de productos te esperan!</p>
            <a href="/" className="btn btn-primary px-4 fw-bold">Ir a comprar</a>
          </div>
        ) : (
          <div className="row">
            <div className="col-lg-8">
              <div className="carrito-items-wrapper bg-white rounded shadow-sm p-4 overflow-auto">
                <table className="table table-borderless carrito-table align-middle mb-0" style={{ minWidth: '600px' }}>
                  <thead className="border-bottom">
                    <tr>
                      <th scope="col">Producto</th>
                      <th scope="col" className="text-center">Precio</th>
                      <th scope="col" className="text-center">Cantidad</th>
                      <th scope="col" className="text-end">Subtotal</th>
                      <th scope="col"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {carrito.map((item) => (
                      <tr key={item._id || item.id} className="border-bottom">
                        <td>
                          <div className="d-flex align-items-center gap-3">
                            <img 
                                src="/placeholder.png" 
                                alt={item.nombre} 
                                className="carrito-item-img rounded"
                            />
                            <div>
                              <h6 className="mb-1 fw-bold text-dark">{item.nombre}</h6>
                              <small className="text-muted text-uppercase fw-bold" style={{ fontSize: '0.75rem' }}>
                                {item.especificaciones_fabricante?.fabricante || 'General'}
                              </small>
                            </div>
                          </div>
                        </td>
                        <td className="text-center">${(item.precio_actual || item.precio || 0).toLocaleString('es-CL')}</td>
                        <td>
                          <div className="d-flex justify-content-center align-items-center gap-2">
                            <button className="btn btn-outline-secondary btn-cantidad" onClick={() => actualizarCantidad(item._id || item.id, -1)}>-</button>
                            <span className="fw-bold" style={{ width: '20px', textAlign: 'center' }}>{item.cantidad || 1}</span>
                            <button className="btn btn-outline-secondary btn-cantidad" onClick={() => actualizarCantidad(item._id || item.id, 1)}>+</button>
                          </div>
                        </td>
                        <td className="text-end fw-bold text-primary fs-5">
                          ${((item.precio_actual || item.precio || 0) * (item.cantidad || 1)).toLocaleString('es-CL')}
                        </td>
                        <td className="text-end">
                          <button className="btn btn-link text-danger p-0 ms-2" onClick={() => eliminarProducto(item._id || item.id)} title="Eliminar">
                            <i className="bi bi-trash-fill fs-5"></i>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="mt-3">
                <button className="btn btn-outline-danger fw-bold shadow-sm" onClick={vaciarCarrito}>
                  <i className="bi bi-trash me-2"></i>Vaciar Carrito
                </button>
              </div>
            </div>
            
            <div className="col-lg-4 mt-4 mt-lg-0">
              <div className="carrito-resumen bg-white rounded shadow-sm p-4 sticky-top" style={{ top: '120px' }}>
                <h4 className="fw-bold mb-4 border-bottom pb-2">Resumen de Compra</h4>
                
                <div className="d-flex justify-content-between mb-3">
                  <span className="text-muted">Subtotal ({carrito.reduce((acc, item) => acc + (item.cantidad || 1), 0)} productos)</span>
                  <span className="fw-bold">${calcularTotal().toLocaleString('es-CL')}</span>
                </div>
                <div className="d-flex justify-content-between mb-3">
                  <span className="text-muted">Envío</span>
                  <span className="text-success fw-bold">Gratis</span>
                </div>
                
                <hr className="my-4" />
                
                <div className="d-flex justify-content-between mb-4 align-items-end">
                  <span className="fw-bold fs-5 text-dark">Total</span>
                  <span className="fw-bold fs-3 text-primary">${calcularTotal().toLocaleString('es-CL')}</span>
                </div>
                
                <button className="btn btn-primary w-100 py-3 fw-bold fs-5 shadow-sm JnsnButton rounded-pill">
                  Proceder al Pago
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      <MainFooter />
    </>
  )
}