import React, { useState } from 'react';
import { useApp } from '../context/AppContext';

const Podcasts = () => {
  const { podcasts } = useApp();
  const [filter, setFilter] = useState('all');

  const platforms = [...new Set(podcasts.map(p => p.platform))];
  const filtered = filter === 'all' ? podcasts : podcasts.filter(p => p.platform === filter);

  const getPlatformIcon = (platform) => {
    const icons = {
      spotify: '🎧', apple: '🍎',
      youtube: '▶️', google: '🎯',
    };
    return icons[platform] || '🎙️';
  };

  return (
    <div className="page page-3d">
      <div className="page-header">
        <h1 className="page-title text-3d-strong">🎙️ <span>Podcasts</span></h1>
        <p className="page-subtitle">Book discussions, author interviews, and literary podcasts</p>
      </div>
      <div className="filter-bar">
        <button className={`btn btn-sm ${filter === 'all' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setFilter('all')}>All Episodes</button>
        {platforms.map(p => (
          <button key={p}
            className={`btn btn-sm ${filter === p ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setFilter(p)}>
            {getPlatformIcon(p)} {p}
          </button>
        ))}
      </div>
      <div className="podcast-grid">
        {filtered.map(ep => (
          <div key={ep.id} className="podcast-card card-3d-tilt">
            {ep.thumbnail_url ? (
              <img src={ep.thumbnail_url} alt={ep.title} className="podcast-thumb" />
            ) : (
              <div className="podcast-thumb-placeholder">
                <span>🎙️</span>
              </div>
            )}
            <div className="podcast-info">
              <h3>{ep.title}</h3>
              {ep.host && <p className="podcast-host">Hosted by {ep.host}</p>}
              <div className="podcast-meta">
                <span className="badge badge-info">{getPlatformIcon(ep.platform)} {ep.platform}</span>
                {ep.duration_minutes && <span className="badge badge-warning">{ep.duration_minutes} min</span>}
                {ep.episode_number && <span className="badge badge-info">Ep {ep.episode_number}</span>}
                {ep.listen_count > 0 && <span className="badge badge-info">📣 {ep.listen_count}</span>}
              </div>
              {ep.tags?.length > 0 && (
                <div className="podcast-tags">
                  {ep.tags.map((t, i) => <span key={i} className="tag">#{t}</span>)}
                </div>
              )}
              <div className="podcast-actions">
                {ep.embed_url ? (
                  <div className="podcast-embed">
                    <iframe src={ep.embed_url} title={ep.title} allowFullScreen loading="lazy" />
                  </div>
                ) : (
                  <a href={ep.audio_url} target="_blank" rel="noopener noreferrer"
                    className="btn btn-sm btn-primary">
                    ▶ Listen on {ep.platform}
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      {filtered.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🎙️</div>
          <h3>No Podcasts Found</h3>
        </div>
      )}
    </div>
  );
};

export default Podcasts;
