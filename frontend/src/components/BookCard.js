import React from 'react';
import { useApp } from '../context/AppContext';

const BookCard = ({ book, catalogView = false, showActions = true }) => {
  const { handleAddToCart, handleScheduleBook, schedules, setPage } = useApp();
  const scheduled = schedules.find(s => s.book_id === book.id && s.is_active);

  const pct = (c, t) => t ? Math.round((c / t) * 100) : 0;
  const progress = pct(book.current_chapter || 0, book.total_chapters || 100);

  return (
    <div
      className={`book-card ${catalogView ? 'catalog-card' : ''} ${scheduled ? 'scheduled' : ''} book-card-3d card-shine`}
      onClick={() => catalogView && setPage('book-' + book.id)}
    >
      {catalogView && book.images?.length > 0 && (
        <img src={book.images[0]?.url} alt={book.title} className="book-cover book-cover-3d" />
      )}
      <div className="book-card-header">
        <h3>{book.title}</h3>
        {book.author && <p className="book-author">by {book.author}</p>}
        {catalogView && book.categories?.length > 0 && (
          <div className="book-categories">
            {book.categories.map(c => (
              <span key={c.id} className="badge badge-info">{c.icon} {c.name}</span>
            ))}
          </div>
        )}
      </div>
      {!catalogView && (
        <div className="book-stats">
          <span>
            {book.current_chapter || 0}/{book.total_chapters || '?'} chapters
          </span>
          <div className="mini-progress">
            <div className="mini-progress-bar" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}
      {catalogView && (
        <div className="book-stats">
          <span>{book.pages || '?'} pages {book.publication_year ? `· ${book.publication_year}` : ''}</span>
        </div>
      )}
      {showActions && (
        <div className="book-card-actions">
          <span className="price-tag">${book.price?.toFixed(2)}</span>
          {catalogView ? (
            <>
              <button className="btn btn-sm btn-primary" onClick={e => { e.stopPropagation(); handleAddToCart(book.id, book.title); }}>
                Add to Cart
              </button>
              <button className="btn btn-sm btn-outline" onClick={e => { e.stopPropagation(); handleScheduleBook(book.id).then(() => {}).catch(() => {}); }}>
                Read
              </button>
            </>
          ) : (
            <>
              {scheduled ? (
                <span className="badge badge-success">Scheduled</span>
              ) : (
                <button className="btn btn-sm btn-primary" onClick={() => handleScheduleBook(book.id)}>
                  Schedule
                </button>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default BookCard;
