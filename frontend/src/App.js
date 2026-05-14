import React from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { AppProvider, useApp } from './context/AppContext';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Library from './pages/Library';
import MediaGallery from './pages/MediaGallery';
import Podcasts from './pages/Podcasts';
import VideoChannels from './pages/VideoChannels';
import CartPage from './pages/CartPage';
import Orders from './pages/Orders';
import Settings from './pages/Settings';
import BooksPage from './pages/BooksPage';
import CricfyTv from './pages/CricfyTv';
import './styles.css';

const pages = [
  { k: 'dashboard', c: Dashboard },
  { k: 'library', c: Library },
  { k: 'media', c: MediaGallery },
  { k: 'podcasts', c: Podcasts },
  { k: 'videos', c: VideoChannels },
  { k: 'cart', c: CartPage },
  { k: 'orders', c: Orders },
  { k: 'cricfy', c: CricfyTv },
  { k: 'upload', c: BooksPage },
  { k: 'settings', c: Settings },
];

function AppContent() {
  const { page } = useApp();

  const renderPage = () => {
    for (const p of pages) {
      if (page === p.k) {
        const Component = p.c;
        return <Component />;
      }
    }
    if (page && page.startsWith('book-')) {
      return <Library />;
    }
    return <Dashboard />;
  };

  return (
    <div className="app scene-3d">
      <div className="particle-bg" aria-hidden="true">
        <div className="particle-orb"></div>
        <div className="particle-orb"></div>
        <div className="particle-orb"></div>
      </div>
      <Navbar />
      <main className="main-content">
        {renderPage()}
      </main>
      <ToastContainer position="bottom-right" theme="dark" autoClose={2500} />
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;
