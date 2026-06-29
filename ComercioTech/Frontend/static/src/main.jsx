import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import Computadores from './computadores.jsx'
import HogarOficina from './hogarOficina.jsx'
import Perifericos from './perifericos.jsx'
import Componentes from './componentes.jsx'
import ConectividadRedes from './conectividadRedes.jsx'
import Electronica from './electronica.jsx'
import Software from './software.jsx'
import LoginUsuario from './loginUsuario.jsx'
import RegistroUsuario from './registroUsuario.jsx'
import CarritoCliente from './carritoCliente.jsx'
import DetalleProducto from './detalleProducto.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/computadores" element={<Computadores />} />
        <Route path="/hogarOficina" element={<HogarOficina />} />
        <Route path="/perifericos" element={<Perifericos />} />
        <Route path="/componentes" element={<Componentes />} />
        <Route path="/conectividadRedes" element={<ConectividadRedes />} />
        <Route path="/electronica" element={<Electronica />} />
        <Route path="/software" element={<Software />} />
        <Route path="/loginUsuario" element={<LoginUsuario />} />
        <Route path="/registroUsuario" element={<RegistroUsuario />} />
        <Route path="/carritoCliente" element={
          <ProtectedRoute>
            <CarritoCliente />
          </ProtectedRoute>
        } />
        <Route path="/producto/:id" element={<DetalleProducto />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)

/*se debe instalar con: npm install react-router-dom para funcionamiento del proyecto*/