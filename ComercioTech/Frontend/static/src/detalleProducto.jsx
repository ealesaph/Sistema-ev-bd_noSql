import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import MainHeader from './components/header';
import { getProductImage } from './utils/getImage';
import MainFooter from './components/footer';
import GridCard from './components/gridCardProductos';

export default function DetalleProducto() {
  const { id } = useParams();
  const [producto, setProducto] = useState(null);
  const [recomendaciones, setRecomendaciones] = useState([]);
  const [resenas, setResenas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Formulario de reseñas
  const [rating, setRating] = useState(5);
  const [titulo, setTitulo] = useState('');
  const [comentario, setComentario] = useState('');
  const [errorResena, setErrorResena] = useState('');
  const [exitoResena, setExitoResena] = useState('');
  const [cargandoResena, setCargandoResena] = useState(false);

  const [usuario, setUsuario] = useState(null);
  const [idCliente, setIdCliente] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Cargar usuario
    const uStr = localStorage.getItem('usuario');
    if (uStr) {
      try {
        const u = JSON.parse(uStr);
        setUsuario(u);
        setIdCliente(u.id_cliente);
      } catch (e) {
        console.error(e);
      }
    }
  }, []);

  useEffect(() => {
    const cargarDatos = async () => {
      setLoading(true);
      setError('');
      try {
        // 1. Detalles del producto
        const resProd = await fetch(`/leo/productos/${id}`);
        const dataProd = await resProd.json();
        if (dataProd.exito) {
          setProducto(dataProd.producto);
        } else {
          setError(dataProd.mensaje || 'No se pudo cargar el producto');
          setLoading(false);
          return;
        }

        // Obtener cliente_id si está logueado para auditoría en backend
        const uStr = localStorage.getItem('usuario');
        let cId = '';
        if (uStr) {
          try {
            cId = JSON.parse(uStr).id_cliente || '';
          } catch(e) {}
        }

        // 2. Recomendaciones (Productos adyacentes)
        const resRec = await fetch(`/leo/productos/${id}/recomendaciones?cliente_id=${cId}`);
        const dataRec = await resRec.json();
        if (dataRec.exito) {
          setRecomendaciones(dataRec.recomendaciones || []);
        }

        // 3. Reseñas
        const resRes = await fetch(`/leo/productos/${id}/resenas`);
        const dataRes = await resRes.json();
        if (dataRes.exito) {
          setResenas(dataRes.resenas || []);
        }

      } catch (err) {
        console.error(err);
        setError('Ocurrió un error al conectar con el servidor.');
      } finally {
        setLoading(false);
      }
    };

    cargarDatos();
    // Limpiar formulario al cambiar de producto
    setRating(5);
    setTitulo('');
    setComentario('');
    setErrorResena('');
    setExitoResena('');
  }, [id]);

  const agregarAlCarrito = async () => {
    if (!producto) return;

    if (idCliente) {
      try {
        const response = await fetch('/leo/carrito/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            cliente_id: idCliente,
            producto_id: producto._id,
            cantidad: 1,
            nombre: producto.nombre,
            precio_unitario: producto.precio_actual || producto.precio || 0,
            id_producto_sql: producto.id_producto_sql
          })
        });

        if (response.ok) {
          alert(`¡${producto.nombre} añadido a tu carrito en línea!`);
        } else {
          alert('Error al agregar al carrito en la base de datos');
        }
      } catch (err) {
        console.error(err);
        alert('Error al agregar al carrito: problema de red');
      }
    } else {
      const carritoActual = JSON.parse(localStorage.getItem('carrito')) || [];
      const index = carritoActual.findIndex(c => (c._id || c.id) === producto._id);
      
      if (index !== -1) {
        carritoActual[index].cantidad = (carritoActual[index].cantidad || 1) + 1;
      } else {
        carritoActual.push({ ...producto, cantidad: 1 });
      }
      
      localStorage.setItem('carrito', JSON.stringify(carritoActual));
      alert(`¡${producto.nombre} añadido al carrito local!`);
    }
  };

  const enviarResena = async (e) => {
    e.preventDefault();
    setErrorResena('');
    setExitoResena('');
    setCargandoResena(true);

    if (!idCliente || !usuario) {
      setErrorResena('Debes iniciar sesión para calificar un producto.');
      setCargandoResena(false);
      return;
    }

    try {
      const response = await fetch(`/leo/productos/${id}/resenas`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          id_cliente: idCliente,
          rating: rating,
          titulo: titulo,
          comentario: comentario,
          nombre_cliente: `${usuario.nombre} ${usuario.apellido || ''}`.trim()
        })
      });

      const data = await response.json();

      if (response.ok && data.exito) {
        setExitoResena('¡Tu reseña ha sido publicada exitosamente!');
        // Actualizar promedio localmente
        setProducto(prev => ({
          ...prev,
          rating_promedio: data.rating_promedio,
          total_resenas: data.total_resenas
        }));
        // Refrescar listado de reseñas
        const resRes = await fetch(`/leo/productos/${id}/resenas`);
        const dataRes = await resRes.json();
        if (dataRes.exito) {
          setResenas(dataRes.resenas || []);
        }
        // Limpiar formulario
        setRating(5);
        setTitulo('');
        setComentario('');
      } else {
        setErrorResena(data.mensaje || 'Error al publicar la reseña.');
      }
    } catch (err) {
      console.error(err);
      setErrorResena('Error de red. Inténtalo de nuevo.');
    } finally {
      setCargandoResena(false);
    }
  };

  // Helper para pintar estrellas doradas
  const renderEstrellas = (score) => {
    const estrellas = [];
    const entero = Math.floor(score);
    for (let i = 1; i <= 5; i++) {
      if (i <= entero) {
        estrellas.push(<i key={i} className="bi bi-star-fill text-warning me-1"></i>);
      } else {
        estrellas.push(<i key={i} className="bi bi-star text-secondary me-1"></i>);
      }
    }
    return estrellas;
  };

  if (loading) {
    return (
      <>
        <MainHeader />
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando producto...</span>
          </div>
        </div>
        <MainFooter />
      </>
    );
  }

  if (error || !producto) {
    return (
      <>
        <MainHeader />
        <div className="container my-5 text-center">
          <div className="alert alert-danger py-4" role="alert">
            <i className="bi bi-exclamation-triangle-fill fs-1 d-block mb-3"></i>
            <h4 className="alert-heading fw-bold">Error al Cargar Producto</h4>
            <p className="mb-0">{error || 'El producto solicitado no existe.'}</p>
            <Link to="/" className="btn btn-outline-danger mt-3 fw-bold rounded-pill">Volver al catálogo</Link>
          </div>
        </div>
        <MainFooter />
      </>
    );
  }

  const marca = producto.especificaciones_fabricante?.fabricante || 'General';
  const precio = producto.precio_actual || producto.precio || 0;

  return (
    <>
      <MainHeader />
      <div className="container my-5">
        {/* Ficha Formal de Producto */}
        <div className="bg-white rounded shadow-sm p-4 border border-light mb-5">
          <nav aria-label="breadcrumb" className="mb-4">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/">Catálogo</Link></li>
              <li className="breadcrumb-item text-capitalize">{producto.categoria}</li>
              <li className="breadcrumb-item active" aria-current="page">{producto.nombre}</li>
            </ol>
          </nav>

          <div className="row">
            {/* Columna Izquierda: Imagen y Puntuaciones */}
            <div className="col-md-5 text-center border-end-md pb-4 pb-md-0">
              <div className="product-image-container p-3 mb-4 bg-light rounded d-flex align-items-center justify-content-center" style={{ height: '350px' }}>
                <img 
                  src={getProductImage(producto)} 
                  alt={producto.nombre} 
                  className="img-fluid" 
                  style={{ maxHeight: '100%', objectFit: 'contain' }} 
                />
              </div>

              {/* Valoración Promedio */}
              <div className="bg-light p-3 rounded text-center">
                <h5 className="fw-bold mb-2">Valoración del Producto</h5>
                <div className="fs-3 mb-1">
                  {renderEstrellas(producto.rating_promedio || 0)}
                </div>
                <div className="fw-bold text-dark fs-4">
                  {producto.rating_promedio ? `${producto.rating_promedio} / 5` : 'Sin calificaciones'}
                </div>
                <small className="text-muted d-block">
                  ({producto.total_resenas || 0} reseñas de compradores)
                </small>
              </div>
            </div>

            {/* Columna Derecha: Características, Precio y Agregar */}
            <div className="col-md-7 ps-md-4">
              <span className="badge bg-secondary mb-2 text-uppercase">{marca}</span>
              <h1 className="fw-bold text-dark mb-3 fs-2">{producto.nombre}</h1>
              
              <div className="d-flex align-items-baseline gap-3 mb-4">
                <span className="fs-2 fw-bold text-price-brand">${precio.toLocaleString('es-CL')}</span>
                <span className="text-success fw-bold">Envío Gratis</span>
              </div>

              <div className="mb-4">
                <h6 className="fw-bold text-secondary mb-2">Descripción General:</h6>
                <p className="text-muted" style={{ lineHeight: '1.6' }}>{producto.descripcion || 'Sin descripción disponible para este artículo.'}</p>
              </div>

              <div className="d-flex align-items-center gap-3 mb-4 border-top border-bottom py-3">
                <div>
                  <span className="text-muted d-block small">Stock disponible:</span>
                  <span className={`fw-bold ${producto.stock > 0 ? 'text-dark' : 'text-danger'}`}>
                    {producto.stock > 0 ? `${producto.stock} unidades` : 'Agotado'}
                  </span>
                </div>
                <button 
                  onClick={agregarAlCarrito} 
                  className="btn btn-primary btn-lg px-5 JnsnButton fw-bold rounded-pill ms-auto"
                  disabled={producto.stock <= 0}
                >
                  <i className="bi bi-cart-plus me-2"></i> Añadir al Carrito
                </button>
              </div>

              {/* Características Técnicas */}
              <div>
                <h5 className="fw-bold text-dark mb-3">Especificaciones Técnicas</h5>
                <div className="table-responsive">
                  <table className="table table-sm table-striped table-bordered align-middle">
                    <tbody>
                      {Object.entries(producto.atributos || {})
                        .filter(([_, val]) => val !== null && val !== undefined && val !== '')
                        .map(([key, val]) => (
                          <tr key={key}>
                            <td className="fw-bold text-secondary text-capitalize px-3" style={{ width: '40%' }}>
                              {key.replace(/_/g, ' ')}
                            </td>
                            <td className="px-3 text-dark">
                              {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                            </td>
                          </tr>
                        ))}
                      {Object.keys(producto.atributos || {}).length === 0 && (
                        <tr>
                          <td colSpan="2" className="text-muted text-center py-2">No hay especificaciones técnicas detalladas.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

            </div>
          </div>
        </div>

        {/* Sección de Publicidad / Sugeridos (Productos Adyacentes) */}
        <div className="mb-5">
          <h3 className="fw-bold text-dark mb-4 pb-2 border-bottom border-3 border-primary d-inline-block">
            Productos Sugeridos (Publicidad Relacionada)
          </h3>
          {recomendaciones.length === 0 ? (
            <p className="text-muted">No hay sugerencias disponibles en esta categoría en este momento.</p>
          ) : (
            <div className="row row-cols-1 row-cols-md-3 row-cols-lg-4 g-4 overflow-auto flex-nowrap pb-3" style={{ scrollbarWidth: 'thin' }}>
              {recomendaciones.map((rec) => (
                <div className="col flex-shrink-0" style={{ width: '280px' }} key={rec._id}>
                  <GridCard producto={rec} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sección de Reseñas y Valoraciones */}
        <div>
          <h3 className="fw-bold text-dark mb-4 pb-2 border-bottom border-3 border-primary d-inline-block">
            Opiniones de Compradores
          </h3>
          
          <div className="row">
            {/* Listado de Reseñas */}
            <div className="col-lg-7 mb-4 mb-lg-0">
              {resenas.length === 0 ? (
                <div className="alert alert-light border text-center py-4">
                  <i className="bi bi-chat-left-dots text-muted fs-2 d-block mb-2"></i>
                  <p className="text-muted mb-0">Este producto aún no tiene reseñas escritas. ¡Sé el primero!</p>
                </div>
              ) : (
                <div className="d-flex flex-column gap-3">
                  {resenas.map((r) => (
                    <div className="card border-0 shadow-sm p-3 rounded" key={r._id}>
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <span className="fw-bold text-dark">{r.nombre_cliente}</span>
                        <span className="text-muted small">{r.fecha ? r.fecha.substring(0, 10) : ''}</span>
                      </div>
                      <div className="mb-2">
                        {renderEstrellas(r.rating)}
                        {r.titulo && <span className="fw-bold text-dark ms-2">{r.titulo}</span>}
                      </div>
                      <p className="text-muted mb-0" style={{ fontSize: '0.95rem' }}>{r.comentario}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Formulario de Reseña */}
            <div className="col-lg-5">
              <div className="card shadow-sm border-0 p-4 rounded bg-light">
                <h5 className="fw-bold text-dark mb-3">Escribir Reseña</h5>

                {usuario ? (
                  <form onSubmit={enviarResena}>
                    {errorResena && <div className="alert alert-danger p-2 small">{errorResena}</div>}
                    {exitoResena && <div className="alert alert-success p-2 small">{exitoResena}</div>}

                    <div className="mb-3">
                      <label className="form-label fw-bold text-secondary">Calificación:</label>
                      <select 
                        className="form-select" 
                        value={rating} 
                        onChange={(e) => setRating(parseInt(e.target.value))}
                        required
                      >
                        <option value="5">⭐⭐⭐⭐⭐ (5 estrellas)</option>
                        <option value="4">⭐⭐⭐⭐ (4 estrellas)</option>
                        <option value="3">⭐⭐⭐ (3 estrellas)</option>
                        <option value="2">⭐⭐ (2 estrellas)</option>
                        <option value="1">⭐ (1 estrella)</option>
                        <option value="0">❌ 0 estrellas</option>
                      </select>
                    </div>

                    <div className="mb-3">
                      <label className="form-label fw-bold text-secondary">Título de la Opinión:</label>
                      <input 
                        type="text" 
                        className="form-control" 
                        placeholder="Ej: Excelente calidad, Muy recomendado" 
                        value={titulo}
                        onChange={(e) => setTitulo(e.target.value)}
                        required
                      />
                    </div>

                    <div className="mb-3">
                      <label className="form-label fw-bold text-secondary">Comentario:</label>
                      <textarea 
                        className="form-control" 
                        rows="4" 
                        placeholder="Comparte tu experiencia de compra y detalles técnicos del producto..." 
                        value={comentario}
                        onChange={(e) => setComentario(e.target.value)}
                        required
                      ></textarea>
                    </div>

                    <div className="alert alert-info py-2 px-3 mb-3 small" style={{ fontSize: '0.8rem' }}>
                      <i className="bi bi-info-circle-fill me-1 text-primary"></i>
                      Tu opinión se validará contra tu historial de compras en PostgreSQL. Sólo se aceptarán reseñas si has comprado el artículo.
                    </div>

                    <button 
                      type="submit" 
                      className="btn btn-primary w-100 JnsnButton fw-bold rounded-pill"
                      disabled={cargandoResena}
                    >
                      {cargandoResena ? 'Publicando...' : 'Publicar Reseña'}
                    </button>
                  </form>
                ) : (
                  <div className="text-center py-3">
                    <p className="text-muted small">Debes haber comprado este artículo y estar autenticado para calificarlo.</p>
                    <Link to="/loginUsuario" className="btn btn-outline-primary fw-bold btn-sm rounded-pill px-4">
                      Iniciar Sesión
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

      </div>
      <MainFooter />
    </>
  );
}
