import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../api';

const AppContext = createContext();

export const useApp = () => useContext(AppContext);

export const AppProvider = ({ children }) => {
  const [page, setPage] = useState('dashboard');
  const [books, setBooks] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [categories, setCategories] = useState([]);
  const [dailyReading, setDailyReading] = useState(null);
  const [schedules, setSchedules] = useState([]);
  const [user, setUser] = useState(null);
  const [cart, setCart] = useState({ items: [], total_items: 0, subtotal: 0 });
  const [media, setMedia] = useState([]);
  const [podcasts, setPodcasts] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [cricfyMatches, setCricfyMatches] = useState([]);
  const [orders, setOrders] = useState([]);
  const [shippingZones, setShippingZones] = useState([]);
  const [currencies, setCurrencies] = useState([]);
  const [countries, setCountries] = useState({});
  const [selectedCurrency, setSelectedCurrency] = useState('USD');
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(false);

  const USER_ID = 1;

  useEffect(() => {
    initUser();
    loadInitialData();
  }, []);

  const initUser = async () => {
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
    } catch (e) { console.error(e); }
  };

  const loadInitialData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadCatalog(), loadCategories(), loadDailyReading(),
        loadSchedules(), loadCart(), loadMedia(), loadPodcasts(),
        loadPlaylists(), loadDashboard(), loadCricfyMatches(),
      ]);
      loadOrders();
      loadShippingZones();
      loadCurrencies();
      loadCountries();
    } finally {
      setLoading(false);
    }
  };

  const loadDashboard = async () => {
    try { setDashboard(await api(`/api/dashboard?user_id=${USER_ID}`)); }
    catch (e) { console.error(e); }
  };

  const loadCatalog = async (params = '') => {
    try { setCatalog(await api(`/api/catalog/${params}`)); }
    catch (e) { console.error(e); }
  };

  const loadCategories = async () => {
    try { setCategories(await api('/api/catalog/categories')); }
    catch (e) { console.error(e); }
  };

  const loadDailyReading = async () => {
    try { setDailyReading(await api(`/api/reading/daily?user_id=${USER_ID}`)); }
    catch (e) { setDailyReading(null); }
  };

  const loadSchedules = async () => {
    try { setSchedules(await api(`/api/reading/schedules?user_id=${USER_ID}`)); }
    catch (e) { setSchedules([]); }
  };

  const loadCart = async () => {
    try {
      setCart(await api(`/api/store/cart?user_id=${USER_ID}&currency=${selectedCurrency}`));
    } catch (e) { setCart({ items: [], total_items: 0, subtotal: 0 }); }
  };

  const loadMedia = async () => {
    try { setMedia(await api('/api/media/')); }
    catch (e) { setMedia([]); }
  };

  const loadPodcasts = async () => {
    try { setPodcasts(await api('/api/podcasts/')); }
    catch (e) { setPodcasts([]); }
  };

  const loadPlaylists = async () => {
    try { setPlaylists(await api('/api/videos/playlists')); }
    catch (e) { setPlaylists([]); }
  };

  const loadOrders = async () => {
    try { setOrders(await api(`/api/store/orders?user_id=${USER_ID}`)); }
    catch (e) { setOrders([]); }
  };

  const loadShippingZones = async () => {
    try { setShippingZones(await api('/api/store/shipping-zones')); }
    catch (e) { setShippingZones([]); }
  };

  const loadCurrencies = async () => {
    try { setCurrencies(await api('/api/store/currencies')); }
    catch (e) { setCurrencies([]); }
  };

  const loadCricfyMatches = async () => {
    try { setCricfyMatches(await api('/api/cricfy/')); }
    catch (e) { setCricfyMatches([]); }
  };

  const loadCountries = async () => {
    try { setCountries(await api('/api/store/countries')); }
    catch (e) { setCountries({}); }
  };

  const handleScheduleBook = async (bookId) => {
    try {
      await api('/api/reading/schedule', {
        method: 'POST',
        body: JSON.stringify({ book_id: bookId, user_id: USER_ID }),
      });
      loadSchedules();
      return true;
    } catch (e) { throw e; }
  };

  const handleAdvanceChapter = async (id) => {
    try {
      await api(`/api/reading/advance/${id}`, { method: 'POST' });
      loadSchedules();
      loadDailyReading();
    } catch (e) { throw e; }
  };

  const handleAddToCart = async (bookId, title) => {
    try {
      await api(`/api/store/cart/add?book_id=${bookId}&quantity=1&user_id=${USER_ID}`, { method: 'POST' });
      loadCart();
      return true;
    } catch (e) { throw e; }
  };

  const handleRemoveFromCart = async (itemId) => {
    try {
      await api(`/api/store/cart/${itemId}?user_id=${USER_ID}`, { method: 'DELETE' });
      loadCart();
    } catch (e) { throw e; }
  };

  const handleSendNotification = async () => {
    try {
      return await api(`/api/reading/send-notification?user_id=${USER_ID}`, { method: 'POST' });
    } catch (e) { throw e; }
  };

  const changeCurrency = (currency) => {
    setSelectedCurrency(currency);
    setTimeout(() => loadCart(), 100);
  };

  const value = {
    page, setPage,
    books, setBooks, catalog, setCatalog,
    categories, dailyReading, schedules,
    user, cart, media, podcasts, playlists,
    orders, shippingZones, currencies, countries, cricfyMatches,
    selectedCurrency, changeCurrency,
    dashboard, loading,
    USER_ID,
    loadCatalog, loadCategories, loadDailyReading,
    loadSchedules, loadCart, loadMedia, loadPodcasts,
    loadPlaylists, loadCricfyMatches, loadOrders, loadDashboard,
    handleScheduleBook, handleAdvanceChapter,
    handleAddToCart, handleRemoveFromCart,
    handleSendNotification,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
