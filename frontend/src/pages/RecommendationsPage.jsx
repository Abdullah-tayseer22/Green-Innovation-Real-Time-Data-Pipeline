import React, { useMemo, useState } from 'react';
import { Icon } from '../components/Icons';
import { AnomalyBadge, RiskBadge } from '../components/StatusBadge';
import { formatDateTime, formatScore } from '../utils/recommendations';

export default function RecommendationsPage({ records, loading, error, city, limit, onSearch, onLimitChange, onRefresh, onOpenRecord }) {
  const [draftCity, setDraftCity] = useState(city);
  const sorted = useMemo(() => records || [], [records]);
  const submit = (event) => { event.preventDefault(); onSearch(draftCity.trim()); };

  return (
    <main className="page-shell">
      <div className="page-intro"><div><span className="eyebrow">Read-only recommendation feed</span><h1>Agricultural Recommendations</h1><p>Review anomaly results and weather-based irrigation and spraying guidance.</p></div></div>
      <form className="toolbar panel" onSubmit={submit}>
        <label className="search-field"><span className="sr-only">Search by city</span><Icon name="search" size={19}/><input value={draftCity} onChange={(event) => setDraftCity(event.target.value)} placeholder="Search by city"/></label>
        <label className="select-field"><span>Records</span><select value={limit} onChange={(event) => onLimitChange(Number(event.target.value))}><option value="10">10</option><option value="20">20</option><option value="50">50</option><option value="100">100</option></select></label>
        <button type="submit" className="primary-button">Search</button>
        {city ? <button type="button" className="secondary-button" onClick={() => { setDraftCity(''); onSearch(''); }}>Clear</button> : null}
        <button type="button" className="icon-button toolbar__refresh" onClick={onRefresh} aria-label="Refresh recommendations"><Icon name="refresh"/></button>
      </form>
      {loading ? <div className="panel table-state">Loading recommendations…</div> : error ? <div className="panel table-state table-state--error"><strong>Could not load recommendations.</strong><span>{error}</span><button type="button" className="secondary-button" onClick={onRefresh}>Retry</button></div> : !sorted.length ? <div className="panel table-state"><strong>No recommendations are currently available.</strong></div> : (
        <div className="panel table-wrap">
          <table><thead><tr><th>Risk</th><th>City</th><th>Anomaly</th><th>Score</th><th>Recommendation</th><th>Source time</th><th></th></tr></thead><tbody>{sorted.map((record) => <tr key={`${record.weather_id}-${record.generated_at}`}><td><RiskBadge risk={record.risk_level}/></td><td className="cell-strong">{record.city || '—'}</td><td><AnomalyBadge active={Boolean(record.is_anomaly)}/></td><td className="cell-mono">{formatScore(record.anomaly_score)}</td><td className="cell-recommendation">{record.recommendation || '—'}</td><td>{formatDateTime(record.source_timestamp)}</td><td><button className="row-action" type="button" onClick={() => onOpenRecord(record)} aria-label={`View recommendation for ${record.city || 'record'}`}><Icon name="chevron" size={18}/></button></td></tr>)}</tbody></table>
          <div className="mobile-records">{sorted.map((record) => <button type="button" className="mobile-record-card" key={`mobile-${record.weather_id}-${record.generated_at}`} onClick={() => onOpenRecord(record)}><div className="mobile-record-card__top"><RiskBadge risk={record.risk_level}/><span>{record.city || '—'}</span><Icon name="chevron" size={18}/></div><p>{record.recommendation || '—'}</p><div className="mobile-record-card__meta"><AnomalyBadge active={Boolean(record.is_anomaly)}/><span>{formatDateTime(record.source_timestamp)}</span></div></button>)}</div>
        </div>
      )}
    </main>
  );
}
