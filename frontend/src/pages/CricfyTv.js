import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { api } from '../api';

const STATUS_ICONS = { live: '🔴', upcoming: '⏳', completed: '✅' };
const STATUS_COLORS = { live: '#dc2626', upcoming: '#d97706', completed: '#059669' };

const MatchCard = ({ match }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`cricfy-match-card card-3d-tilt ${match.status === 'live' ? 'match-live' : ''} ${match.is_featured ? 'match-featured' : ''}`}
      onClick={() => match.status !== 'completed' && setExpanded(!expanded)}
    >
      <div className="match-header">
        <span className="match-status-badge" style={{ background: STATUS_COLORS[match.status] }}>
          {STATUS_ICONS[match.status]} {match.status.toUpperCase()}
        </span>
        <span className="match-series">{match.series_name}</span>
        {match.is_featured && match.status === 'live' && <span className="match-live-dot pulse-ring"></span>}
      </div>
      <div className="match-teams">
        <div className="team team1">
          <img src={match.team1_logo || `https://placehold.co/80x80/1e40af/ffffff?text=${match.team1[0]}`} alt={match.team1} className="team-logo" />
          <span className="team-name">{match.team1}</span>
          {match.score_team1 && <span className="team-score">{match.score_team1}</span>}
          {match.overs_team1 && <span className="team-overs">({match.overs_team1} ov)</span>}
        </div>
        <div className="match-vs">
          <span className="vs-text">VS</span>
          {match.match_time && <span className="match-time">{match.match_time}</span>}
          {match.match_result && <span className="match-result">{match.match_result}</span>}
        </div>
        <div className="team team2">
          <img src={match.team2_logo || `https://placehold.co/80x80/dc2626/ffffff?text=${match.team2[0]}`} alt={match.team2} className="team-logo" />
          <span className="team-name">{match.team2}</span>
          {match.score_team2 && <span className="team-score">{match.score_team2}</span>}
          {match.overs_team2 && <span className="team-overs">({match.overs_team2} ov)</span>}
        </div>
      </div>
      <div className="match-footer">
        <span className="match-venue">{match.venue}</span>
        <span className="match-date">{new Date(match.match_date).toDateString()}</span>
        {match.live_url && match.status !== 'completed' && (
          <a href={match.live_url} target="_blank" rel="noopener noreferrer" className="btn btn-sm btn-primary watch-btn" onClick={e => e.stopPropagation()}>
            {match.status === 'live' ? '📺 Watch Live' : '🔔 Set Reminder'}
          </a>
        )}
      </div>
      {expanded && match.embed_url && (
        <div className="match-embed">
          <iframe src={match.embed_url} title={match.title} allowFullScreen frameBorder="0"></iframe>
        </div>
      )}
    </div>
  );
};

const LiveBanner = ({ matches }) => {
  if (!matches.length) return null;
  const live = matches[0];
  return (
    <div className="live-banner page-3d" onClick={() => document.getElementById('cricfy-matches')?.scrollIntoView({ behavior: 'smooth' })}>
      <div className="live-banner-glow"></div>
      <div className="live-banner-content">
        <div className="live-badge-pulse">
          <span className="live-dot"></span>
          <span className="live-text">LIVE</span>
        </div>
        <div className="live-banner-teams">
          <div className="banner-team">
            <img src={live.team1_logo || 'https://placehold.co/60x60/1e40af/ffffff?text=T1'} alt={live.team1} />
            <span>{live.team1}</span>
            <span className="banner-score">{live.score_team1 || ''}</span>
          </div>
          <div className="banner-vs">
            <span className="banner-vs-text">VS</span>
          </div>
          <div className="banner-team">
            <img src={live.team2_logo || 'https://placehold.co/60x60/dc2626/ffffff?text=T2'} alt={live.team2} />
            <span>{live.team2}</span>
            <span className="banner-score">{live.score_team2 || ''}</span>
          </div>
        </div>
        <div className="banner-info">
          <span>{live.series_name}</span>
          <span>|</span>
          <span>{live.venue}</span>
        </div>
      </div>
    </div>
  );
};

const CricfyTv = () => {
  const { page } = useApp();
  const [matches, setMatches] = useState([]);
  const [filter, setFilter] = useState('all');
  const [seriesFilter, setSeriesFilter] = useState('');
  const [series, setSeries] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadMatches();
    loadSeries();
  }, []);

  const loadMatches = async () => {
    setLoading(true);
    try {
      const data = await api('/api/cricfy/');
      setMatches(data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const loadSeries = async () => {
    try {
      const data = await api('/api/cricfy/series/list');
      setSeries(data);
    } catch (e) { console.error(e); }
  };

  const liveMatches = matches.filter(m => m.status === 'live');
  const upcomingMatches = matches.filter(m => m.status === 'upcoming');
  const completedMatches = matches.filter(m => m.status === 'completed');

  const filteredMatches = matches.filter(m => {
    if (filter === 'live' && m.status !== 'live') return false;
    if (filter === 'upcoming' && m.status !== 'upcoming') return false;
    if (filter === 'completed' && m.status !== 'completed') return false;
    if (seriesFilter && m.series_name !== seriesFilter) return false;
    return true;
  });

  return (
    <div className="page page-3d cricfy-page">
      <LiveBanner matches={liveMatches} />

      <div className="page-header">
        <h1 className="text-3d-strong">🏏 Cricfy TV</h1>
        <p className="page-subtitle">Live Cricket Streaming — Matches, Scores & Highlights</p>
      </div>

      <div className="cricfy-stats-row">
        <div className="stat-card-3d float-3d">
          <span className="stat-icon">🔴</span>
          <span className="stat-value">{liveMatches.length}</span>
          <span className="stat-label">Live Now</span>
        </div>
        <div className="stat-card-3d float-3d">
          <span className="stat-icon">⏳</span>
          <span className="stat-value">{upcomingMatches.length}</span>
          <span className="stat-label">Upcoming</span>
        </div>
        <div className="stat-card-3d float-3d">
          <span className="stat-icon">✅</span>
          <span className="stat-value">{completedMatches.length}</span>
          <span className="stat-label">Completed</span>
        </div>
        <div className="stat-card-3d float-3d">
          <span className="stat-icon">🏏</span>
          <span className="stat-value">{series.length}</span>
          <span className="stat-label">Series</span>
        </div>
      </div>

      <div className="cricfy-filters">
        <div className="filter-tabs">
          {[
            { k: 'all', l: '🏏 All Matches' },
            { k: 'live', l: '🔴 Live' },
            { k: 'upcoming', l: '⏳ Upcoming' },
            { k: 'completed', l: '✅ Completed' },
          ].map(f => (
            <button
              key={f.k}
              className={`btn btn-sm ${filter === f.k ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setFilter(f.k)}
            >
              {f.l}
            </button>
          ))}
        </div>
        {series.length > 0 && (
          <select className="currency-select" value={seriesFilter} onChange={e => setSeriesFilter(e.target.value)}>
            <option value="">All Series</option>
            {series.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        )}
      </div>

      {loading ? (
        <div className="loading-grid">
          {[1,2,3,4,5,6].map(i => <div key={i} className="shimmer-3d" style={{ height: 200, borderRadius: 16 }}></div>)}
        </div>
      ) : (
        <div id="cricfy-matches" className="cricfy-grid">
          {filteredMatches.map(m => <MatchCard key={m.id} match={m} />)}
          {filteredMatches.length === 0 && (
            <div className="empty-state">
              <span className="empty-icon">🏏</span>
              <p>No matches found</p>
            </div>
          )}
        </div>
      )}

      <div className="cricfy-features glass-deep page-3d">
        <h2 className="text-3d-strong">✨ Cricfy TV Features</h2>
        <div className="features-grid">
          <div className="feature-card card-3d-tilt">
            <span className="feature-icon">📺</span>
            <h3>Live Streaming</h3>
            <p>Watch live cricket matches from IPL, World Cup, BBL, SA20 & more</p>
          </div>
          <div className="feature-card card-3d-tilt">
            <span className="feature-icon">📊</span>
            <h3>Live Scores</h3>
            <p>Real-time ball-by-ball scores, overs, and match stats</p>
          </div>
          <div className="feature-card card-3d-tilt">
            <span className="feature-icon">📅</span>
            <h3>Match Schedule</h3>
            <p>Never miss a match with upcoming fixtures calendar</p>
          </div>
          <div className="feature-card card-3d-tilt">
            <span className="feature-icon">🎯</span>
            <h3>Multi-Series</h3>
            <p>International, T20 leagues, Test matches & more</p>
          </div>
          <div className="feature-card card-3d-tilt">
            <span className="feature-icon">🔔</span>
            <h3>Match Alerts</h3>
            <p>Get notified when your favorite team is playing</p>
          </div>
          <div className="feature-card card-3d-tilt">
            <span className="feature-icon">📱</span>
            <h3>Multi-Platform</h3>
            <p>Stream on YouTube, Hotstar, and other platforms</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CricfyTv;
