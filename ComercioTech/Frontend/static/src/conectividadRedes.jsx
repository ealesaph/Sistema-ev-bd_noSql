import MainHeader from './components/header'
import MainFooter from './components/footer'
import ListaProductosPorCategoria from './components/ListaProductosPorCategoria'

export default function ConectividadRedes() {
  return (
    <>
      <MainHeader />
      <div className="container page_container">
        <h1 className="text-center py-3 mb-5 rounded page_title">Conectividad / Redes</h1>
      </div>
      <ListaProductosPorCategoria etiqueta="conectividadRedes" />
      <MainFooter />
    </>
  )
}