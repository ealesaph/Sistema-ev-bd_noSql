import MainHeader from './components/header'
import MainFooter from './components/footer'

export default function Computadores() {
  return (
    <>
      <MainHeader />
      <div className="container page_container">
        <h1 className="text-center py-3 mb-5 rounded page_title">Computadores</h1>
      </div>
      <p>Contenido de Computadores próximamente...</p>
      <MainFooter />
    </>
  )
}