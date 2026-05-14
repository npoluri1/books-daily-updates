import React from 'react';
import { useApp } from '../context/AppContext';

const navItems = [
  { k: 'dashboard', i: '📊', l: 'Home' },
  { k: 'library', i: '📚', l: 'Library' },
  { k: 'media', i: '🎬', l: 'Media' },
  { k: 'podcasts', i: '🎙️', l: 'Podcasts' },
  { k: 'videos', i: '📹', l: 'Videos' },
  { k: 'cricfy', i: '🏏', l: 'Cricfy TV' },
  { k: 'cart', i: '🛒', l: 'Cart' },
  { k: 'orders', i: '📦', l: 'Orders' },
  { k: 'upload', i: '📁', l: 'Upload' },
  { k: 'settings', i: '⚙️', l: 'Settings' },
];

const Navbar = () => {
  const { page, setPage, cart, selectedCurrency, currencies, changeCurrency } = useApp();

  return (
    <nav className="navbar navbar-3d">
      <div className="nav-inner">
          <div className="nav-brand card-3d" onClick={() => setPage('dashboard')}>
            <div className="brand-icon accent-gradient">📚</div>
          <span className="brand-text">GlobalBookStore</span>
        </div>
        <div className="nav-links">
          {navItems.map(p => (
            <button
              key={p.k}
              className={`nav-link ${page === p.k ? 'active' : ''}`}
              onClick={() => setPage(p.k)}
            >
              {p.i} {p.l}
              {p.k === 'cart' && cart.total_items > 0 && (
                <span className="cart-badge">{cart.total_items}</span>
              )}
            </button>
          ))}
        </div>
        <div className="nav-right">
          <select
            className="currency-select"
            value={selectedCurrency}
            onChange={e => changeCurrency(e.target.value)}
          >
            {currencies.map(c => (
              <option key={c.code} value={c.code}>
                {c.symbol} {c.code}
              </option>
            ))}
          </select>
          <button
            className="mobile-menu-btn"
            onClick={() => document.querySelector('.nav-links')?.classList.toggle('show')}
          >
            ☰
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
