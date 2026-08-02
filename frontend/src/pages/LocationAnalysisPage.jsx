import React, { useMemo, useState } from 'react';
import FarmMap from '../components/FarmMap';
import { Icon } from '../components/Icons';
import { AnomalyBadge, RiskBadge } from '../components/StatusBadge';
import { formatDateTime, formatScore } from '../utils/recommendations';

const DEFAULT_LAT = '28.0871';
const DEFAULT_LON = '30.7618';

export default function LocationAnalysisPage({ onAnalyze, analyzing, analysisError, result, onOpenResult }) {
  const [latitude, setLatitude] = useState(result?.latitude ?? DEFAULT_LAT);
  const [longitude, setLongitude] = useState(result?.longitude ?? DEFAULT_LON);
  const [gpsError, setGpsError] = useState('');
  const [locating, setLocating] = useState(false);

  const coordinatesValid = useMemo(() => {
    const lat = Number(latitude); const lon = Number(longitude);
    return Number.isFinite(lat) && Number.isFinite(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
  }, [latitude, longitude]);

  const useGps = () => {
    setGpsError('');
    if (!navigator.geolocation) { setGpsError('Location services are not supported by this browser.'); return; }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => { setLatitude(coords.latitude.toFixed(6)); setLongitude(coords.longitude.toFixed(6)); setLocating(false); },
      (error) => { setGpsError(error.code === 1 ? 'Location permission was denied. You can enter the coordinates manually.' : 'Your location could not be detected.'); setLocating(false); },
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 },
    );
  };

  const submit = (event) => {
    event.preventDefault();
    if (coordinatesValid) onAnalyze({ latitude: Number(latitude), longitude: Number(longitude) });
  };

  const activeLat = result?.latitude ?? latitude;
  const activeLon = result?.longitude ?? longitude;

  return (
    <main className="page-shell location-page">
      <div className="page-intro location-intro"><div><span className="eyebrow">Farm location intelligence</span><h1>Analyze a Farm Location</h1><p>Choose the farm coordinates, retrieve its current weather, and generate irrigation, spraying, and risk guidance.</p></div></div>
      <div className="location-layout">
        <section className="panel location-control-card">
          <div className="technical-heading"><span>01</span><div><h2>Farm coordinates</h2><p>Use the device GPS or enter latitude and longitude manually.</p></div></div>
          <form onSubmit={submit} className="coordinate-form">
            <div className="coordinate-grid">
              <label><span>Latitude</span><input type="number" step="any" min="-90" max="90" value={latitude} onChange={(e) => setLatitude(e.target.value)} required /></label>
              <label><span>Longitude</span><input type="number" step="any" min="-180" max="180" value={longitude} onChange={(e) => setLongitude(e.target.value)} required /></label>
            </div>
            <button type="button" className="secondary-button gps-button" onClick={useGps} disabled={locating}><Icon name="location" size={18}/>{locating ? 'Detecting location…' : 'Use my current location'}</button>
            {gpsError ? <p className="form-message form-message--error">{gpsError}</p> : null}
            {!coordinatesValid ? <p className="form-message form-message--error">Enter latitude from −90 to 90 and longitude from −180 to 180.</p> : null}
            <button type="submit" className="agri-button" disabled={!coordinatesValid || analyzing}><Icon name="analyze" size={18}/>{analyzing ? 'Analyzing current weather…' : 'Analyze this location'}</button>
          </form>
          <div className="process-steps" aria-label="Analysis process">
            <span>Coordinates</span><i/><span>Live weather</span><i/><span>Recommendation</span>
          </div>
          {analysisError ? <div className="analysis-error"><strong>Analysis could not be completed.</strong><p>{analysisError}</p></div> : null}
        </section>
        <section className="panel location-map-card">
          <div className="technical-heading"><span>02</span><div><h2>Location preview</h2><p>The marker changes color after analysis to represent the generated risk level.</p></div></div>
          <FarmMap latitude={activeLat} longitude={activeLon} riskLevel={result?.risk_level || 'normal'} height={430}/>
          <div className="coordinate-readout"><span>LAT <strong>{Number(activeLat).toFixed(6)}</strong></span><span>LON <strong>{Number(activeLon).toFixed(6)}</strong></span></div>
        </section>
      </div>
      {result ? (
        <section className="panel analysis-result-card">
          <div className="analysis-result-card__header"><div><span className="eyebrow">Generated recommendation</span><h2>{result.city || 'Selected farm location'}</h2></div><div className="result-statuses"><RiskBadge risk={result.risk_level}/><AnomalyBadge active={Boolean(result.is_anomaly)}/></div></div>
          <div className="result-metrics"><div><span>Anomaly score</span><strong>{formatScore(result.anomaly_score)}</strong></div><div><span>Weather record</span><strong>#{result.weather_id ?? '—'}</strong></div><div><span>Generated</span><strong>{formatDateTime(result.generated_at)}</strong></div></div>
          <div className="recommendation-highlight"><Icon name="leaf" size={24}/><p>{result.recommendation}</p></div>
          <div className="action-guidance-grid"><article><span>Irrigation guidance</span><p>{result.irrigation_action}</p></article><article><span>Spraying guidance</span><p>{result.spraying_action}</p></article></div>
          <button type="button" className="primary-button" onClick={() => onOpenResult(result)}>Open full technical details</button>
        </section>
      ) : null}
    </main>
  );
}
