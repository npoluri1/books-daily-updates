import React, { useEffect, useState, useRef } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  TextInput, Alert, RefreshControl, SafeAreaView, Platform,
  StatusBar, Switch, Animated, Dimensions
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import notifee, { AndroidImportance } from '@notifee/react-native';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const API_BASE = 'http://localhost:8000';

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

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [dailyReading, setDailyReading] = useState(null);
  const [books, setBooks] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [user, setUser] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [settings, setSettings] = useState({
    email: '', email_notifications: false,
    telegram_chat_id: '', telegram_notifications: false,
    whatsapp_number: '', whatsapp_notifications: false,
    notification_time: '08:30', timezone: 'Asia/Kolkata',
  });

  useEffect(() => {
    loadUser();
    loadAll();
    setupNotifications();
  }, []);

  const setupNotifications = async () => {
    try {
      await notifee.requestPermission();
      const channelId = await notifee.createChannel({
        id: 'daily-reading', name: 'Daily Reading',
        importance: AndroidImportance.HIGH, vibration: true, sound: 'default',
      });
      await AsyncStorage.setItem('notification_channel', channelId);
    } catch (e) { console.log('Notification setup:', e.message); }
  };

  const showLocalNotification = async (title, body) => {
    try {
      const channelId = await AsyncStorage.getItem('notification_channel') || 'daily-reading';
      await notifee.displayNotification({ title, body, android: { channelId, importance: AndroidImportance.HIGH, smallIcon: 'ic_notification', pressAction: { id: 'default' } } });
    } catch (e) { Alert.alert(title, body); }
  };

  const loadUser = async () => {
    try {
      let u = await AsyncStorage.getItem('book_user');
      if (!u) {
        u = await api('/api/users/', { method: 'POST', body: JSON.stringify({ email: 'user@example.com', name: 'Reader' }) });
        await AsyncStorage.setItem('book_user', JSON.stringify(u));
      } else { u = JSON.parse(u); }
      setUser(u);
    } catch (e) {}
  };

  const loadAll = async () => {
    try {
      const [b, d, s] = await Promise.all([
        api('/api/books/').catch(() => []),
        api('/api/reading/daily?user_id=1').catch(() => null),
        api('/api/reading/schedules?user_id=1').catch(() => []),
      ]);
      setBooks(b); setDailyReading(d); setSchedules(s);
    } catch (e) {}
  };

  const loadSettings = async () => {
    try {
      const u = JSON.parse(await AsyncStorage.getItem('book_user') || '{}');
      if (u.id) {
        const data = await api(`/api/users/${u.id}`);
        setSettings(prev => ({ ...prev, ...data }));
      }
    } catch (e) {}
  };

  const saveSettings = async () => {
    try {
      const u = JSON.parse(await AsyncStorage.getItem('book_user') || '{}');
      if (!u.id) return;
      const data = await api(`/api/users/${u.id}`, { method: 'PUT', body: JSON.stringify(settings) });
      setSettings(data);
      Alert.alert('Saved', 'Notification settings updated');
    } catch (e) { Alert.alert('Error', e.message); }
  };

  const onRefresh = async () => { setRefreshing(true); await loadAll(); setRefreshing(false); };

  const handleSendNotification = async () => {
    if (!dailyReading) return;
    await showLocalNotification(`${dailyReading.book_title} - Ch.${dailyReading.chapter_number}`, dailyReading.summary.substring(0, 200) + '...');
    try { await api('/api/reading/send-notification?user_id=1', { method: 'POST' }); Alert.alert('Sent', 'Chapter sent to your connected channels'); }
    catch (e) { Alert.alert('Sent locally'); }
  };

  const handleScheduleBook = async (bookId) => {
    try {
      await api('/api/reading/schedule', { method: 'POST', body: JSON.stringify({ book_id: bookId, user_id: 1 }) });
      Alert.alert('Scheduled', 'You will receive daily chapter summaries');
      loadAll();
    } catch (e) { Alert.alert('Error', e.message); }
  };

  const getProgress = (current, total) => { if (!total) return 0; return Math.round((current / total) * 100); };

  const activeSchedules = schedules.filter(s => s.is_active).length;
  const totalChaptersRead = schedules.reduce((sum, s) => sum + (s.current_chapter || 0), 0);

  const Dashboard = () => (
    <ScrollView style={styles.page} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.pageTitle}>Your <Text style={styles.highlight}>Reading</Text> Today</Text>

      <View style={styles.statsRow}>
        <View style={[styles.statCard, { borderLeftColor: '#0071e3' }]}>
          <Text style={styles.statNumber}>{books.length}</Text>
          <Text style={styles.statLabel}>Books</Text>
        </View>
        <View style={[styles.statCard, { borderLeftColor: '#30d158' }]}>
          <Text style={styles.statNumber}>{activeSchedules}</Text>
          <Text style={styles.statLabel}>Active</Text>
        </View>
        <View style={[styles.statCard, { borderLeftColor: '#ff9f0a' }]}>
          <Text style={styles.statNumber}>{totalChaptersRead}</Text>
          <Text style={styles.statLabel}>Chapters</Text>
        </View>
      </View>

      {dailyReading ? (
        <View style={styles.dailyCard}>
          <View style={styles.readingHeader}>
            <View style={{ flex: 1 }}>
              <Text style={styles.bookTitle}>{dailyReading.book_title}</Text>
              <Text style={styles.chapterInfo}>Chapter {dailyReading.chapter_number}{dailyReading.chapter_title ? `: ${dailyReading.chapter_title}` : ''} · {dailyReading.reading_time_minutes} min</Text>
            </View>
            <View style={styles.progressCircle}>
              <Text style={styles.progressCircleText}>{Math.round(dailyReading.progress)}%</Text>
            </View>
          </View>
          <Text style={styles.summary}>{dailyReading.summary}</Text>
          <View style={styles.pointsBox}>
            <Text style={styles.pointsTitle}>Key Takeaways</Text>
            {dailyReading.key_points.map((p, i) => (
              <Text key={i} style={styles.point}>• {p}</Text>
            ))}
          </View>
          <TouchableOpacity style={styles.primaryBtn} onPress={handleSendNotification}>
            <Text style={styles.primaryBtnText}>Send to My Phone</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.emptyState}>
          <View style={styles.emptyIconCircle}><Text style={styles.emptyIcon}>📖</Text></View>
          <Text style={styles.emptyTitle}>No Reading Scheduled</Text>
          <Text style={styles.emptyDesc}>Upload books and schedule one to start receiving daily summaries</Text>
        </View>
      )}
    </ScrollView>
  );

  const BooksTab = () => (
    <ScrollView style={styles.page} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.pageTitle}>My <Text style={styles.highlight}>Books</Text></Text>
      {books.map((book) => {
        const scheduled = schedules.find(s => s.book_id === book.id && s.is_active);
        const pct = getProgress(book.current_chapter || 0, book.total_chapters || 100);
        return (
          <TouchableOpacity key={book.id} style={[styles.bookCard, scheduled && { borderLeftColor: '#30d158' }]}>
            <View style={styles.bookInfo}>
              <Text style={styles.bookName}>{book.title}</Text>
              {book.author && <Text style={styles.bookAuthor}>by {book.author}</Text>}
              <View style={styles.bookMeta}>
                <Text style={styles.bookStats}>{book.current_chapter || 0}/{book.total_chapters || '?'}</Text>
                <View style={styles.miniProgressBg}>
                  <View style={[styles.miniProgressFill, { width: `${pct}%` }]} />
                </View>
              </View>
            </View>
            <View style={styles.bookActions}>
              {scheduled ? (
                <View style={styles.scheduledBadge}><Text style={styles.scheduledBadgeText}>Active</Text></View>
              ) : (
                <TouchableOpacity style={styles.smallBtn} onPress={() => handleScheduleBook(book.id)}>
                  <Text style={styles.smallBtnText}>Schedule</Text>
                </TouchableOpacity>
              )}
            </View>
          </TouchableOpacity>
        );
      })}
      {books.length === 0 && (
        <View style={styles.emptyState}>
          <View style={styles.emptyIconCircle}><Text style={styles.emptyIcon}>📂</Text></View>
          <Text style={styles.emptyTitle}>No Books Yet</Text>
          <Text style={styles.emptyDesc}>Upload an Excel file from the web app to get started</Text>
        </View>
      )}
    </ScrollView>
  );

  const ScheduleTab = () => (
    <ScrollView style={styles.page} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.pageTitle}>Reading <Text style={styles.highlight}>Schedule</Text></Text>
      {schedules.map((s) => {
        const book = books.find(b => b.id === s.book_id);
        const pct = getProgress(s.current_chapter, book?.total_chapters || 100);
        return (
          <View key={s.id} style={[styles.card, !s.is_active && { opacity: 0.6 }]}>
            <Text style={styles.bookTitle}>{book?.title || 'Unknown Book'}</Text>
            <Text style={styles.chapterInfo}>Chapter {s.current_chapter}/{book?.total_chapters || '?'}</Text>
            <View style={styles.progressBarBg}>
              <View style={[styles.progressBarFill, { width: `${pct}%` }]} />
            </View>
            <Text style={styles.progressPct}>{pct}% complete</Text>
            {!s.is_active && <Text style={styles.completedText}>✅ Completed</Text>}
          </View>
        );
      })}
      {schedules.length === 0 && (
        <View style={styles.emptyState}>
          <View style={styles.emptyIconCircle}><Text style={styles.emptyIcon}>📅</Text></View>
          <Text style={styles.emptyTitle}>No Schedule</Text>
          <Text style={styles.emptyDesc}>Schedule a book from the Books tab to begin</Text>
        </View>
      )}
    </ScrollView>
  );

  const SettingsTab = () => {
    useEffect(() => { loadSettings(); }, []);
    return (
      <ScrollView style={styles.page} keyboardShouldPersistTaps="handled">
        <Text style={styles.pageTitle}>Notification <Text style={styles.highlight}>Settings</Text></Text>

        <View style={styles.card}>
          <Text style={styles.settingHeader}>📧 Email</Text>
          <TextInput style={styles.input} placeholder="your@email.com" placeholderTextColor="#aeaeb2"
            value={settings.email} onChangeText={v => setSettings({...settings, email: v})}
            keyboardType="email-address" autoCapitalize="none" />
          <View style={styles.toggleRow}>
            <Text style={styles.toggleLabel}>Notifications</Text>
            <Switch value={settings.email_notifications} onValueChange={v => setSettings({...settings, email_notifications: v})}
              trackColor={{ false: '#e5e5ea', true: '#b3d4ff' }} thumbColor={settings.email_notifications ? '#0071e3' : '#fff'} />
          </View>
          {settings.email ? <Text style={styles.statusText}>✓ {settings.email}</Text> : <Text style={styles.statusMuted}>No email set</Text>}
        </View>

        <View style={styles.card}>
          <Text style={styles.settingHeader}>🤖 Telegram</Text>
          <Text style={styles.hintText}>Set TELEGRAM_BOT_TOKEN in .env, enter Chat ID below</Text>
          <TextInput style={styles.input} placeholder="123456789" placeholderTextColor="#aeaeb2"
            value={settings.telegram_chat_id} onChangeText={v => setSettings({...settings, telegram_chat_id: v})}
            keyboardType="number-pad" />
          <View style={styles.toggleRow}>
            <Text style={styles.toggleLabel}>Notifications</Text>
            <Switch value={settings.telegram_notifications} onValueChange={v => setSettings({...settings, telegram_notifications: v})}
              trackColor={{ false: '#e5e5ea', true: '#b3d4ff' }} thumbColor={settings.telegram_notifications ? '#0071e3' : '#fff'} />
          </View>
          {settings.telegram_chat_id ? <Text style={styles.statusText}>✓ Chat ID set</Text> : <Text style={styles.statusMuted}>No Chat ID</Text>}
        </View>

        <View style={styles.card}>
          <Text style={styles.settingHeader}>💬 WhatsApp</Text>
          <Text style={styles.hintText}>Set Twilio credentials in .env, enter number below</Text>
          <TextInput style={styles.input} placeholder="+919876543210" placeholderTextColor="#aeaeb2"
            value={settings.whatsapp_number} onChangeText={v => setSettings({...settings, whatsapp_number: v})}
            keyboardType="phone-pad" />
          <View style={styles.toggleRow}>
            <Text style={styles.toggleLabel}>Notifications</Text>
            <Switch value={settings.whatsapp_notifications} onValueChange={v => setSettings({...settings, whatsapp_notifications: v})}
              trackColor={{ false: '#e5e5ea', true: '#b3d4ff' }} thumbColor={settings.whatsapp_notifications ? '#0071e3' : '#fff'} />
          </View>
          {settings.whatsapp_number ? <Text style={styles.statusText}>✓ Number set</Text> : <Text style={styles.statusMuted}>No number</Text>}
        </View>

        <View style={styles.card}>
          <Text style={styles.settingHeader}>⏰ Schedule</Text>
          <TextInput style={styles.input} placeholder="08:30" placeholderTextColor="#aeaeb2"
            value={settings.notification_time} onChangeText={v => setSettings({...settings, notification_time: v})} />
          <TextInput style={styles.input} placeholder="Asia/Kolkata" placeholderTextColor="#aeaeb2"
            value={settings.timezone} onChangeText={v => setSettings({...settings, timezone: v})} />
        </View>

        <TouchableOpacity style={styles.primaryBtn} onPress={saveSettings}>
          <Text style={styles.primaryBtnText}>Save Settings</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />
      <View style={styles.header}>
        <View style={styles.headerIcon}><Text style={{ fontSize: 18 }}>📚</Text></View>
        <Text style={styles.headerTitle}>BooksDaily</Text>
      </View>
      <View style={styles.content}>
        {page === 'dashboard' && <Dashboard />}
        {page === 'books' && <BooksTab />}
        {page === 'schedule' && <ScheduleTab />}
        {page === 'settings' && <SettingsTab />}
      </View>
      <View style={styles.tabBar}>
        {[
          { key: 'dashboard', icon: '📊', label: 'Today' },
          { key: 'books', icon: '📖', label: 'Books' },
          { key: 'schedule', icon: '📅', label: 'Schedule' },
          { key: 'settings', icon: '⚙️', label: 'Settings' },
        ].map((tab) => (
          <TouchableOpacity key={tab.key} style={[styles.tab, page === tab.key && styles.activeTab]} onPress={() => setPage(tab.key)}>
            <Text style={styles.tabIcon}>{tab.icon}</Text>
            <Text style={[styles.tabLabel, page === tab.key && styles.activeTabLabel]}>{tab.label}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f2f2f7' },

  header: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    backgroundColor: '#1a1a2e', padding: 16,
    paddingTop: Platform.OS === 'android' ? 40 : 16,
  },
  headerIcon: {
    width: 30, height: 30, borderRadius: 7,
    backgroundColor: '#0071e3', alignItems: 'center', justifyContent: 'center',
  },
  headerTitle: { color: '#fff', fontSize: 18, fontWeight: '700', letterSpacing: -0.3 },

  content: { flex: 1 },
  page: { flex: 1, padding: 16 },

  pageTitle: {
    fontSize: 26, fontWeight: '800', letterSpacing: -0.5,
    marginBottom: 18, color: '#1d1d1f',
  },
  highlight: { color: '#0071e3' },

  statsRow: { flexDirection: 'row', gap: 10, marginBottom: 20 },
  statCard: {
    flex: 1, backgroundColor: '#fff', borderRadius: 14, padding: 14,
    borderLeftWidth: 3, shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04, shadowRadius: 4, elevation: 2,
  },
  statNumber: { fontSize: 22, fontWeight: '800', color: '#1d1d1f' },
  statLabel: { fontSize: 12, color: '#8e8e93', marginTop: 2, fontWeight: '500' },

  dailyCard: {
    backgroundColor: '#1a1a2e', borderRadius: 20, padding: 24,
    shadowColor: '#000', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15, shadowRadius: 16, elevation: 8,
  },
  readingHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  bookTitle: { fontSize: 18, fontWeight: '700', color: '#fff' },
  chapterInfo: { fontSize: 13, color: 'rgba(255,255,255,0.6)', marginTop: 4 },
  progressCircle: {
    width: 56, height: 56, borderRadius: 28, borderWidth: 3, borderColor: '#0071e3',
    alignItems: 'center', justifyContent: 'center', marginLeft: 12,
  },
  progressCircleText: { fontSize: 14, fontWeight: '700', color: '#fff' },

  summary: { fontSize: 15, lineHeight: 24, color: 'rgba(255,255,255,0.85)', marginBottom: 16 },

  pointsBox: {
    backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 14,
    padding: 18, marginBottom: 16, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
  },
  pointsTitle: { fontSize: 14, fontWeight: '700', color: 'rgba(255,255,255,0.9)', marginBottom: 10 },
  point: { fontSize: 13, color: 'rgba(255,255,255,0.75)', marginBottom: 6, lineHeight: 20 },

  card: {
    backgroundColor: '#fff', borderRadius: 16, padding: 20,
    marginBottom: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04, shadowRadius: 6, elevation: 2,
  },

  bookCard: {
    backgroundColor: '#fff', borderRadius: 14, padding: 16, marginBottom: 10,
    flexDirection: 'row', alignItems: 'center',
    shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04, shadowRadius: 4, elevation: 2,
    borderLeftWidth: 3, borderLeftColor: '#e5e5ea',
  },
  bookInfo: { flex: 1 },
  bookName: { fontSize: 16, fontWeight: '700', color: '#1d1d1f' },
  bookAuthor: { fontSize: 13, color: '#8e8e93', marginTop: 2 },
  bookMeta: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 8 },
  bookStats: { fontSize: 12, color: '#8e8e93', fontWeight: '500' },
  miniProgressBg: { flex: 1, height: 4, backgroundColor: '#e5e5ea', borderRadius: 2, overflow: 'hidden' },
  miniProgressFill: { height: '100%', backgroundColor: '#0071e3', borderRadius: 2 },
  bookActions: { marginLeft: 12 },

  primaryBtn: {
    backgroundColor: '#0071e3', borderRadius: 12, padding: 16, alignItems: 'center',
    shadowColor: '#0071e3', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3, shadowRadius: 8, elevation: 4,
  },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  smallBtn: {
    backgroundColor: '#0071e3', borderRadius: 8, paddingVertical: 8, paddingHorizontal: 16,
  },
  smallBtnText: { color: '#fff', fontSize: 13, fontWeight: '600' },
  scheduledBadge: {
    backgroundColor: '#e8f8ee', borderRadius: 20, paddingVertical: 4, paddingHorizontal: 14,
  },
  scheduledBadgeText: { color: '#248a3d', fontSize: 12, fontWeight: '600' },

  progressBarBg: { height: 6, backgroundColor: '#e5e5ea', borderRadius: 3, marginVertical: 8, overflow: 'hidden' },
  progressBarFill: { height: '100%', backgroundColor: '#0071e3', borderRadius: 3 },
  progressPct: { fontSize: 12, color: '#8e8e93' },
  completedText: { color: '#30d158', fontWeight: '700', marginTop: 4 },

  emptyState: { alignItems: 'center', paddingVertical: 60 },
  emptyIconCircle: {
    width: 72, height: 72, borderRadius: 20,
    backgroundColor: '#e8f0fe', alignItems: 'center', justifyContent: 'center',
    marginBottom: 16,
  },
  emptyIcon: { fontSize: 32 },
  emptyTitle: { fontSize: 18, fontWeight: '700', color: '#1d1d1f', marginBottom: 8 },
  emptyDesc: { fontSize: 14, color: '#8e8e93', textAlign: 'center', lineHeight: 20, paddingHorizontal: 20 },

  settingHeader: { fontSize: 16, fontWeight: '700', color: '#1d1d1f', marginBottom: 12 },
  hintText: { fontSize: 12, color: '#aeaeb2', marginBottom: 10, lineHeight: 16 },

  input: {
    backgroundColor: '#f2f2f7', borderRadius: 10, padding: 12, fontSize: 15,
    color: '#1d1d1f', marginBottom: 12, fontFamily: Platform.OS === 'ios' ? 'SF Pro' : undefined,
  },

  toggleRow: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingVertical: 8, borderTopWidth: 1, borderTopColor: '#f2f2f7',
  },
  toggleLabel: { fontSize: 15, fontWeight: '500', color: '#1d1d1f' },
  statusText: { fontSize: 12, color: '#30d158', fontWeight: '500', marginTop: 4 },
  statusMuted: { fontSize: 12, color: '#aeaeb2', marginTop: 4 },

  tabBar: {
    flexDirection: 'row', backgroundColor: 'rgba(255,255,255,0.85)',
    backdropFilter: 'blur(20px)',
    borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.06)',
    paddingBottom: Platform.OS === 'ios' ? 20 : 8, paddingTop: 8,
  },
  tab: { flex: 1, alignItems: 'center', paddingVertical: 4 },
  activeTab: { },
  tabIcon: { fontSize: 20 },
  tabLabel: { fontSize: 10, color: '#8e8e93', marginTop: 2, fontWeight: '500' },
  activeTabLabel: { color: '#0071e3', fontWeight: '700' },
});
