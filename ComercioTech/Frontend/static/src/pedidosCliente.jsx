import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import MainHeader from './components/header';
import MainFooter from './components/footer';

export default function PedidosCliente() {
  const [pedidos, setPedidos] = useState([]);
  const [pedidoDetalle, setPedidoDetalle] = useState(null);
  const [pedidoSeleccionadoId, setPedidoSeleccionadoId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingDetalle, setLoadingDetalle] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const cargarPedidos = async () => {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('token');
      
      if (!token) {
        setError('No has iniciado sesión.');
        setLoading(false);
        navigate('/loginUsuario');
        return;
      }

      try {
        const response = await fetch('/leo/pedidos/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        const data = await response.json();

        if (response.ok && data.exito) {
          setPedidos(data.pedidos || []);
        } else {
          setError(data.mensaje || 'Error al cargar los pedidos.');
        }
      } catch (err) {
        console.error(err);
        setError('Error de red al cargar el historial de pedidos.');
      } finally {
        setLoading(false);
      }
    };

    cargarPedidos();
  }, [navigate]);

  const verDetalle = async (idPedido) => {
    setPedidoSeleccionadoId(idPedido);
    setLoadingDetalle(true);
    setPedidoDetalle(null);
    const token = localStorage.getItem('token');

    try {
      const response = await fetch(`/leo/pedidos/${idPedido}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (response.ok && data.exito) {
        setPedidoDetalle(data.pedido);
      } else {
        alert(data.mensaje || 'Error al obtener detalles del pedido.');
      }
    } catch (err) {
      console.error(err);
      alert('Error de red al consultar el detalle del pedido.');
    } finally {
      setLoadingDetalle(false);
    }
  };

  const getBadgeClass = (estado) => {
    switch (estado) {
      case 'PENDIENTE': return 'bg-warning text-dark';
      case 'CONFIRMADO': return 'bg-info text-dark';
      case 'ENVIADO': return 'bg-primary';
      case 'ENTREGADO': return 'bg-success';
      case 'CANCELADO': return 'bg-danger';
      default: return 'bg-secondary';
    }
  };

  if (loading) {
    return (
      <>
        <MainHeader />
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando pedidos...</span>
          </div>
        </div>
        <MainFooter />
      </>
    );
  }

  return (
    <>
      <MainHeader />
      <div className="container my-5" style={{ minHeight: '60vh' }}>
        <h1 className="text-center py-3 mb-4 rounded page_title">Historial de Pedidos</h1>

        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        {pedidos.length === 0 ? (
          <div className="text-center py-5 bg-white rounded shadow-sm border-top border-4 border-primary">
            <i className="bi bi-receipt-cutoff text-muted" style={{ fontSize: '4rem' }}></i>
            <h3 className="mt-3 text-muted">Aún no tienes pedidos registrados</h3>
            <p className="text-muted mb-4">Tus compras relacionales aparecerán listadas aquí.</p>
            <Link to="/" className="btn btn-primary px-4 fw-bold">Ir a Comprar</Link>
          </div>
        ) : (
          <div className="row">
            {/* Listado de Pedidos (Master) */}
            <div className="col-lg-7">
              <div className="bg-white rounded shadow-sm p-4 border border-light">
                <h5 className="fw-bold mb-4 border-bottom pb-2 text-dark">Mis Compras</h5>
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        <th scope="col" className="px-3">Pedido ID</th>
                        <th scope="col">Fecha</th>
                        <th scope="col" className="text-center">Estado</th>
                        <th scope="col" className="text-end">Total</th>
                        <th scope="col" className="text-center">Acción</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pedidos.map((p) => (
                        <tr 
                          key={p.id_pedido} 
                          className={pedidoSeleccionadoId === p.id_pedido ? 'table-primary-subtle' : ''}
                          style={{ cursor: 'pointer' }}
                          onClick={() => verDetalle(p.id_pedido)}
                        >
                          <td className="px-3 fw-bold">#{p.id_pedido}</td>
                          <td>{p.fecha_pedido.substring(0, 10)}</td>
                          <td className="text-center">
                            <span className={`badge ${getBadgeClass(p.estado)}`}>
                              {p.estado}
                            </span>
                          </td>
                          <td className="text-end fw-bold">${p.total.toLocaleString('es-CL')}</td>
                          <td className="text-center">
                            <button 
                              className="btn btn-sm btn-outline-primary rounded-pill px-3"
                              onClick={(e) => {
                                e.stopPropagation();
                                verDetalle(p.id_pedido);
                              }}
                            >
                              Detalle
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div className="col-lg-5 mt-4 mt-lg-0">
              <div className="bg-white rounded shadow-sm p-4 border border-light sticky-top" style={{ top: '120px' }}>
                <h5 className="fw-bold mb-4 border-bottom pb-2 text-dark">Detalle del Pedido</h5>

                {loadingDetalle && (
                  <div className="text-center py-5">
                    <div className="spinner-border spinner-border-sm text-primary" role="status">
                      <span className="visually-hidden">Cargando detalles...</span>
                    </div>
                  </div>
                )}

                {!loadingDetalle && !pedidoDetalle && (
                  <div className="text-center py-5 text-muted">
                    <i className="bi bi-arrow-left-right fs-2 mb-2 d-block"></i>
                    <p className="small mb-0">Selecciona un pedido de la lista para examinar sus productos y valores.</p>
                  </div>
                )}

                {!loadingDetalle && pedidoDetalle && (
                  <div>
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <span className="fw-bold text-dark fs-5">Pedido #{pedidoDetalle.id_pedido}</span>
                      <span className={`badge ${getBadgeClass(pedidoDetalle.estado)}`}>
                        {pedidoDetalle.estado}
                      </span>
                    </div>

                    <div className="small text-muted mb-4">
                      <div className="mb-1"><strong>Fecha de Compra:</strong> {pedidoDetalle.fecha_pedido}</div>
                      <div><strong>Medio de Pago:</strong> Tarjeta de Crédito (Simulado)</div>
                    </div>

                    <div className="border rounded overflow-hidden mb-4">
                      <table className="table table-sm table-borderless align-middle mb-0">
                        <thead className="bg-light border-bottom text-muted" style={{ fontSize: '0.8rem' }}>
                          <tr>
                            <th scope="col" className="ps-3 py-2">Producto</th>
                            <th scope="col" className="text-center py-2">Cant.</th>
                            <th scope="col" className="text-end pe-3 py-2">Precio</th>
                          </tr>
                        </thead>
                        <tbody style={{ fontSize: '0.9rem' }}>
                          {pedidoDetalle.detalles.map((d) => (
                            <tr key={d.id_detalle} className="border-bottom-subtle">
                              <td className="ps-3 py-2 text-dark fw-semibold">
                                <Link to={`/producto/${d.id_producto}`} className="text-decoration-none text-dark">
                                  {d.nombre_producto}
                                </Link>
                              </td>
                              <td className="text-center py-2">{d.cantidad}</td>
                              <td className="text-end pe-3 py-2 fw-bold">${d.precio_unitario.toLocaleString('es-CL')}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    <div className="d-flex justify-content-between align-items-end pt-2">
                      <span className="fw-bold text-secondary">Total Pagado:</span>
                      <span className="fw-bold text-primary fs-3">${pedidoDetalle.total.toLocaleString('es-CL')}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
      <MainFooter />
    </>
  );
}
