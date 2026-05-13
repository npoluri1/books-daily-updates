import React, { useEffect, useState, useRef } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  TextInput, FlatList, Alert, RefreshControl, SafeAreaView, Platform,
  Linking, StatusBar
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import notifee, { AndroidImportance } from '@notifee/react-native';

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

  useEffect(() => {
    loadUser();
    loadAll();
    setupNotifications();
  }, []);

  const setupNotifications = async () => {
    try {
      await notifee.requestPermission();
      const channelId = await notifee.createChannel({
        id: 'daily-reading',
        name: 'Daily Reading',
        importance: AndroidImportance.HIGH,
        vibration: true,
        sound: 'default',
      });
      await AsyncStorage.setItem('notification_channel', channelId);
    } catch (e) {
      console.log('Notification setup:', e.message);
    }
  };

  const showLocalNotification = async (title, body) => {
    try {
      const channelId = await AsyncStorage.getItem('notification_channel') || 'daily-reading';
      await notifee.displayNotification({
        title,
        body,
        android: {
          channelId,
          importance: AndroidImportance.HIGH,
          smallIcon: 'ic_notification',
          pressAction: { id: 'default' },
        },
      });
    } catch (e) {
      Alert.alert(title, body);
    }
  };

  const loadUser = async () => {
    try {
      let u = await AsyncStorage.getItem('book_user');
      if (!u) {
        u = await api('/api/users/', {
          method: 'POST',
          body: JSON.stringify({ email: 'user@example.com', name: 'Reader' }),
        });
        await AsyncStorage.setItem('book_user', JSON.stringify(u));
      } else {
        u = JSON.parse(u);
      }
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
      setBooks(b);
      setDailyReading(d);
      setSchedules(s);
    } catch (e) {}
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAll();
    setRefreshing(false);
  };

  const handleSendNotification = async () => {
    if (!dailyReading) return;
    await showLocalNotification(
      `${dailyReading.book_title} - Ch.${dailyReading.chapter_number}`,
      dailyReading.summary.substring(0, 200) + '...',
    );
    try {
      await api('/api/reading/send-notification?user_id=1', { method: 'POST' });
      Alert.alert('Sent', 'Chapter sent to your connected channels');
    } catch (e) {
      Alert.alert('Sent locally');
    }
  };

  const handleScheduleBook = async (bookId) => {
    try {
      await api('/api/reading/schedule', {
        method: 'POST',
        body: JSON.stringify({ book_id: bookId, user_id: 1 }),
      });
      Alert.alert('Scheduled', 'You will receive daily chapter summaries');
      loadAll();
    } catch (e) {
      Alert.alert('Error', e.message);
    }
  };

  const getProgress = (current, total) => {
    if (!total) return 0;
    return Math.round((current / total) * 100);
  };

  const Dashboard = () => (
    <ScrollView style={styles.page} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.pageTitle}>📚 Your Daily Reading</Text>
      {dailyReading ? (
        <View style={styles.card}>
          <View style={styles.readingHeader}>
            <View style={{ flex: 1 }}>
              <Text style={styles.bookTitle}>{dailyReading.book_title}</Text>
              <Text style={styles.chapterInfo}>
                Chapter {dailyReading.chapter_number}
                {dailyReading.chapter_title ? `: ${dailyReading.chapter_title}` : ''}
                {' · '}{dailyReading.reading_time_minutes} min
              </Text>
            </View>
            <View style={styles.progressCircle}>
              <Text style={styles.progressText}>{dailyReading.progress}%</Text>
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
            <Text style={styles.btnText}>Send to Phone & Channels</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>📖</Text>
          <Text style={styles.emptyTitle}>No Reading Scheduled</Text>
          <Text style={styles.emptyDesc}>Upload books and schedule one to start</Text>
        </View>
      )}
    </ScrollView>
  );

  const BooksTab = () => (
    <ScrollView style={styles.page} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.pageTitle}>📖 My Books</Text>
      {books.map((book) => {
        const scheduled = schedules.find(s => s.book_id === book.id && s.is_active);
        return (
          <TouchableOpacity key={book.id} style={[styles.bookCard, scheduled && styles.scheduledCard]}>
            <View style={styles.bookInfo}>
              <Text style={styles.bookName}>{book.title}</Text>
              {book.author && <Text style={styles.bookAuthor}>by {book.author}</Text>}
              <Text style={styles.bookStats}>
                📊 {book.current_chapter || 0}/{book.total_chapters || '?'} chapters
              </Text>
            </View>
            <View style={styles.bookActions}>
              {scheduled ? (
                <View style={styles.scheduledBadge}><Text style={styles.scheduledText}>Scheduled</Text></View>
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
          <Text style={styles.emptyIcon}>📂</Text>
          <Text style={styles.emptyTitle}>No Books Yet</Text>
          <Text style={styles.emptyDesc}>Upload Excel from web app to get started</Text>
        </View>
      )}
    </ScrollView>
  );

  const ScheduleTab = () => (
    <ScrollView style={styles.page} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.pageTitle}>📅 Reading Schedule</Text>
      {schedules.map((s) => {
        const book = books.find(b => b.id === s.book_id);
        const pct = getProgress(s.current_chapter, book?.total_chapters || 100);
        return (
          <View key={s.id} style={[styles.card, !s.is_active && styles.completedCard]}>
            <Text style={styles.bookTitle}>{book?.title || 'Book'}</Text>
            <Text style={styles.chapterInfo}>Chapter {s.current_chapter}/{book?.total_chapters || '?'}</Text>
            <View style={styles.progressBarBg}>
              <View style={[styles.progressBarFill, { width: `${pct}%` }]} />
            </View>
            <Text style={styles.progressLabel}>{pct}% complete</Text>
            {!s.is_active && <Text style={styles.completedText}>✅ Completed</Text>}
          </View>
        );
      })}
      {schedules.length === 0 && (
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>📅</Text>
          <Text style={styles.emptyTitle}>No Schedule</Text>
          <Text style={styles.emptyDesc}>Schedule a book from Books tab</Text>
        </View>
      )}
    </ScrollView>
  );

  const SettingsTab = () => (
    <ScrollView style={styles.page}>
      <Text style={styles.pageTitle}>⚙️ Settings</Text>
      <View style={styles.card}>
        <Text style={styles.settingTitle}>📧 Email</Text>
        <Text style={styles.settingDesc}>user@example.com</Text>
        <Text style={styles.settingStatus}>Active ✅</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.settingTitle}>🤖 Telegram</Text>
        <Text style={styles.settingDesc}>Set TELEGRAM_BOT_TOKEN in backend .env</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.settingTitle}>💬 WhatsApp</Text>
        <Text style={styles.settingDesc}>Set Twilio credentials in backend .env</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.settingTitle}>⏰ Notification Time</Text>
        <Text style={styles.settingDesc}>Daily at 8:30 AM IST</Text>
      </View>
      <TouchableOpacity style={styles.primaryBtn} onPress={() => showLocalNotification('Test Notification', 'Your daily reading reminder is working!')}>
        <Text style={styles.btnText}>🔔 Test Notification</Text>
      </TouchableOpacity>
    </ScrollView>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1e40af" />
      <View style={styles.header}>
        <Text style={styles.headerTitle}>📚 BooksDaily</Text>
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
          <TouchableOpacity
            key={tab.key}
            style={[styles.tab, page === tab.key && styles.activeTab]}
            onPress={() => setPage(tab.key)}
          >
            <Text style={styles.tabIcon}>{tab.icon}</Text>
            <Text style={[styles.tabLabel, page === tab.key && styles.activeTabLabel]}>{tab.label}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0f2f5' },
  header: {
    backgroundColor: '#1e40af',
    padding: 16,
    paddingTop: Platform.OS === 'android' ? 40 : 16,
  },
  headerTitle: { color: '#fff', fontSize: 20, fontWeight: '700' },
  content: { flex: 1 },
  page: { flex: 1, padding: 16 },
  pageTitle: { fontSize: 22, fontWeight: '700', marginBottom: 16, color: '#1f2937' },

  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  readingHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  bookTitle: { fontSize: 18, fontWeight: '700', color: '#1f2937' },
  chapterInfo: { fontSize: 13, color: '#6b7280', marginTop: 4 },
  summary: { fontSize: 15, lineHeight: 24, color: '#374151', marginBottom: 16 },
  pointsBox: { backgroundColor: '#eff6ff', borderRadius: 8, padding: 16, marginBottom: 16 },
  pointsTitle: { fontSize: 15, fontWeight: '700', color: '#1e40af', marginBottom: 8 },
  point: { fontSize: 14, color: '#374151', marginBottom: 6, lineHeight: 20 },
  progressCircle: {
    width: 56, height: 56, borderRadius: 28, borderWidth: 3, borderColor: '#3b82f6',
    alignItems: 'center', justifyContent: 'center', marginLeft: 12,
  },
  progressText: { fontSize: 14, fontWeight: '700', color: '#1e40af' },

  bookCard: {
    backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 10,
    flexDirection: 'row', alignItems: 'center',
    shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 4, elevation: 2,
    borderLeftWidth: 4, borderLeftColor: '#e5e7eb',
  },
  scheduledCard: { borderLeftColor: '#059669' },
  bookInfo: { flex: 1 },
  bookName: { fontSize: 16, fontWeight: '600', color: '#1f2937' },
  bookAuthor: { fontSize: 13, color: '#6b7280' },
  bookStats: { fontSize: 12, color: '#6b7280', marginTop: 4 },
  bookActions: { marginLeft: 12 },

  primaryBtn: {
    backgroundColor: '#1e40af', borderRadius: 8, padding: 14, alignItems: 'center',
  },
  btnText: { color: '#fff', fontSize: 15, fontWeight: '600' },
  smallBtn: {
    backgroundColor: '#1e40af', borderRadius: 6, paddingVertical: 6, paddingHorizontal: 14,
  },
  smallBtnText: { color: '#fff', fontSize: 13, fontWeight: '600' },
  scheduledBadge: {
    backgroundColor: '#d1fae5', borderRadius: 12, paddingVertical: 4, paddingHorizontal: 12,
  },
  scheduledText: { color: '#059669', fontSize: 12, fontWeight: '600' },

  progressBarBg: { height: 8, backgroundColor: '#e5e7eb', borderRadius: 4, marginVertical: 8, overflow: 'hidden' },
  progressBarFill: { height: '100%', backgroundColor: '#3b82f6', borderRadius: 4 },
  progressLabel: { fontSize: 12, color: '#6b7280' },
  completedCard: { opacity: 0.7 },
  completedText: { color: '#059669', fontWeight: '600', marginTop: 4 },

  emptyState: { alignItems: 'center', paddingVertical: 60 },
  emptyIcon: { fontSize: 48, marginBottom: 12 },
  emptyTitle: { fontSize: 18, fontWeight: '600', color: '#374151', marginBottom: 8 },
  emptyDesc: { fontSize: 14, color: '#6b7280', textAlign: 'center' },

  settingTitle: { fontSize: 16, fontWeight: '600', marginBottom: 4 },
  settingDesc: { fontSize: 14, color: '#6b7280', marginBottom: 4 },
  settingStatus: { fontSize: 13, color: '#059669', fontWeight: '500' },

  tabBar: {
    flexDirection: 'row', backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: '#e5e7eb',
    paddingBottom: Platform.OS === 'ios' ? 20 : 8, paddingTop: 8,
  },
  tab: { flex: 1, alignItems: 'center', paddingVertical: 4 },
  activeTab: { },
  tabIcon: { fontSize: 20 },
  tabLabel: { fontSize: 11, color: '#6b7280', marginTop: 2 },
  activeTabLabel: { color: '#1e40af', fontWeight: '600' },
});
