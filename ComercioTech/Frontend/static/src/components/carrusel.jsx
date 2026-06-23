import { useState } from "react";

export default function Carroussel() {
  const [activeIndex, setActiveIndex] = useState(0);

  const slides = [
    { src: "src/assets/image.jpg", alt: "trabajo_en_equipo" },
    { src: "src/assets/Virtual-Office.png", alt: "labor_en_la_oficina" },
    { src: "src/assets/3485346-0-65796900-1742380165-shutterstock_2431976515.webp", alt: "meeting_it" }
  ];

  const nextSlide = () => setActiveIndex((prev) => (prev === slides.length - 1 ? 0 : prev + 1));
  const prevSlide = () => setActiveIndex((prev) => (prev === 0 ? slides.length - 1 : prev - 1));

  return (
    <div id="carouselExampleIndicators" className="carousel slide">
      <div className="carousel-indicators">
        {slides.map((_, i) => (
          <button
            key={i}
            type="button"
            onClick={() => setActiveIndex(i)}
            className={activeIndex === i ? "active" : ""}
            aria-current={activeIndex === i ? "true" : undefined}
            aria-label={`Slide ${i + 1}`}
          ></button>
        ))}
      </div>
      <div className="carousel-inner">
        {slides.map((slide, i) => (
          <div key={i} className={`carousel-item ${activeIndex === i ? "active" : ""}`}>
            <img 
              src={slide.src} 
              className="d-block w-100" 
              alt={slide.alt} 
              style={{ height: "500px", objectFit: "cover" }} 
            />
          </div>
        ))}
      </div>
      <button className="carousel-control-prev" type="button" onClick={prevSlide}>
        <span className="carousel-control-prev-icon" aria-hidden="true"></span>
        <span className="visually-hidden">Previous</span>
      </button>
      <button className="carousel-control-next" type="button" onClick={nextSlide}>
        <span className="carousel-control-next-icon" aria-hidden="true"></span>
        <span className="visually-hidden">Next</span>
      </button>
    </div>
  );
}