import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import MainHeader from './components/header'
import MainFooter from './components/footer'

export default function RegistroUsuario() {
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    email: '',
    contraseña: '',
    rut: '',
    telefono: '',
    calle: '',
    numero: '',
    comuna: '',
    ciudad: '',
    region: '',
    codigoPostal: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const payload = {
      nombre: formData.nombre,
      apellido: formData.apellido,
      email: formData.email,
      contraseña: formData.contraseña,
      rut: formData.rut,
      telefono: formData.telefono || null,
      direccion: {
        calle: formData.calle,
        numero: formData.numero,
        comuna: formData.comuna,
        ciudad: formData.ciudad,
        region: formData.region,
        pais: 'Chile',
        codigo_postal: formData.codigoPostal || null
      }
    };

    try {
      const response = await fetch('/leo/auth/register-cliente', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok && data.exito) {
        alert('¡Usuario registrado exitosamente! Ya puedes iniciar sesión.');
        navigate('/loginUsuario');
      } else {
        setError(data.mensaje || 'Error al registrar usuario');
      }
    } catch (err) {
      setError('Ocurrió un error de red. Inténtalo de nuevo.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <MainHeader />
      <div className="container my-5 d-flex justify-content-center">
        <div className="card shadow-sm p-4 border-0 auth-card-container-wide">
          <h2 className="text-center mb-4 fw-bold text-primary">Crear Cuenta</h2>
          
          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <h5 className="mb-3 text-secondary border-bottom pb-2 fw-bold">1. Datos Personales</h5>
            
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label fw-bold text-muted">Nombre</label>
                <input
                  type="text"
                  name="nombre"
                  className="form-control bg-light"
                  placeholder="Ej: Juan"
                  value={formData.nombre}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label fw-bold text-muted">Apellido</label>
                <input
                  type="text"
                  name="apellido"
                  className="form-control bg-light"
                  placeholder="Ej: Pérez"
                  value={formData.apellido}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label fw-bold text-muted">RUT</label>
                <input
                  type="text"
                  name="rut"
                  className="form-control bg-light"
                  placeholder="Ej: 12.345.678-9"
                  value={formData.rut}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label fw-bold text-muted">Teléfono</label>
                <input
                  type="text"
                  name="telefono"
                  className="form-control bg-light"
                  placeholder="Ej: +56912345678"
                  value={formData.telefono}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label fw-bold text-muted">Correo Electrónico</label>
                <input
                  type="email"
                  name="email"
                  className="form-control bg-light"
                  placeholder="juan@correo.com"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label fw-bold text-muted">Contraseña</label>
                <input
                  type="password"
                  name="contraseña"
                  className="form-control bg-light"
                  placeholder="********"
                  value={formData.contraseña}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <h5 className="my-3 text-secondary border-bottom pb-2 fw-bold">2. Dirección de Envío</h5>

            <div className="row">
              <div className="col-md-8 mb-3">
                <label className="form-label fw-bold text-muted">Calle</label>
                <input
                  type="text"
                  name="calle"
                  className="form-control bg-light"
                  placeholder="Ej: Av. Providencia"
                  value={formData.calle}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-4 mb-3">
                <label className="form-label fw-bold text-muted">Número</label>
                <input
                  type="text"
                  name="numero"
                  className="form-control bg-light"
                  placeholder="Ej: 1234"
                  value={formData.numero}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label fw-bold text-muted">Comuna</label>
                <input
                  type="text"
                  name="comuna"
                  className="form-control bg-light"
                  placeholder="Ej: Providencia"
                  value={formData.comuna}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label fw-bold text-muted">Ciudad</label>
                <input
                  type="text"
                  name="ciudad"
                  className="form-control bg-light"
                  placeholder="Ej: Santiago"
                  value={formData.ciudad}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label fw-bold text-muted">Región</label>
                <input
                  type="text"
                  name="region"
                  className="form-control bg-light"
                  placeholder="Ej: Metropolitana"
                  value={formData.region}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label fw-bold text-muted">Código Postal</label>
                <input
                  type="text"
                  name="codigoPostal"
                  className="form-control bg-light"
                  placeholder="Ej: 7500000"
                  value={formData.codigoPostal}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary w-100 py-3 fw-bold JnsnButton rounded-pill mt-4"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Registrando...
                </>
              ) : (
                'Registrarse'
              )}
            </button>
          </form>

          <div className="text-center mt-3">
            <span className="text-muted">¿Ya tienes cuenta? </span>
            <Link to="/loginUsuario" className="fw-bold text-decoration-none text-primary">
              Inicia sesión aquí
            </Link>
          </div>
        </div>
      </div>
      <MainFooter />
    </>
  );
}
