import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainHeader from './components/header';
import MainFooter from './components/footer';
import Landing from './Landing';

function App() {
  const navigate = useNavigate();

  useEffect(() => {
    const usuarioStr = localStorage.getItem('usuario');
    if (usuarioStr) {
      try {
        const usuario = JSON.parse(usuarioStr);
        if (usuario.rol === 'Administrador') {
          // Redirigir al panel de administración si es admin
          navigate('/admin/clientes', { replace: true });
        }
      } catch (e) {
        console.error(e);
      }
    }
  }, [navigate]);

  return (
    <>
      <MainHeader />
      <Landing />
      <MainFooter />
    </>
  );
}

export default App;
