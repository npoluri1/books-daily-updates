import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import MediaCard from '../components/MediaCard';

const MediaGallery = () => {
  const { media } = useApp();
  const [filter, setFilter] = useState('all');

  const getFiltered = () => {
    if (filter === 'all') return media;
    return media.filter(m => m.media_type === filter || m.platform === filter);
  };

  const filtered = getFiltered();
  const platforms = [...new Set(media.map(m => m.platform))];

  return (
    <div className="page page-3d">
      <div className="page-header">
        <h1 className="page-title text-3d-strong">Media <span>Gallery</span></h1>
        <p className="page-subtitle">Book reviews, author interviews, and literary content from across the web</p>
      </div>
      <div className="filter-bar">
        <button className={`btn btn-sm ${filter === 'all' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setFilter('all')}>All</button>
        <button className={`btn btn-sm ${filter === 'video' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setFilter('video')}>🎥 Videos</button>
        <button className={`btn btn-sm ${filter === 'podcast' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setFilter('podcast')}>🎙️ Podcasts</button>
        {platforms.map(p => (
          <button key={p}
            className={`btn btn-sm ${filter === p ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setFilter(p)}>
            {p === 'youtube' ? '▶️' : p === 'tiktok' ? '🎵' : p === 'instagram' ? '📸' : p === 'spotify' ? '🎧' : p === 'apple' ? '🍎' : '🎬'} {p}
          </button>
        ))}
      </div>
      <div className="media-grid">
        {filtered.map(m => <MediaCard key={m.id} item={m} />)}
      </div>
      {filtered.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🎬</div>
          <h3>No Media Found</h3>
        </div>
      )}
    </div>
  );
};

export default MediaGallery;
