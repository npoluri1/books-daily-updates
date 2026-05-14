import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { API_URL } from '../api';

const BooksPage = () => {
  const { catalog, categories } = useApp();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('');
  const [search, setSearch] = useState('');
  const [filtered, setFiltered] = useState([]);
  const [typeFilter, setTypeFilter] = useState('all');
  const [catFilter, setCatFilter] = useState('');

  useEffect(() => {
    let f = [...catalog];
    if (typeFilter !== 'all') f = f.filter(b => b.product_type === typeFilter);
    if (catFilter) f = f.filter(b => b.categories?.some(c => c.slug === catFilter));
    if (search) {
      const lq = search.toLowerCase();
      f = f.filter(b => b.title.toLowerCase().includes(lq) || (b.author || '').toLowerCase().includes(lq));
    }
    setFiltered(f);
  }, [catalog, typeFilter, catFilter, search]);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setUploadProgress(0);
    setUploadStatus('Uploading...');

    const formData = new FormData();
    formData.append('file', file);
    const xhr = new XMLHttpRequest();
    xhr.upload.onprogress = (ev) => {
      if (ev.lengthComputable) setUploadProgress(Math.round((ev.loaded / ev.total) * 100));
    };
    xhr.onload = async () => {
      try {
        const data = JSON.parse(xhr.responseText);
        const { toast } = await import('react-toastify');
        toast(data.message || `Uploaded successfully!`, { type: 'success' });
        setUploadStatus(`✅ ${data.books_added || 0} books added`);
      } catch (err) {
        const { toast } = await import('react-toastify');
        toast('Upload completed but parse error', { type: 'warning' });
      }
      setUploading(false);
    };
    xhr.onerror = async () => {
      const { toast } = await import('react-toastify');
      toast('Upload failed', { type: 'error' });
      setUploadStatus('❌ Upload failed');
      setUploading(false);
    };
    xhr.open('POST', `${API_URL}/api/books/upload`);
    xhr.send(formData);
    e.target.value = '';
  };

  const allTypes = [...new Set(catalog.filter(b => b.product_type).map(b => b.product_type))];

  return (
    <div className="page page-3d">
      <div className="page-header">
        <h1 className="page-title text-3d-strong">📖 Upload <span>Books</span></h1>
        <label className={`btn btn-primary upload-btn ${uploading ? 'disabled' : ''}`} style={{ cursor: uploading ? 'not-allowed' : 'pointer' }}>
          {uploading ? `⏳ ${uploadProgress}%` : '+ Upload Excel'}
          <input type="file" accept=".xlsx,.xls,.csv" onChange={handleFileUpload} hidden disabled={uploading} />
        </label>
      </div>

      {uploading && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 13, color: 'var(--text-secondary)' }}>
            <span>{uploadStatus}</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="progress-bar" style={{ height: 8 }}>
            <div className="progress-fill" style={{ width: `${uploadProgress}%` }} />
          </div>
        </div>
      )}

      {uploadStatus && !uploading && (
        <div className="card" style={{ marginBottom: 20, padding: 16 }}>
          <span style={{ fontSize: 14 }}>{uploadStatus}</span>
        </div>
      )}

      <p className="page-subtitle" style={{ marginBottom: 16 }}>
        Upload Excel files (.xlsx) with columns: title, author, price, description, product_type (book/electronics/clothing), brand.
      </p>

      <div className="filter-bar" style={{ marginBottom: 16 }}>
        <select className="cat-select" value={typeFilter} onChange={e => setTypeFilter(e.target.value)} style={{ minWidth: 140 }}>
          <option value="all">All Types</option>
          {allTypes.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
        </select>
        <select className="cat-select" value={catFilter} onChange={e => setCatFilter(e.target.value)} style={{ minWidth: 160 }}>
          <option value="">All Categories</option>
          {categories.map(c => <option key={c.id} value={c.slug}>{c.icon} {c.name}</option>)}
        </select>
        <div className="search-wrapper" style={{ flex: 1 }}>
          <input type="text" placeholder="Search products..." value={search} onChange={e => setSearch(e.target.value)} className="search-input" />
        </div>
      </div>

      <div className="books-grid">
        {filtered.map(b => (
          <div key={b.id} className="book-card catalog-card book-card-3d card-shine" style={{ position: 'relative' }}>
            {b.images?.length > 0 && <img src={b.images[0]?.url} alt={b.title} className="book-cover book-cover-3d" />}
            <div className="book-card-header">
              <h3>{b.title}</h3>
              {b.author && <p className="book-author">by {b.author}</p>}
              <div className="book-categories">
                {b.product_type && (
                  <span className={`badge ${b.product_type === 'electronics' ? 'badge-warning' : b.product_type === 'clothing' ? 'badge-info' : 'badge-success'}`}>
                    {b.product_type === 'electronics' ? '📱' : b.product_type === 'clothing' ? '👕' : '📚'} {b.product_type}
                  </span>
                )}
              </div>
            </div>
            <div className="book-stats">
              <span>{b.pages || 'N/A'} pages · ${b.price?.toFixed(2)}</span>
              {b.brand && <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Brand: {b.brand}</span>}
            </div>
          </div>
        ))}
      </div>
      {filtered.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📁</div>
          <h3>No Products Found</h3>
          <p>Upload Excel or adjust filters</p>
        </div>
      )}
    </div>
  );
};

export default BooksPage;
