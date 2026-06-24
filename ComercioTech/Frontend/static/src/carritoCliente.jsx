import MainHeader from './components/header'
import MainFooter from './components/footer'

export default function CarritoCliente() {
  return (
    <>
      <MainHeader />
      <div className="container page_container">
        <h1 className="text-center py-3 mb-5 rounded page_title">Carrito de Compras</h1>
      </div>
      <p>Contenido de Carrito próximamente...</p>
      <MainFooter />
    </>
  )
}