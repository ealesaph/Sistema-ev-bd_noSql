import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminHeader from './components/adminHeader';
import MainFooter from './components/footer';

export default function ModuloStock() {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [ajustandoProducto, setAjustandoProducto] = useState(null);
  const [cantidadAjuste, setCantidadAjuste] = useState(0);
  const navigate = useNavigate();

  const cargarStock = async () => {
    setLoading(true);
    setError('');
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('/leo/productos/admin/stock', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok && data.exito) {
        setProductos(data.productos || []);
      } else {
        setError(data.mensaje || 'Error al obtener inventario.');
        if (response.status === 403 || response.status === 401) {
          navigate('/');
        }
      }
    } catch (err) {
      console.error(err);
      setError('Error de red al listar inventario.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarStock();
  }, []);

  const aplicarAjuste = async () => {
    if (cantidadAjuste === 0) {
      alert('La cantidad de cambio no puede ser 0.');
      return;
    }

    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`/leo/productos/${ajustandoProducto.id_producto}/stock`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ cantidad_cambio: cantidadAjuste })
      });
      const data = await response.json();
      if (response.ok && data.exito) {
        alert('Stock e informe de pago a proveedor actualizados correctamente en transacción ACID.');
        // Actualizar la lista
        setProductos(prev => prev.map(p => 
          p.id_producto === ajustandoProducto.id_producto ? { ...p, stock: data.nuevo_stock } : p
        ));
        setAjustandoProducto(null);
        setCantidadAjuste(0);
      } else {
        alert(data.mensaje || 'Error al ajustar stock.');
      }
    } catch (err) {
      console.error(err);
      alert('Error de red al ajustar stock.');
    }
  };

  const criticosCount = productos.filter(p => p.stock < 10).length;

  if (loading) {
    return (
      <>
        <AdminHeader />
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando inventario...</span>
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
        <h1 className="text-center py-3 mb-4 rounded page_title">Control de Stock e Inventario</h1>

        {error && <div className="alert alert-danger">{error}</div>}

        {/* Indicadores de Stock */}
        <div className="row g-4 mb-4">
          <div className="col-md-6 col-lg-4">
            <div className="p-3 bg-white shadow-sm rounded border-start border-4 border-primary">
              <span className="text-muted small uppercase d-block fw-semibold mb-1">Total SKU Activos</span>
              <span className="fs-3 fw-bold text-dark">{productos.length}</span>
            </div>
          </div>
          <div className="col-md-6 col-lg-4">
            <div className={`p-3 bg-white shadow-sm rounded border-start border-4 ${criticosCount > 0 ? 'border-danger' : 'border-success'}`}>
              <span className="text-muted small uppercase d-block fw-semibold mb-1">Productos Stock Crítico (&lt; 10)</span>
              <span className={`fs-3 fw-bold ${criticosCount > 0 ? 'text-danger animate-pulse' : 'text-success'}`}>{criticosCount}</span>
            </div>
          </div>
          <div className="col-md-6 col-lg-4">
            <div className="p-3 bg-white shadow-sm rounded border-start border-4 border-info">
              <span className="text-muted small uppercase d-block fw-semibold mb-1">Unidades en Bodega</span>
              <span className="fs-3 fw-bold text-dark">{productos.reduce((acc, p) => acc + p.stock, 0).toLocaleString('es-CL')}</span>
            </div>
          </div>
        </div>

        {/* Modal/Formulario de Ajuste rápido */}
        {ajustandoProducto && (
          <div className="card mb-4 shadow border border-primary animate-fade-in">
            <div className="card-header bg-primary text-white py-3 fw-bold">
              Ajustar Stock de: {ajustandoProducto.nombre} (Stock Actual: {ajustandoProducto.stock})
            </div>
            <div className="card-body p-4 bg-light">
              <div className="row align-items-center g-3">
                <div className="col-md-6">
                  <label className="form-label fw-semibold text-dark">Cantidad a Ajustar (Suma o Resta)</label>
                  <div className="input-group">
                    <button className="btn btn-danger fw-bold" onClick={() => setCantidadAjuste(prev => prev - 1)}>-</button>
                    <input 
                      type="number" 
                      className="form-control text-center fw-bold fs-5"
                      value={cantidadAjuste}
                      onChange={(e) => setCantidadAjuste(parseInt(e.target.value) || 0)}
                    />
                    <button className="btn btn-success fw-bold" onClick={() => setCantidadAjuste(prev => prev + 1)}>+</button>
                  </div>
                  <span className="form-text text-muted">
                    Los valores positivos aumentan el stock y crean una cuenta por pagar al proveedor. Los valores negativos descuentan stock.
                  </span>
                </div>
                <div className="col-md-6 text-md-end">
                  <button className="btn btn-primary rounded-pill px-4 fw-bold me-2" onClick={aplicarAjuste}>
                    Guardar Cambios
                  </button>
                  <button className="btn btn-outline-secondary rounded-pill px-4" onClick={() => { setAjustandoProducto(null); setCantidadAjuste(0); }}>
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded shadow-sm p-4 border border-light">
          <h5 className="fw-bold mb-4 border-bottom pb-2 text-dark">Catálogo e Inventario</h5>
          
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light">
                <tr>
                  <th scope="col" className="px-3">ID</th>
                  <th scope="col">Nombre de Producto</th>
                  <th scope="col">Proveedor</th>
                  <th scope="col" className="text-end">Precio Base</th>
                  <th scope="col" className="text-center">Stock Actual</th>
                  <th scope="col" className="text-center">Estado Stock</th>
                  <th scope="col" className="text-center">Acción</th>
                </tr>
              </thead>
              <tbody>
                {productos.map((p) => (
                  <tr key={p.id_producto} className={p.stock < 10 ? 'table-danger-subtle' : ''}>
                    <td className="px-3 fw-bold">#{p.id_producto}</td>
                    <td className="fw-semibold text-dark">{p.nombre}</td>
                    <td>{p.proveedor}</td>
                    <td className="text-end fw-semibold">${p.precio.toLocaleString('es-CL')}</td>
                    <td className="text-center fw-bold fs-5">{p.stock}</td>
                    <td className="text-center">
                      <span className={`badge ${p.stock === 0 ? 'bg-danger' : p.stock < 10 ? 'bg-warning text-dark' : 'bg-success'}`}>
                        {p.stock === 0 ? 'SIN STOCK' : p.stock < 10 ? 'STOCK CRÍTICO' : 'DISPONIBLE'}
                      </span>
                    </td>
                    <td className="text-center">
                      <button 
                        className="btn btn-sm btn-primary rounded-pill px-3 fw-bold"
                        onClick={() => { setAjustandoProducto(p); setCantidadAjuste(0); }}
                      >
                        Ajustar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <MainFooter />
    </>
  );
}
