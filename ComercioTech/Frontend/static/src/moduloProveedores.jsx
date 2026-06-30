import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminHeader from './components/adminHeader';
import MainFooter from './components/footer';

export default function ModuloProveedores() {
  const [proveedores, setProveedores] = useState([]);
  const [pagos, setPagos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const cargarDatos = async () => {
    setLoading(true);
    setError('');
    const token = localStorage.getItem('token');
    try {
      // 1. Cargar proveedores
      const resProv = await fetch('/leo/productos/proveedores', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const dataProv = await resProv.json();

      // 2. Cargar pagos
      const resPagos = await fetch('/leo/productos/proveedores/pagos', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const dataPagos = await resPagos.json();

      if (resProv.ok && dataProv.exito && resPagos.ok && dataPagos.exito) {
        setProveedores(dataProv.proveedores || []);
        setPagos(dataPagos.pagos || []);
      } else {
        setError('Error al obtener información de proveedores/pagos.');
        if (resProv.status === 403 || resProv.status === 401) {
          navigate('/');
        }
      }
    } catch (err) {
      console.error(err);
      setError('Error de red al consultar proveedores.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const realizarPago = async (idPago) => {
    if (!window.confirm('¿Está seguro de que desea registrar este pago como PAGADO en PostgreSQL?')) {
      return;
    }

    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`/leo/productos/proveedores/pagos/${idPago}/pagar`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok && data.exito) {
        alert(data.mensaje);
        // Actualizar lista local
        setPagos(prev => prev.map(p => 
          p.id_pago === idPago ? { ...p, estado: 'PAGADO', fecha_pago: new Date().toISOString().substring(0, 10) } : p
        ));
      } else {
        alert(data.mensaje || 'Error al procesar el pago.');
      }
    } catch (err) {
      console.error(err);
      alert('Error de red al procesar el pago.');
    }
  };

  if (loading) {
    return (
      <>
        <AdminHeader />
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando proveedores...</span>
          </div>
        </div>
        <MainFooter />
      </>
    );
  }

  return (
    <>
      <AdminHeader />
      <div className="container my-5" style={{ minHeight: '60vh' }}>
        <h1 className="text-center py-3 mb-4 rounded page_title">Módulo de Proveedores y Cuentas por Pagar</h1>

        {error && <div className="alert alert-danger">{error}</div>}

        <div className="row g-4">
          {/* Listado de Proveedores */}
          <div className="col-lg-5">
            <div className="bg-white rounded shadow-sm p-4 border border-light">
              <h5 className="fw-bold mb-4 border-bottom pb-2 text-dark">Proveedores Autorizados</h5>
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th scope="col" className="px-3">Proveedor</th>
                      <th scope="col">RUT</th>
                      <th scope="col">Email / Teléfono</th>
                    </tr>
                  </thead>
                  <tbody>
                    {proveedores.map((p) => (
                      <tr key={p.id_proveedor}>
                        <td className="px-3 fw-bold text-dark">{p.nombre}</td>
                        <td className="small">{p.rut}</td>
                        <td className="small text-muted">
                          <div>{p.email}</div>
                          <div>{p.telefono}</div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Historial de Pagos y Cuentas por Pagar */}
          <div className="col-lg-7">
            <div className="bg-white rounded shadow-sm p-4 border border-light">
              <h5 className="fw-bold mb-4 border-bottom pb-2 text-dark">Historial de Pagos / Abastecimiento (ACID)</h5>
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th scope="col" className="px-3">ID</th>
                      <th scope="col">Proveedor</th>
                      <th scope="col" className="text-end">Monto</th>
                      <th scope="col">Estado</th>
                      <th scope="col" className="text-center">Acción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pagos.length === 0 ? (
                      <tr>
                        <td colSpan="5" className="text-center py-4 text-muted">No se registran transacciones de pago a proveedores.</td>
                      </tr>
                    ) : (
                      pagos.map((p) => (
                        <tr key={p.id_pago} className={p.estado === 'PENDIENTE' ? 'table-warning-subtle' : ''}>
                          <td className="px-3 fw-bold">#{p.id_pago}</td>
                          <td>
                            <div className="fw-semibold text-dark">{p.proveedor}</div>
                            <div className="small text-muted" style={{ fontSize: '0.75rem' }}>{p.referencia}</div>
                          </td>
                          <td className="text-end fw-bold text-dark">${p.monto.toLocaleString('es-CL')}</td>
                          <td>
                            <span className={`badge ${p.estado === 'PAGADO' ? 'bg-success' : 'bg-warning text-dark'}`}>
                              {p.estado}
                            </span>
                            {p.fecha_pago && <div className="small text-muted" style={{ fontSize: '0.7rem' }}>Pagado: {p.fecha_pago}</div>}
                          </td>
                          <td className="text-center">
                            {p.estado === 'PENDIENTE' ? (
                              <button 
                                className="btn btn-sm btn-success rounded-pill px-3 fw-bold"
                                onClick={() => realizarPago(p.id_pago)}
                              >
                                Pagar
                              </button>
                            ) : (
                              <span className="text-muted small">Liquidado</span>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
      <MainFooter />
    </>
  );
}
