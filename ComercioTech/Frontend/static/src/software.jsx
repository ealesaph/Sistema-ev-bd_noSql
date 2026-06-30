import MainHeader from './components/header'
import MainFooter from './components/footer'
import ListaProductosPorCategoria from './components/ListaProductosPorCategoria'

export default function Software() {
  return (
    <>
      <MainHeader />
      <div className="container page_container">
        <h1 className="text-center py-3 mb-5 rounded page_title">Software</h1>
      </div>
      <ListaProductosPorCategoria etiqueta="software" />
      <MainFooter />
    </>
  )
}