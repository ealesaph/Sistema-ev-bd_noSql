import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminHeader from './components/adminHeader';
import MainFooter from './components/footer';

export default function ModuloFacturacion() {
  const [facturas, setFacturas] = useState([]);
  const [reporte, setReporte] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const cargarDatos = async () => {
    setLoading(true);
    setError('');
    const token = localStorage.getItem('token');
    try {
      // 1. Cargar facturas
      const resFac = await fetch('/leo/pedidos/facturas', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const dataFac = await resFac.json();
      
      // 2. Cargar reporte contable
      const resRep = await fetch('/leo/pedidos/reporte-contable', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const dataRep = await resRep.json();

      if (resFac.ok && dataFac.exito && resRep.ok && dataRep.exito) {
        setFacturas(dataFac.facturas || []);
        setReporte(dataRep.reporte);
      } else {
        setError('Error al obtener datos contables/facturación.');
        if (resFac.status === 403 || resFac.status === 401) {
          navigate('/');
        }
      }
    } catch (err) {
      console.error(err);
      setError('Error de red al consultar el módulo financiero.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  if (loading) {
    return (
      <>
        <AdminHeader />
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando contabilidad...</span>
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
        <h1 className="text-center py-3 mb-4 rounded page_title">Módulo Contable y de Facturación</h1>

        {error && <div className="alert alert-danger">{error}</div>}

        {/* Indicadores Financieros */}
        {reporte && (
          <div className="row g-4 mb-5">
            <div className="col-md-6 col-lg-3">
              <div className="p-3 bg-white shadow-sm rounded border-start border-4 border-success">
                <span className="text-muted small uppercase d-block fw-semibold mb-1">Ventas Totales Brutas</span>
                <span className="fs-3 fw-bold text-success">${reporte.total_ventas.toLocaleString('es-CL')}</span>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="p-3 bg-white shadow-sm rounded border-start border-4 border-primary">
                <span className="text-muted small uppercase d-block fw-semibold mb-1">Ventas Netas (Sin IVA)</span>
                <span className="fs-3 fw-bold text-primary">${reporte.total_neto.toLocaleString('es-CL')}</span>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="p-3 bg-white shadow-sm rounded border-start border-4 border-warning">
                <span className="text-muted small uppercase d-block fw-semibold mb-1">Impuesto IVA Recaudado (19%)</span>
                <span className="fs-3 fw-bold text-warning">${reporte.total_impuestos.toLocaleString('es-CL')}</span>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="p-3 bg-white shadow-sm rounded border-start border-4 border-danger">
                <span className="text-muted small uppercase d-block fw-semibold mb-1">Cuentas por Pagar (Proveedores)</span>
                <span className="fs-3 fw-bold text-danger">${reporte.cuentas_por_pagar.toLocaleString('es-CL')}</span>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded shadow-sm p-4 border border-light">
          <h5 className="fw-bold mb-4 border-bottom pb-2 text-dark">Registro de Facturación Electrónica a Clientes</h5>
          
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light">
                <tr>
                  <th scope="col" className="px-3">Factura N°</th>
                  <th scope="col">Cliente</th>
                  <th scope="col">Fecha Emisión</th>
                  <th scope="col" className="text-end">Monto Neto</th>
                  <th scope="col" className="text-end">Impuesto (19%)</th>
                  <th scope="col" className="text-end">Monto Total</th>
                  <th scope="col" className="text-center">Estado</th>
                </tr>
              </thead>
              <tbody>
                {facturas.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="text-center py-4 text-muted">No se registran facturas emitidas en el sistema.</td>
                  </tr>
                ) : (
                  facturas.map((f) => (
                    <tr key={f.id_factura}>
                      <td className="px-3 fw-bold text-primary">{f.numero_factura}</td>
                      <td>{f.cliente}</td>
                      <td>{f.fecha_emision.substring(0, 16)}</td>
                      <td className="text-end">${f.monto_neto.toLocaleString('es-CL')}</td>
                      <td className="text-end">${f.impuesto.toLocaleString('es-CL')}</td>
                      <td className="text-end fw-bold text-dark">${f.monto_total.toLocaleString('es-CL')}</td>
                      <td className="text-center">
                        <span className={`badge ${f.estado === 'PAGADA' ? 'bg-success' : f.estado === 'EMITIDA' ? 'bg-info' : 'bg-danger'}`}>
                          {f.estado}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <MainFooter />
    </>
  );
}
