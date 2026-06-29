import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainHeader from './components/header'
import MainFooter from './components/footer'

export default function CarritoCliente() {
  const [carrito, setCarrito] = useState([]);
  const [usuario, setUsuario] = useState(null);
  const [idCliente, setIdCliente] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingCheckout, setLoadingCheckout] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const inicializarCarrito = async () => {
      setLoading(true);
      
      // 1. Obtener datos del usuario logueado
      const uStr = localStorage.getItem('usuario');
      let currentIdCliente = null;
      let currentUsuario = null;
      
      if (uStr) {
        try {
          currentUsuario = JSON.parse(uStr);
          currentIdCliente = currentUsuario.id_cliente;
          setUsuario(currentUsuario);
          setIdCliente(currentIdCliente);
        } catch (e) {
          console.error(e);
        }
      }

      // 2. Obtener carrito local de invitado (si existe)
      const carritoLocal = JSON.parse(localStorage.getItem('carrito')) || [];

      if (currentIdCliente) {
        try {
          // Si hay artículos en el carrito local, sincronizarlos con la base de datos MongoDB
          if (carritoLocal.length > 0) {
            for (const item of carritoLocal) {
              await fetch('/leo/carrito/', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                  cliente_id: currentIdCliente,
                  producto_id: item._id || item.id,
                  cantidad: item.cantidad || 1,
                  nombre: item.nombre,
                  precio_unitario: item.precio_actual || item.precio || 0,
                  id_producto_sql: item.id_producto_sql
                })
              });
            }
            // Limpiar el carrito local una vez sincronizado
            localStorage.removeItem('carrito');
          }

          // Cargar el carrito definitivo de MongoDB
          const response = await fetch(`/leo/carrito/${currentIdCliente}`);
          const data = await response.json();
          if (data.exito && data.carrito) {
            setCarrito(data.carrito.items || []);
          } else {
            setCarrito([]);
          }
        } catch (err) {
          console.error('Error al sincronizar/cargar carrito desde MongoDB:', err);
        }
      } else {
        // Usuario no logueado, usar sólo localStorage
        setCarrito(carritoLocal);
      }
      
      setLoading(false);
    };

    inicializarCarrito();
  }, []);

  const actualizarCantidad = async (id, delta) => {
    if (idCliente) {
      try {
        const itemObj = carrito.find(item => (item.producto_id || item._id || item.id) === id);
        if (!itemObj) return;

        // Evitar que la cantidad sea menor a 1
        if (delta === -1 && (itemObj.cantidad || 1) <= 1) return;

        const response = await fetch('/leo/carrito/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            cliente_id: idCliente,
            producto_id: id,
            cantidad: delta,
            nombre: itemObj.nombre,
            precio_unitario: itemObj.precio_unitario || itemObj.precio_actual || itemObj.precio || 0,
            id_producto_sql: itemObj.id_producto_sql
          })
        });

        if (response.ok) {
          const res = await fetch(`/leo/carrito/${idCliente}`);
          const data = await res.json();
          if (data.exito && data.carrito) {
            setCarrito(data.carrito.items || []);
          }
        }
      } catch (err) {
        console.error('Error al actualizar cantidad en MongoDB:', err);
      }
    } else {
      const nuevoCarrito = carrito.map(item => {
        if ((item.producto_id || item._id || item.id) === id) {
          const nuevaCantidad = Math.max(1, (item.cantidad || 1) + delta);
          return { ...item, cantidad: nuevaCantidad };
        }
        return item;
      });
      setCarrito(nuevoCarrito);
      localStorage.setItem('carrito', JSON.stringify(nuevoCarrito));
    }
  };

  const eliminarProducto = async (id) => {
    if (idCliente) {
      try {
        const response = await fetch('/leo/carrito/item', {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            cliente_id: idCliente,
            producto_id: id
          })
        });

        if (response.ok) {
          setCarrito(prev => prev.filter(item => (item.producto_id || item._id || item.id) !== id));
        } else {
          alert('Error al eliminar el producto del carrito.');
        }
      } catch (err) {
        console.error('Error al eliminar producto de MongoDB:', err);
      }
    } else {
      const nuevoCarrito = carrito.filter(item => (item.producto_id || item._id || item.id) !== id);
      setCarrito(nuevoCarrito);
      localStorage.setItem('carrito', JSON.stringify(nuevoCarrito));
    }
  };

  const vaciarCarrito = async () => {
    if (window.confirm('¿Estás seguro de que quieres vaciar el carrito?')) {
      if (idCliente) {
        try {
          const response = await fetch(`/leo/carrito/${idCliente}`, {
            method: 'DELETE'
          });

          if (response.ok) {
            setCarrito([]);
          } else {
            alert('Error al vaciar el carrito.');
          }
        } catch (err) {
          console.error('Error al vaciar carrito de MongoDB:', err);
        }
      } else {
        setCarrito([]);
        localStorage.removeItem('carrito');
      }
    }
  };

  const calcularTotal = () => {
    return carrito.reduce((total, item) => total + ((item.precio_unitario || item.precio_actual || item.precio || 0) * (item.cantidad || 1)), 0);
  };

  const handlePagar = async () => {
    if (!usuario || !idCliente) {
      alert('Debes iniciar sesión para proceder al pago.');
      navigate('/loginUsuario');
      return;
    }

    if (carrito.length === 0) {
      alert('Tu carrito está vacío.');
      return;
    }

    try {
      setLoadingCheckout(true);

      // Mapear los productos a los IDs correspondientes en PostgreSQL
      const productosPayload = carrito.map(item => {
        const sqlId = item.id_producto_sql;
        if (!sqlId) {
          throw new Error(`El producto "${item.nombre}" no tiene un ID SQL correspondiente.`);
        }
        return {
          id_producto: sqlId,
          cantidad: item.cantidad || 1
        };
      });

      const response = await fetch('/leo/pedidos/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          id_cliente: idCliente,
          id_usuario: usuario.id_usuario,
          productos: productosPayload
        })
      });

      const data = await response.json();

      if (response.ok && data.exito) {
        alert('¡Compra realizada con éxito! Tu orden ha sido registrada en PostgreSQL.');
        
        // Vaciar el carrito en MongoDB tras la compra exitosa
        await fetch(`/leo/carrito/${idCliente}`, {
          method: 'DELETE'
        });

        setCarrito([]);
      } else {
        alert(`Error al registrar el pedido: ${data.mensaje || 'Error desconocido'}`);
      }
    } catch (err) {
      console.error('Error en el checkout:', err);
      alert(`Error en el checkout: ${err.message}`);
    } finally {
      setLoadingCheckout(false);
    }
  };

  if (loading) {
    return (
      <>
        <MainHeader />
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando carrito...</span>
          </div>
        </div>
        <MainFooter />
      </>
    );
  }

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
                    {carrito.map((item) => {
                      const itemPrecio = item.precio_unitario || item.precio_actual || item.precio || 0;
                      const itemId = item.producto_id || item._id || item.id;
                      return (
                        <tr key={itemId} className="border-bottom">
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
                          <td className="text-center">${itemPrecio.toLocaleString('es-CL')}</td>
                          <td>
                            <div className="d-flex justify-content-center align-items-center gap-2">
                              <button className="btn btn-outline-secondary btn-cantidad" onClick={() => actualizarCantidad(itemId, -1)}>-</button>
                              <span className="fw-bold" style={{ width: '20px', textAlign: 'center' }}>{item.cantidad || 1}</span>
                              <button className="btn btn-outline-secondary btn-cantidad" onClick={() => actualizarCantidad(itemId, 1)}>+</button>
                            </div>
                          </td>
                          <td className="text-end fw-bold text-primary fs-5">
                            ${(itemPrecio * (item.cantidad || 1)).toLocaleString('es-CL')}
                          </td>
                          <td className="text-end">
                            <button className="btn btn-link text-danger p-0 ms-2" onClick={() => eliminarProducto(itemId)} title="Eliminar">
                              <i className="bi bi-trash-fill fs-5"></i>
                            </button>
                          </td>
                        </tr>
                      );
                    })}
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
                
                <button 
                  onClick={handlePagar} 
                  className="btn btn-primary w-100 py-3 fw-bold fs-5 shadow-sm JnsnButton rounded-pill"
                  disabled={loadingCheckout}
                >
                  {loadingCheckout ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Procesando...
                    </>
                  ) : (
                    'Proceder al Pago'
                  )}
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