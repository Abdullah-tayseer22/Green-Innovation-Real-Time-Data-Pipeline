import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Header from './components/Header';
import BottomNav from './components/BottomNav';
import RecommendationDrawer from './components/RecommendationDrawer';
import HomePage from './pages/HomePage';
import AuthPage from './pages/AuthPage';
import OverviewPage from './pages/OverviewPage';
import RecommendationsPage from './pages/RecommendationsPage';
import LocationAnalysisPage from './pages/LocationAnalysisPage';
import { analyzeLocation, clearStoredAuth, getHealth, getRecommendations } from './services/api';
import { getOverviewMetrics } from './utils/recommendations';

export default function App() {
  const [activeView, setActiveView] = useState('home');
  const [user, setUser] = useState(() => { try { return JSON.parse(localStorage.getItem('greenInnovationUser') || 'null'); } catch { return null; } });
  const [pendingView, setPendingView] = useState(null);
  const [authMode, setAuthMode] = useState('login');
  const [records, setRecords] = useState([]);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [locationResult, setLocationResult] = useState(null);
  const [city, setCity] = useState('');
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(false);
  const [healthLoading, setHealthLoading] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);
  const [error, setError] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const [appInitialized, setAppInitialized] = useState(false);

  const loadHealth = useCallback(async () => { setHealthLoading(true); try { await getHealth(); setApiOnline(true); } catch { setApiOnline(false); } finally { setHealthLoading(false); } }, []);
  const loadRecords = useCallback(async (nextCity = city, nextLimit = limit) => { setLoading(true); setError(''); try { const data = await getRecommendations({ city: nextCity, limit: nextLimit }); setRecords(Array.isArray(data) ? data : []); setApiOnline(true); } catch (requestError) { setRecords([]); setError(requestError.message || 'Unable to load recommendations.'); if (!requestError.status || requestError.status >= 500) setApiOnline(false); } finally { setLoading(false); } }, [city, limit]);

  useEffect(() => {
    if (!['overview','location','recommendations'].includes(activeView) || appInitialized) return;
    setAppInitialized(true); loadHealth(); loadRecords('', 50);
  }, [activeView, appInitialized, loadHealth, loadRecords]);

  const navigate = (view) => {
    if (view === 'location' && !user) { setPendingView('location'); setAuthMode('login'); setActiveView('auth'); window.scrollTo({ top: 0, behavior: 'smooth' }); return; }
    setActiveView(view); window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  const openAuth = (mode) => { setAuthMode(mode); navigate('auth'); };
  const handleAuthComplete = (result) => { localStorage.setItem('greenInnovationToken', result.access_token); localStorage.setItem('greenInnovationUser', JSON.stringify(result.user)); setUser(result.user); const destination = pendingView || 'overview'; setPendingView(null); navigate(destination); };
  const logout = () => { clearStoredAuth(); setUser(null); setPendingView(null); setLocationResult(null); navigate('home'); };
  const handleAnalyze = async (coordinates) => { setAnalyzing(true); setAnalysisError(''); try { const data = await analyzeLocation(coordinates); setLocationResult(data); setSelectedRecord(data); setApiOnline(true); setRecords((current) => [data, ...current.filter((item) => item.weather_id !== data.weather_id)]); } catch (requestError) { setAnalysisError(requestError.message || 'Unable to analyze this location.'); if (!requestError.status || requestError.status >= 500) setApiOnline(false); } finally { setAnalyzing(false); } };
  const metrics = useMemo(() => getOverviewMetrics(records), [records]);

  if (activeView === 'home') return <HomePage onNavigate={navigate} onOpenAuth={openAuth}/>;
  if (activeView === 'auth') return <AuthPage initialMode={authMode} onBackHome={() => navigate('home')} onComplete={handleAuthComplete}/>;

  const page = activeView === 'overview'
    ? <OverviewPage metrics={metrics} loading={loading} error={error} onRetry={() => { loadHealth(); loadRecords(); }} onOpenRecord={setSelectedRecord} onNavigateRecommendations={() => navigate('recommendations')}/>
    : activeView === 'location'
      ? <LocationAnalysisPage onAnalyze={handleAnalyze} analyzing={analyzing} analysisError={analysisError} result={locationResult} onOpenResult={setSelectedRecord}/>
      : <RecommendationsPage records={records} loading={loading} error={error} city={city} limit={limit} onSearch={(nextCity) => { setCity(nextCity); loadRecords(nextCity, limit); }} onLimitChange={(nextLimit) => { setLimit(nextLimit); loadRecords(city, nextLimit); }} onRefresh={() => loadRecords()} onOpenRecord={setSelectedRecord}/>;
  return <div className="app-shell"><Header apiOnline={apiOnline} loading={healthLoading} user={user} onLogout={logout}/>{page}<BottomNav activeView={activeView} onNavigate={navigate}/><RecommendationDrawer record={selectedRecord} onClose={() => setSelectedRecord(null)}/></div>;
}
