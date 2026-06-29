import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import MainHeader from './components/header'
import MainFooter from './components/footer'

export default function LoginUsuario() {
  const [email, setEmail] = useState('');
  const [contraseña, setContraseña] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/leo/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, contraseña })
      });

      const data = await response.json();

      if (response.ok && data.exito) {
        // Guardar token e info en localStorage
        localStorage.setItem('token', data.token);
        localStorage.setItem('usuario', JSON.stringify(data.usuario));
        
        // Alertas de éxito y redirección
        alert('¡Inicio de sesión exitoso!');
        navigate('/');
      } else {
        setError(data.mensaje || 'Error al iniciar sesión');
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
        <div className="card shadow-sm p-4 border-0 auth-card-container">
          <h2 className="text-center mb-4 fw-bold text-primary">Iniciar Sesión</h2>
          
          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label fw-bold text-secondary">Correo Electrónico</label>
              <div className="input-group">
                <span className="input-group-text bg-light border-end-0">
                  <i className="bi bi-envelope-fill text-muted"></i>
                </span>
                <input
                  type="email"
                  className="form-control border-start-0 bg-light"
                  placeholder="ejemplo@correo.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="mb-4">
              <label className="form-label fw-bold text-secondary">Contraseña</label>
              <div className="input-group">
                <span className="input-group-text bg-light border-end-0">
                  <i className="bi bi-lock-fill text-muted"></i>
                </span>
                <input
                  type="password"
                  className="form-control border-start-0 bg-light"
                  placeholder="********"
                  value={contraseña}
                  onChange={(e) => setContraseña(e.target.value)}
                  required
                />
              </div>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary w-100 py-2 fw-bold JnsnButton rounded-pill mb-3"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Ingresando...
                </>
              ) : (
                'Ingresar'
              )}
            </button>
          </form>

          <div className="text-center mt-3">
            <span className="text-muted">¿No tienes cuenta? </span>
            <Link to="/registroUsuario" className="fw-bold text-decoration-none text-primary">
              Regístrate aquí
            </Link>
          </div>
        </div>
      </div>
      <MainFooter />
    </>
  );
}