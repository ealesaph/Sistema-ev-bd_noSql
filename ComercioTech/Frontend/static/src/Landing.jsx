import { useNavigate } from 'react-router-dom';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <main className="landing-page">
      <section className="landing-hero">
        <div className="landing-hero-content">
          <h1 className="landing-title">Compra tecnología con confianza</h1>
          <p className="landing-subtitle">
            Descubre equipos, accesorios y soluciones para tu hogar o negocio con precios competitivos,
            asesoría cercana y envío rápido.
          </p>
          <div className="d-flex justify-content-center gap-3">
            <button className="landing-cta-btn" onClick={() => navigate('/registroUsuario')}>Crear cuenta</button>
            <button className="landing-cta-btn" onClick={() => navigate('/componentes')}>Ver productos</button>
          </div>
        </div>
      </section>

      <section className="landing-testimonials">
        <h2 className="landing-section-title">¿Por qué elegir ComercioTech?</h2>
        <div className="testimonials-grid">
          <div className="testimonial-card">
            <p className="testimonial-name">Variedad</p>
            <p className="testimonial-body">Encuentra hardware, software, redes y accesorios en un solo lugar.</p>
          </div>

          <div className="testimonial-card">
            <p className="testimonial-name">Asesoría</p>
            <p className="testimonial-body">Nuestro equipo te acompaña para elegir lo más adecuado para tus necesidades.</p>
          </div>

          <div className="testimonial-card">
            <p className="testimonial-name">Conveniencia</p>
            <p className="testimonial-body">Compra desde cualquier dispositivo y revisa tus pedidos con facilidad.</p>
          </div>
        </div>
      </section>

      <section className="landing-testimonials">
        <h2 className="landing-section-title">Lo que dicen nuestros clientes</h2>
        <div className="testimonials-grid">
          <div className="testimonial-card">
            <div className="testimonial-header">
              <p className="testimonial-name">María López</p>
              <p className="testimonial-role">Compradora recurrente</p>
            </div>
            <p className="testimonial-body">Gran variedad y excelente atención. Encontré todo lo que necesitaba para armar mi PC y la entrega fue rápida.</p>
          </div>

          <div className="testimonial-card">
            <div className="testimonial-header">
              <p className="testimonial-name">Juan Pérez</p>
              <p className="testimonial-role">Técnico IT</p>
            </div>
            <p className="testimonial-body">Precios competitivos y soporte técnico eficiente. Recomiendo ComercioTech para proyectos profesionales.</p>
          </div>

          <div className="testimonial-card">
            <div className="testimonial-header">
              <p className="testimonial-name">Sofía García</p>
              <p className="testimonial-role">Estudiante</p>
            </div>
            <p className="testimonial-body">La experiencia de compra fue muy sencilla y las promociones estudiantiles ayudaron mucho.</p>
          </div>
        </div>
      </section>
    </main>
  );
}
