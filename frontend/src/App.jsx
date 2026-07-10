import React, { useCallback, useEffect, useMemo, useState } from 'react';
import Header from './components/Header';
import BottomNav from './components/BottomNav';
import RecommendationDrawer from './components/RecommendationDrawer';
import OverviewPage from './pages/OverviewPage';
import RecommendationsPage from './pages/RecommendationsPage';
import LocationAnalysisPage from './pages/LocationAnalysisPage';
import { analyzeLocation, getHealth, getRecommendations } from './services/api';
import { getOverviewMetrics } from './utils/recommendations';

export default function App() {
  const [activeView, setActiveView] = useState('overview');
  const [records, setRecords] = useState([]);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [locationResult, setLocationResult] = useState(null);
  const [city, setCity] = useState('');
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(true);
  const [healthLoading, setHealthLoading] = useState(true);
  const [apiOnline, setApiOnline] = useState(false);
  const [error, setError] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState('');

  const loadHealth = useCallback(async () => { setHealthLoading(true); try { await getHealth(); setApiOnline(true); } catch { setApiOnline(false); } finally { setHealthLoading(false); } }, []);
  const loadRecords = useCallback(async (nextCity = city, nextLimit = limit) => { setLoading(true); setError(''); try { const data = await getRecommendations({ city: nextCity, limit: nextLimit }); setRecords(Array.isArray(data) ? data : []); setApiOnline(true); } catch (requestError) { setRecords([]); setError(requestError.message || 'Unable to load recommendations.'); if (!requestError.status || requestError.status >= 500) setApiOnline(false); } finally { setLoading(false); } }, [city, limit]);
  useEffect(() => { loadHealth(); loadRecords('', 50); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleAnalyze = async (coordinates) => {
    setAnalyzing(true); setAnalysisError('');
    try {
      const data = await analyzeLocation(coordinates);
      setLocationResult(data); setSelectedRecord(data); setApiOnline(true);
      setRecords((current) => [data, ...current.filter((item) => item.weather_id !== data.weather_id)]);
    } catch (requestError) { setAnalysisError(requestError.message || 'Unable to analyze this location.'); if (!requestError.status || requestError.status >= 500) setApiOnline(false); }
    finally { setAnalyzing(false); }
  };

  const metrics = useMemo(() => getOverviewMetrics(records), [records]);
  const handleSearch = (nextCity) => { setCity(nextCity); loadRecords(nextCity, limit); };
  const handleLimitChange = (nextLimit) => { setLimit(nextLimit); loadRecords(city, nextLimit); };

  return <div className="app-shell"><Header apiOnline={apiOnline} loading={healthLoading}/>{activeView === 'overview' ? <OverviewPage metrics={metrics} loading={loading} error={error} onRetry={() => { loadHealth(); loadRecords(); }} onOpenRecord={setSelectedRecord} onNavigateRecommendations={() => setActiveView('recommendations')}/> : activeView === 'location' ? <LocationAnalysisPage onAnalyze={handleAnalyze} analyzing={analyzing} analysisError={analysisError} result={locationResult} onOpenResult={setSelectedRecord}/> : <RecommendationsPage records={records} loading={loading} error={error} city={city} limit={limit} onSearch={handleSearch} onLimitChange={handleLimitChange} onRefresh={() => loadRecords()} onOpenRecord={setSelectedRecord}/>}<BottomNav activeView={activeView} onNavigate={setActiveView}/><RecommendationDrawer record={selectedRecord} onClose={() => setSelectedRecord(null)}/></div>;
}
