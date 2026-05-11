import { Link } from 'react-router-dom'
import { Mountain, Mail, MapPin, Phone, Code, ExternalLink } from 'lucide-react'
import './Footer.css'

export default function Footer() {
  return (
    <footer className="footer" id="main-footer">
      <div className="container">
        <div className="footer__grid">
          {/* Brand */}
          <div className="footer__brand">
            <Link to="/" className="footer__logo">
              <div className="footer__logo-icon">
                <Mountain size={20} />
              </div>
              <span className="footer__logo-text">Dihyang</span>
            </Link>
            <p className="footer__desc">
              Platform pariwisata cerdas berbasis AI untuk pengalaman wisata Dieng yang aman, informatif, dan menyeluruh.
            </p>
            <div className="footer__badges">
              <span className="badge badge-primary">AI Powered</span>
              <span className="badge badge-success">Real-time Weather</span>
            </div>
          </div>

          {/* Quick Links */}
          <div className="footer__section">
            <h4 className="footer__title">Navigasi</h4>
            <div className="footer__links">
              <Link to="/" className="footer__link">Beranda</Link>
              <Link to="/dashboard" className="footer__link">Dashboard Cuaca</Link>
              <Link to="/explore" className="footer__link">Jelajahi Dieng</Link>
              <Link to="/chat" className="footer__link">Tanya DITA</Link>
              <Link to="/itinerary" className="footer__link">Smart Itinerary</Link>
              <Link to="/info" className="footer__link">Pusat Informasi</Link>
            </div>
          </div>

          {/* Destinations */}
          <div className="footer__section">
            <h4 className="footer__title">Destinasi Populer</h4>
            <div className="footer__links">
              <a href="#" className="footer__link">Kawah Sikidang</a>
              <a href="#" className="footer__link">Telaga Warna</a>
              <a href="#" className="footer__link">Candi Arjuna</a>
              <a href="#" className="footer__link">Bukit Sikunir</a>
              <a href="#" className="footer__link">Batu Ratapan Angin</a>
              <a href="#" className="footer__link">Dieng Plateau Theater</a>
            </div>
          </div>

          {/* Contact */}
          <div className="footer__section">
            <h4 className="footer__title">Kontak</h4>
            <div className="footer__contact-list">
              <div className="footer__contact-item">
                <MapPin size={16} />
                <span>Wonosobo, Jawa Tengah</span>
              </div>
              <div className="footer__contact-item">
                <Mail size={16} />
                <span>team@dihyang.id</span>
              </div>
              <div className="footer__contact-item">
                <Code size={16} />
                <a href="#" className="footer__link" style={{ padding: 0 }}>GitHub Repository</a>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="footer__bottom">
          <p className="footer__copyright">
            © 2026 Dihyang Web — Tim PJK-GM067 | Pijak × IBM SkillsBuild Capstone Project
          </p>
          <p className="footer__powered">
            Powered by Gemini AI & Open-Meteo
          </p>
        </div>
      </div>
    </footer>
  )
}
