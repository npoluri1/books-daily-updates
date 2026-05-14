import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import Toggle from '../components/Toggle';

const Settings = () => {
  const { user, loadSchedules } = useApp();
  const [settings, setSettings] = useState({
    email: '', email_notifications: false,
    telegram_chat_id: '', telegram_notifications: false,
    whatsapp_number: '', whatsapp_notifications: false,
    notification_time: '08:30', timezone: 'Asia/Kolkata',
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const { api } = await import('../api');
      const u = JSON.parse(localStorage.getItem('book_user') || '{}');
      if (u.id) {
        const d = await api(`/api/users/${u.id}`);
        setSettings(p => ({ ...p, ...d }));
      }
    } catch (e) { console.error(e); }
  };

  const saveSettings = async () => {
    try {
      const { api, toast } = await import('../api');
      const u = JSON.parse(localStorage.getItem('book_user') || '{}');
      if (!u.id) return;
      const d = await api(`/api/users/${u.id}`, {
        method: 'PUT',
        body: JSON.stringify(settings),
      });
      setSettings(d);
      const { toast: t } = await import('react-toastify');
      t('Settings saved!', { type: 'success' });
    } catch (e) {
      const { toast: t } = await import('react-toastify');
      t(e.message, { type: 'error' });
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Notification <span>Settings</span></h1>
      </div>
      <div className="settings-grid">
        <div className="card settings-form-card">
          <h3>📧 Email</h3>
          <div className="settings-field">
            <label>Email Address</label>
            <input type="email" value={settings.email}
              onChange={e => setSettings({...settings, email: e.target.value})}
              placeholder="your@email.com" />
          </div>
          <div className="toggle-row">
            <span className="toggle-label">Email Notifications</span>
            <Toggle value={settings.email_notifications}
              onChange={() => setSettings({...settings, email_notifications: !settings.email_notifications})} />
          </div>
          <div className="channel-status">
            <span className={`dot ${settings.email ? 'active' : 'inactive'}`}></span>
            {settings.email ? 'Configured' : 'Not set'}
          </div>
        </div>
        <div className="card settings-form-card">
          <h3>🤖 Telegram</h3>
          <p className="hint">Set TELEGRAM_BOT_TOKEN in .env</p>
          <div className="settings-field">
            <label>Chat ID</label>
            <input type="text" value={settings.telegram_chat_id}
              onChange={e => setSettings({...settings, telegram_chat_id: e.target.value})}
              placeholder="123456789" />
          </div>
          <div className="toggle-row">
            <span className="toggle-label">Telegram Notifications</span>
            <Toggle value={settings.telegram_notifications}
              onChange={() => setSettings({...settings, telegram_notifications: !settings.telegram_notifications})} />
          </div>
          <div className="channel-status">
            <span className={`dot ${settings.telegram_chat_id ? 'active' : 'inactive'}`}></span>
            {settings.telegram_chat_id ? 'Chat ID set' : 'No Chat ID'}
          </div>
        </div>
        <div className="card settings-form-card">
          <h3>💬 WhatsApp</h3>
          <p className="hint">Set Twilio credentials in .env</p>
          <div className="settings-field">
            <label>WhatsApp Number</label>
            <input type="text" value={settings.whatsapp_number}
              onChange={e => setSettings({...settings, whatsapp_number: e.target.value})}
              placeholder="+919876543210" />
          </div>
          <div className="toggle-row">
            <span className="toggle-label">WhatsApp Notifications</span>
            <Toggle value={settings.whatsapp_notifications}
              onChange={() => setSettings({...settings, whatsapp_notifications: !settings.whatsapp_notifications})} />
          </div>
          <div className="channel-status">
            <span className={`dot ${settings.whatsapp_number ? 'active' : 'inactive'}`}></span>
            {settings.whatsapp_number ? 'Number set' : 'No number'}
          </div>
        </div>
        <div className="card settings-form-card">
          <h3>⏰ Schedule</h3>
          <div className="settings-field">
            <label>Daily Time</label>
            <input type="time" value={settings.notification_time}
              onChange={e => setSettings({...settings, notification_time: e.target.value})} />
          </div>
          <div className="settings-field">
            <label>Timezone</label>
            <select value={settings.timezone}
              onChange={e => setSettings({...settings, timezone: e.target.value})}>
              <option value="Asia/Kolkata">India (IST)</option>
              <option value="America/New_York">US East</option>
              <option value="America/Chicago">US Central</option>
              <option value="America/Los_Angeles">US West</option>
              <option value="Europe/London">UK</option>
              <option value="Europe/Berlin">Central Europe</option>
              <option value="Asia/Dubai">Dubai</option>
              <option value="Asia/Singapore">Singapore</option>
              <option value="Australia/Sydney">Sydney</option>
              <option value="Asia/Tokyo">Tokyo</option>
              <option value="UTC">UTC</option>
            </select>
          </div>
        </div>
      </div>
      <button className="btn btn-primary save-settings-btn btn-lg" onClick={saveSettings}>
        Save Settings
      </button>
    </div>
  );
};

export default Settings;
