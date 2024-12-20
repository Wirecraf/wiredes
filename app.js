import React, { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [format, setFormat] = useState('');
  const [quality, setQuality] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [downloadLink, setDownloadLink] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch('/api/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, format, quality }),
      });
      const data = await response.json();
      setDownloadLink(data.downloadUrl);
    } catch (error) {
      console.error('Error:', error);
      alert('Hubo un error al procesar su solicitud. Por favor, inténtelo de nuevo.');
    }
    setIsLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Descarga Videos y Música Fácilmente</h1>
        <p>Herramienta educativa para descargar contenido multimedia</p>
      </header>
      <main>
        <section className="download-section">
          <h2>Empieza a Descargar</h2>
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Pega aquí el enlace del video o música"
              required
            />
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              required
            >
              <option value="">Selecciona el formato</option>
              <option value="mp4">Video - MP4</option>
              <option value="mp3">Audio - MP3</option>
            </select>
            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
              required
            >
              <option value="">Selecciona la calidad</option>
              <option value="high">Alta</option>
              <option value="medium">Media</option>
              <option value="low">Baja</option>
            </select>
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Procesando...' : 'Descargar Ahora'}
            </button>
          </form>
          {downloadLink && (
            <div className="download-link">
              <a href={downloadLink} download>Haz clic aquí para descargar tu archivo</a>
            </div>
          )}
        </section>
        <section className="features-section">
          <h2>Características Clave</h2>
          <ul>
            <li>Descargas rápidas y seguras</li>
            <li>Compatibilidad con múltiples plataformas</li>
            <li>Formatos adaptables para cualquier dispositivo</li>
          </ul>
        </section>
        <section className="faq-section">
          <h2>Preguntas Frecuentes</h2>
          <div className="faq-item">
            <h3>¿Es legal usar esta herramienta?</h3>
            <p>Esta herramienta está diseñada con fines educativos. Los usuarios son responsables de cumplir con los derechos de autor y los términos de servicio de las plataformas de origen.</p>
          </div>
          <div className="faq-item">
            <h3>¿Cómo funciona?</h3>
            <p>Nuestra herramienta utiliza tecnologías de código abierto para procesar y convertir los enlaces que proporcionas en archivos descargables.</p>
          </div>
        </section>
      </main>
      <footer>
        <p>© 2023 Video Downloader. Todos los derechos reservados.</p>
        <p>Aviso Legal: Esta herramienta es para uso educativo. No promovemos la infracción de derechos de autor.</p>
      </footer>
    </div>
  );
}

export default App;

