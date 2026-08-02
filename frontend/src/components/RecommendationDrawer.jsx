import React, { useEffect } from 'react';
import { Icon } from './Icons';
import { AnomalyBadge, RiskBadge } from './StatusBadge';
import { formatDateTime, formatScore } from '../utils/recommendations';
import FarmMap from './FarmMap';

function Field({ label, children, wide = false }) {
  return <div className={`detail-field ${wide ? 'detail-field--wide' : ''}`}><dt>{label}</dt><dd>{children || '—'}</dd></div>;
}

export default function RecommendationDrawer({ record, onClose }) {
  useEffect(() => {
    if (!record) return undefined;
    const onKeyDown = (event) => { if (event.key === 'Escape') onClose(); };
    document.addEventListener('keydown', onKeyDown);
    document.body.classList.add('drawer-open');
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.body.classList.remove('drawer-open');
    };
  }, [record, onClose]);

  if (!record) return null;
  return (
    <div className="drawer-backdrop" onMouseDown={onClose} role="presentation">
      <aside className="drawer" role="dialog" aria-modal="true" aria-labelledby="drawer-title" onMouseDown={(event) => event.stopPropagation()}>
        <div className="drawer__header">
          <div><span className="eyebrow">Recommendation details</span><h2 id="drawer-title">{record.city || 'Agricultural recommendation'}</h2></div>
          <button type="button" className="icon-button" onClick={onClose} aria-label="Close details"><Icon name="close" /></button>
        </div>
        <div className="drawer__body">
          <section className="detail-section">
            <h3>Risk assessment</h3>
            <dl className="detail-grid">
              <Field label="Risk level"><RiskBadge risk={record.risk_level} /></Field>
              <Field label="Anomaly status"><AnomalyBadge active={Boolean(record.is_anomaly)} /></Field>
              <Field label="Anomaly score">{formatScore(record.anomaly_score)}</Field>
              <Field label="Weather record ID">{record.weather_id}</Field>
            </dl>
          </section>
          <section className="detail-section">
            <h3>Recommended actions</h3>
            <dl className="detail-grid">
              <Field label="Irrigation action" wide>{record.irrigation_action}</Field>
              <Field label="Spraying action" wide>{record.spraying_action}</Field>
            </dl>
          </section>
          <section className="detail-section">
            <h3>Recommendation summary</h3>
            <p className="recommendation-copy">{record.recommendation || '—'}</p>
          </section>
          {record.latitude !== undefined && record.longitude !== undefined ? (
            <section className="detail-section">
              <h3>Farm location</h3>
              <FarmMap latitude={record.latitude} longitude={record.longitude} riskLevel={record.risk_level} height={280} />
            </section>
          ) : null}
          <section className="detail-section">
            <h3>Timing</h3>
            <dl className="detail-grid">
              <Field label="Source timestamp">{formatDateTime(record.source_timestamp)}</Field>
              <Field label="Generated at">{formatDateTime(record.generated_at)}</Field>
            </dl>
          </section>
        </div>
      </aside>
    </div>
  );
}
