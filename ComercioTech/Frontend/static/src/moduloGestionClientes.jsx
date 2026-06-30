import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminHeader from './components/adminHeader';
import MainFooter from './components/footer';

export default function ModuloGestionClientes() {
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const cargarClientes = async () => {
    setLoading(true);
    setError('');
    const token = localStorage.getItem('token');

    try {
      const response = await fetch('/leo/clientes/admin-list', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok && data.exito) {
        setClientes(data.clientes || []);
      } else {
        setError(data.mensaje || 'Error al obtener clientes.');
        if (response.status === 403 || response.status === 401) {
          navigate('/');
        }
      }
    } catch (err) {
      console.error(err);
      setError('Error de red al listar los clientes.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarClientes();
  }, []);

  const toggleActivo = async (idCliente) => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`/leo/clientes/${idCliente}/desactivar`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok && data.exito) {
        // Actualizar la lista en local
        setClientes(prev => prev.map(c => 
          c.id_cliente === idCliente ? { ...c, activo_usuario: data.activo_usuario } : c
        ));
      } else {
        alert(data.mensaje || 'Error al cambiar estado.');
      }
    } catch (err) {
      console.error(err);
      alert('Error de red al modificar estado.');
    }
  };

  const eliminarCliente = async (idCliente) => {
    if (!window.confirm('¿Está seguro de que desea eliminar permanentemente este cliente de PostgreSQL?')) {
      return;
    }

    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`/leo/clientes/${idCliente}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok && data.exito) {
        alert(data.mensaje);
        setClientes(prev => prev.filter(c => c.id_cliente !== idCliente));
      } else {
        // Muestra el error de consistencia ACID / Derecho al olvido
        alert(data.mensaje || 'Error al eliminar.');
      }
    } catch (err) {
      console.error(err);
      alert('Error de red al eliminar.');
    }
  };

  if (loading) {
    return (
      <>
        <AdminHeader />
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando gestión...</span>
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
        <h1 className="text-center py-3 mb-4 rounded page_title">Gestión de Clientes</h1>

        {error && <div className="alert alert-danger">{error}</div>}

        <div className="bg-white rounded shadow-sm p-4 border border-light">
          <h5 className="fw-bold mb-4 border-bottom pb-2 text-dark">Clientes Registrados (PostgreSQL)</h5>
          
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light">
                <tr>
                  <th scope="col" className="px-3">ID</th>
                  <th scope="col">Nombre</th>
                  <th scope="col">Email</th>
                  <th scope="col">RUT</th>
                  <th scope="col">Teléfono</th>
                  <th scope="col" className="text-center">Estado Acceso</th>
                  <th scope="col" className="text-center">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {clientes.map((c) => (
                  <tr key={c.id_cliente}>
                    <td className="px-3 fw-bold">#{c.id_cliente}</td>
                    <td>{c.nombre}</td>
                    <td>{c.email}</td>
                    <td>{c.rut}</td>
                    <td>{c.telefono || 'Sin registrar'}</td>
                    <td className="text-center">
                      <span className={`badge ${c.activo_usuario ? 'bg-success' : 'bg-danger'}`}>
                        {c.activo_usuario ? 'ACTIVO' : 'BLOQUEADO'}
                      </span>
                    </td>
                    <td className="text-center">
                      <button 
                        className={`btn btn-sm ${c.activo_usuario ? 'btn-warning' : 'btn-success'} rounded-pill px-3 me-2 fw-bold`}
                        onClick={() => toggleActivo(c.id_cliente)}
                      >
                        {c.activo_usuario ? 'Bloquear' : 'Desbloquear'}
                      </button>
                      <button 
                        className="btn btn-sm btn-outline-danger rounded-pill px-3 fw-bold"
                        onClick={() => eliminarCliente(c.id_cliente)}
                      >
                        Eliminar
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
