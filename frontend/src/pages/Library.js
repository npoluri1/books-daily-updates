import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import BookCard from '../components/BookCard';

const Library = () => {
  const { catalog, categories, setPage, loadCatalog } = useApp();
  const [cat, setCat] = useState('');
  const [q, setQ] = useState('');
  const [filtered, setFiltered] = useState([]);

  useEffect(() => {
    let f = [...catalog];
    if (cat) f = f.filter(b => b.categories?.some(c => c.slug === cat));
    if (q) {
      const lq = q.toLowerCase();
      f = f.filter(b =>
        b.title.toLowerCase().includes(lq) ||
        (b.author || '').toLowerCase().includes(lq) ||
        (b.description || '').toLowerCase().includes(lq)
      );
    }
    setFiltered(f);
  }, [cat, q, catalog]);

  return (
    <div className="page page-3d">
      <div className="page-header">
        <h1 className="page-title text-3d-strong">Book <span>Library</span></h1>
      </div>
      <div className="search-bar">
        <div className="search-wrapper">
          <input
            type="text" placeholder="Search by title, author, description..."
            value={q} onChange={e => setQ(e.target.value)}
            className="search-input"
          />
        </div>
        <select className="cat-select" value={cat} onChange={e => setCat(e.target.value)}>
          <option value="">All Categories</option>
          {categories.map(c => (
            <option key={c.id} value={c.slug}>{c.icon} {c.name}</option>
          ))}
        </select>
      </div>
      <div className="books-grid">
        {filtered.map(b => (
          <BookCard key={b.id} book={b} catalogView={true} showActions={true} />
        ))}
      </div>
      {filtered.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📚</div>
          <h3>No Books Found</h3>
          <p>Try a different search or category filter</p>
        </div>
      )}
    </div>
  );
};

export default Library;
