import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, Mountain, CloudSun, Sun, Moon } from 'lucide-react'
import './Navbar.css'

const navLinks = [
  { path: '/', label: 'Beranda' },
  { path: '/dashboard', label: 'Dashboard Cuaca' },
  { path: '/explore', label: 'Jelajahi' },
  { path: '/itinerary', label: 'Itinerary' },
  { path: '/info', label: 'Pusat Info' },
]

export default function Navbar({ theme, toggleTheme }) {
  const location = useLocation()
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setIsScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  return (
    <nav className={`navbar ${isScrolled ? 'navbar--scrolled' : ''}`} id="main-navbar">
      <div className="navbar__inner container">
        {/* Logo */}
        <Link to="/" className="navbar__logo" id="navbar-logo">
          <div className="navbar__logo-icon">
            <Mountain size={24} />
          </div>
          <div className="navbar__logo-text">
            <span className="navbar__brand">Dihyang</span>
            <span className="navbar__tagline">Smart Tourism</span>
          </div>
        </Link>

        {/* Desktop Nav */}
        <div className="navbar__links hide-mobile">
          {navLinks.map(link => (
            <Link
              key={link.path}
              to={link.path}
              className={`navbar__link ${location.pathname === link.path ? 'navbar__link--active' : ''}`}
              id={`nav-link-${link.path.replace('/', '') || 'home'}`}
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* CTA & Theme Toggle */}
        <div className="navbar__actions hide-mobile">
          <button 
            className="navbar__theme-toggle btn btn-icon btn-ghost" 
            onClick={toggleTheme}
            aria-label="Toggle Theme"
          >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          <Link to="/chat" className="btn btn-primary btn-sm" id="nav-cta-dita">
            <CloudSun size={16} />
            Tanya DITA
          </Link>
        </div>

        {/* Mobile Toggle */}
        <button
          className="navbar__toggle"
          onClick={() => setMobileOpen(!mobileOpen)}
          id="navbar-mobile-toggle"
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="navbar__mobile animate-fade-in-down" id="mobile-menu">
          <div className="navbar__mobile-links">
            {navLinks.map(link => (
              <Link
                key={link.path}
                to={link.path}
                className={`navbar__mobile-link ${location.pathname === link.path ? 'navbar__mobile-link--active' : ''}`}
              >
                {link.label}
              </Link>
            ))}
            <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
              <button 
                className="btn btn-outline" 
                onClick={toggleTheme}
                style={{ flex: 1, padding: '8px', display: 'flex', justifyContent: 'center' }}
              >
                {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
              </button>
              <Link to="/chat" className="btn btn-primary" style={{ flex: 3 }}>
                <CloudSun size={16} />
                Tanya DITA
              </Link>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
