import React, { useState, useEffect } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './styles.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [page, setPage] = useState('dashboard');
  const [books, setBooks] = useState([]);
  const [dailyReading, setDailyReading] = useState(null);
  const [schedules, setSchedules] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [useRegex, setUseRegex] = useState(false);
  const [user, setUser] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadUser();
    loadBooks();
    loadDailyReading();
    loadSchedules();
  }, []);

  const api = async (endpoint, options = {}) => {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    };
    if (config.body && typeof config.body === 'string') {
      config.headers['Content-Type'] = 'application/json';
    }
    const resp = await fetch(url, config);
    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(err);
    }
    return resp.json();
  };

  const loadUser = async () => {
    try {
      let u = localStorage.getItem('book_user');
      if (!u) {
        u = await api('/api/users/', {
          method: 'POST',
          body: JSON.stringify({ email: 'user@example.com', name: 'Reader' }),
        });
        localStorage.setItem('book_user', JSON.stringify(u));
      } else {
        u = JSON.parse(u);
      }
      setUser(u);
    } catch (e) {
      console.error('User load error:', e);
    }
  };

  const loadBooks = async (search, regex) => {
    try {
      let url = '/api/books/';
      if (search) url += `?search=${encodeURIComponent(search)}&regex=${regex}`;
      const data = await api(url);
      setBooks(data);
      if (search) setSearchResults(data);
    } catch (e) {
      console.error('Books load error:', e);
    }
  };

  const loadDailyReading = async () => {
    try {
      const data = await api('/api/reading/daily?user_id=1');
      setDailyReading(data);
    } catch (e) {
      setDailyReading(null);
    }
  };

  const loadSchedules = async () => {
    try {
      const data = await api('/api/reading/schedules?user_id=1');
      setSchedules(data);
    } catch (e) {
      setSchedules([]);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const resp = await fetch(`${API_BASE}/api/books/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await resp.json();
      alert(data.message);
      loadBooks();
    } catch (e) {
      alert('Upload failed: ' + e.message);
    }
    setUploading(false);
    e.target.value = '';
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadBooks(searchQuery, useRegex);
  };

  const handleScheduleBook = async (bookId) => {
    try {
      await api('/api/reading/schedule', {
        method: 'POST',
        body: JSON.stringify({ book_id: bookId, user_id: 1 }),
      });
      loadSchedules();
      alert('Book scheduled! You will receive daily chapters.');
    } catch (e) {
      alert('Schedule error: ' + e.message);
    }
  };

  const handleSendNotification = async () => {
    try {
      const data = await api('/api/reading/send-notification?user_id=1', {
        method: 'POST',
      });
      alert('Notification sent: ' + JSON.stringify(data.results));
    } catch (e) {
      alert('Notification error: ' + e.message);
    }
  };

  const handleAdvanceChapter = async (scheduleId) => {
    try {
      await api(`/api/reading/advance/${scheduleId}`, { method: 'POST' });
      loadSchedules();
      loadDailyReading();
    } catch (e) {
      alert('Advance error: ' + e.message);
    }
  };

  const handleDeleteBook = async (bookId) => {
    if (!window.confirm('Delete this book?')) return;
    try {
      await api(`/api/books/${bookId}`, { method: 'DELETE' });
      loadBooks();
    } catch (e) {
      alert('Delete error: ' + e.message);
    }
  };

  const progressPercent = (current, total) => {
    if (!total) return 0;
    return Math.round((current / total) * 100);
  };

  const NavBar = () => (
    <nav className="navbar">
      <div className="nav-brand" onClick={() => setPage('dashboard')}>
        <span className="brand-icon">📚</span>
        <span className="brand-text">BooksDaily</span>
      </div>
      <div className="nav-links">
        <button className={`nav-link ${page === 'dashboard' ? 'active' : ''}`} onClick={() => setPage('dashboard')}>Dashboard</button>
        <button className={`nav-link ${page === 'books' ? 'active' : ''}`} onClick={() => setPage('books')}>Books</button>
        <button className={`nav-link ${page === 'schedule' ? 'active' : ''}`} onClick={() => setPage('schedule')}>Schedule</button>
        <button className={`nav-link ${page === 'settings' ? 'active' : ''}`} onClick={() => setPage('settings')}>Settings</button>
      </div>
      <button className="mobile-menu-btn" onClick={() => document.querySelector('.nav-links').classList.toggle('show')}>☰</button>
    </nav>
  );

  const Dashboard = () => (
    <div className="page">
      <h1>📚 Your Daily Reading</h1>
      {dailyReading ? (
        <div className="daily-reading-card card">
          <div className="reading-header">
            <div>
              <h2>{dailyReading.book_title}</h2>
              <p className="reading-meta">
                Chapter {dailyReading.chapter_number}
                {dailyReading.chapter_title ? `: ${dailyReading.chapter_title}` : ''}
                {' · '}{dailyReading.reading_time_minutes} min read
              </p>
            </div>
            <div className="progress-ring">
              <svg width="60" height="60" viewBox="0 0 60 60">
                <circle cx="30" cy="30" r="26" fill="none" stroke="#e5e7eb" strokeWidth="4"/>
                <circle cx="30" cy="30" r="26" fill="none" stroke="#3b82f6" strokeWidth="4"
                  strokeDasharray={`${2 * Math.PI * 26}`}
                  strokeDashoffset={`${2 * Math.PI * 26 * (1 - dailyReading.progress / 100)}`}
                  transform="rotate(-90 30 30)"
                />
                <text x="30" y="30" textAnchor="middle" dominantBaseline="central"
                  fontSize="14" fontWeight="bold" fill="#1e40af">
                  {dailyReading.progress}%
                </text>
              </svg>
            </div>
          </div>
          <div className="reading-summary">
            <p>{dailyReading.summary}</p>
          </div>
          <div className="reading-points">
            <h3>Key Takeaways</h3>
            <ul>
              {dailyReading.key_points.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
          <div className="reading-actions">
            <button className="btn btn-primary" onClick={handleSendNotification}>
              Send to My Phone
            </button>
            <button className="btn btn-outline" onClick={() => setPage('schedule')}>
              View All Schedules
            </button>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📖</div>
          <h3>No Reading Scheduled</h3>
          <p>Upload a books Excel file and schedule a book to start receiving daily chapter summaries.</p>
        </div>
      )}
    </div>
  );

  const BooksPage = () => (
    <div className="page">
      <div className="page-header">
        <h1>📖 My Books</h1>
        <label className="btn btn-primary upload-btn">
          {uploading ? 'Uploading...' : '+ Upload Excel'}
          <input type="file" accept=".xlsx,.xls" onChange={handleFileUpload} hidden />
        </label>
      </div>

      <form className="search-bar" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search books by name... (use .* for regex)"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        <label className="regex-toggle">
          <input type="checkbox" checked={useRegex} onChange={() => setUseRegex(!useRegex)} />
          Regex
        </label>
        <button type="submit" className="btn btn-primary">Search</button>
      </form>

      <div className="books-grid">
        {books.map((book) => {
          const scheduled = schedules.find(s => s.book_id === book.id && s.is_active);
          const pct = progressPercent(book.current_chapter || 0, book.total_chapters || 100);
          return (
            <div key={book.id} className={`book-card ${scheduled ? 'scheduled' : ''}`}>
              <div className="book-card-header">
                <h3>{book.title}</h3>
                {book.author && <p className="book-author">by {book.author}</p>}
              </div>
              <div className="book-stats">
                <span>📊 {book.current_chapter || 0}/{book.total_chapters || '?'} chapters</span>
                <div className="mini-progress">
                  <div className="mini-progress-bar" style={{ width: `${pct}%` }}></div>
                </div>
              </div>
              <div className="book-card-actions">
                {scheduled ? (
                  <span className="badge badge-success">Scheduled</span>
                ) : (
                  <button className="btn btn-sm btn-primary"
                    onClick={() => handleScheduleBook(book.id)}>
                    Schedule
                  </button>
                )}
                <button className="btn btn-sm btn-danger"
                  onClick={() => handleDeleteBook(book.id)}>
                  Delete
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {books.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📂</div>
          <h3>No Books Yet</h3>
          <p>Upload an Excel file with your book list to get started.</p>
          <p className="hint">Format: columns like Title, Author, Total_Chapters</p>
        </div>
      )}
    </div>
  );

  const SchedulePage = () => (
    <div className="page">
      <h1>📅 Reading Schedule</h1>

      {schedules.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📅</div>
          <h3>No Active Schedules</h3>
          <p>Go to Books page and click "Schedule" on any book to start daily reading.</p>
        </div>
      ) : (
        <div className="schedules-list">
          {schedules.map((s) => {
            const book = books.find(b => b.id === s.book_id);
            const pct = progressPercent(s.current_chapter, book?.total_chapters || 100);
            return (
              <div key={s.id} className={`schedule-card card ${s.is_active ? '' : 'completed'}`}>
                <div className="schedule-info">
                  <h3>{book?.title || 'Unknown Book'}</h3>
                  <p>Chapter {s.current_chapter}/{book?.total_chapters || '?'}</p>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${pct}%` }}></div>
                    <span className="progress-label">{pct}%</span>
                  </div>
                </div>
                <div className="schedule-actions">
                  {s.is_active ? (
                    <button className="btn btn-sm btn-primary"
                      onClick={() => handleAdvanceChapter(s.id)}>
                      Next Chapter
                    </button>
                  ) : (
                    <span className="badge badge-success">Completed ✓</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  const SettingsPage = () => (
    <div className="page">
      <h1>⚙️ Settings</h1>

      <div className="settings-grid">
        <div className="card setting-card">
          <h3>📧 Email Notifications</h3>
          <p>Receive daily chapter summaries via email</p>
          <div className="setting-status">
            <span className="badge badge-success">Active</span>
            <small>user@example.com</small>
          </div>
        </div>

        <div className="card setting-card">
          <h3>🤖 Telegram</h3>
          <p>Get summaries on Telegram</p>
          <p className="hint">Set TELEGRAM_BOT_TOKEN in .env and chat_id in user settings</p>
        </div>

        <div className="card setting-card">
          <h3>💬 WhatsApp</h3>
          <p>Receive on WhatsApp</p>
          <p className="hint">Set Twilio credentials in .env</p>
        </div>

        <div className="card setting-card">
          <h3>⏰ Notification Time</h3>
          <p>Daily at 8:30 AM IST (configurable)</p>
          <p className="hint">Set NOTIFICATION_TIME in .env (default: 08:30)</p>
        </div>
      </div>

      <div className="card setup-guide">
        <h3>📋 Quick Setup Guide</h3>
        <ol>
          <li><strong>Upload Excel</strong> — Go to Books page and upload your books list</li>
          <li><strong>Schedule a Book</strong> — Click "Schedule" on any book to start daily reading</li>
          <li><strong>Configure .env</strong> — Add SMTP, Telegram, or Twilio credentials for notifications</li>
          <li><strong>Receive Daily</strong> — Get chapter summaries every morning at 8:30 AM</li>
          <li><strong>Track Progress</strong> — View progress on Dashboard and Schedule pages</li>
        </ol>
      </div>
    </div>
  );

  return (
    <div className="app">
      <NavBar />
      <main className="main-content">
        {page === 'dashboard' && <Dashboard />}
        {page === 'books' && <BooksPage />}
        {page === 'schedule' && <SchedulePage />}
        {page === 'settings' && <SettingsPage />}
      </main>
      <ToastContainer position="bottom-right" theme="dark" />
    </div>
  );
}

export default App;
