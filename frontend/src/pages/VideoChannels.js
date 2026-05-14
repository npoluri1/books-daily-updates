import React, { useState } from 'react';
import { useApp } from '../context/AppContext';

const PLATFORM_ICONS = {
  youtube: { icon: '▶️', color: '#ff0000' },
  tiktok: { icon: '🎵', color: '#000000' },
  instagram: { icon: '📸', color: '#e4405f' },
};

const VideoChannels = () => {
  const { playlists } = useApp();
  const [activePlaylist, setActivePlaylist] = useState(null);

  const featured = playlists.filter(p => p.is_featured);
  const other = playlists.filter(p => !p.is_featured);

  return (
    <div className="page page-3d">
      <div className="page-header">
        <h1 className="page-title text-3d-strong">📹 Video <span>Channels</span></h1>
        <p className="page-subtitle">Curated book videos from YouTube, TikTok, and Instagram</p>
      </div>

      <div className="playlist-grid">
        <h2 className="section-title">⭐ Featured Channels</h2>
        <div className="channels-row">
          {featured.map(p => (
            <div
              key={p.id}
              className={`channel-card card-3d-tilt ${activePlaylist === p.id ? 'active pulse-ring' : ''}`}
              onClick={() => setActivePlaylist(activePlaylist === p.id ? null : p.id)}
            >
              <div className="channel-header">
                <div className="channel-platform-badge" style={{
                  background: PLATFORM_ICONS[p.platform]?.color || '#0071e3'
                }}>
                  {PLATFORM_ICONS[p.platform]?.icon || '🎬'} {p.platform}
                </div>
                {p.thumbnail_url && (
                  <img src={p.thumbnail_url} alt={p.name} className="channel-thumb" />
                )}
              </div>
              <div className="channel-info">
                <h3>{p.name}</h3>
                {p.channel_name && <p className="channel-name">{p.channel_name}</p>}
                {p.description && <p className="channel-desc">{p.description}</p>}
                {p.channel_url && (
                  <a href={p.channel_url} target="_blank" rel="noopener noreferrer"
                    className="btn btn-sm btn-outline">
                    Visit Channel ↗
                  </a>
                )}
              </div>
              {activePlaylist === p.id && p.videos?.length > 0 && (
                <div className="playlist-videos">
                  <h4>🎵 {p.videos.length} videos</h4>
                  {p.videos.map(v => (
                    <div key={v.id} className="video-item">
                      {v.embed_url ? (
                        <div className="video-embed-sm">
                          <iframe src={v.embed_url} title={v.title} allowFullScreen loading="lazy" />
                        </div>
                      ) : (
                        <div className="video-thumb-sm" style={{
                          background: v.thumbnail_url ? `url(${v.thumbnail_url}) center/cover` : '#1a1a2e'
                        }}>
                          <span className="play-icon-sm">▶</span>
                        </div>
                      )}
                      <div className="video-item-info">
                        <strong>{v.title}</strong>
                        <div className="video-item-meta">
                          <span className="badge badge-info">{v.platform}</span>
                          {v.duration_minutes && <span>{v.duration_minutes}m</span>}
                        </div>
                        <a href={v.url} target="_blank" rel="noopener noreferrer"
                          className="btn btn-sm btn-primary">\u25B6 Watch</a>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {other.length > 0 && (
          <>
            <h2 className="section-title">More Channels</h2>
            <div className="channels-row">
              {other.map(p => (
                <div
                  key={p.id}
                  className={`channel-card ${activePlaylist === p.id ? 'active' : ''}`}
                  onClick={() => setActivePlaylist(activePlaylist === p.id ? null : p.id)}
                >
                  <div className="channel-header">
                    <div className="channel-platform-badge" style={{
                      background: PLATFORM_ICONS[p.platform]?.color || '#0071e3'
                    }}>
                  {PLATFORM_ICONS[p.platform]?.icon || '🎬'} {p.platform}
                    </div>
                  </div>
                  <div className="channel-info">
                    <h3>{p.name}</h3>
                    {p.channel_name && <p className="channel-name">{p.channel_name}</p>}
                  </div>
                  {activePlaylist === p.id && p.videos?.length > 0 && (
                    <div className="playlist-videos">
                      {p.videos.map(v => (
                        <div key={v.id} className="video-item">
                          <div className="video-item-info">
                            <strong>{v.title}</strong>
                            <a href={v.url} target="_blank" rel="noopener noreferrer"
              className="btn btn-sm btn-primary">▶ Watch</a>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {playlists.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📹</div>
          <h3>No Video Channels Yet</h3>
          <p>Video playlists and channels will appear here</p>
        </div>
      )}
    </div>
  );
};

export default VideoChannels;
