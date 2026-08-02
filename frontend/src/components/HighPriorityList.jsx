import React from 'react';
import { Icon } from './Icons';
import { formatRelativeTime, normalizeRisk } from '../utils/recommendations';

export default function HighPriorityList({ records, onOpen, onViewAll }) {
  return (
    <section className="dashboard-section" aria-labelledby="priority-title">
      <div className="section-heading">
        <h2 id="priority-title">High-Priority Recommendations</h2>
        {records.length ? <button type="button" className="text-button" onClick={onViewAll}>View all</button> : null}
      </div>
      {!records.length ? (
        <div className="panel empty-inline">
          <span className="empty-inline__mark">✓</span>
          <div>
            <strong>No high-risk or critical recommendations</strong>
            <p>The currently loaded records do not contain urgent risks.</p>
          </div>
        </div>
      ) : (
        <div className="priority-list">
          {records.slice(0, 3).map((record) => {
            const risk = normalizeRisk(record.risk_level);
            return (
              <button key={`${record.weather_id}-${record.generated_at}`} type="button" className={`priority-card priority-card--${risk}`} onClick={() => onOpen(record)}>
                <span className="priority-card__icon"><Icon name={risk === 'critical' ? 'anomaly' : 'risk'} size={22} /></span>
                <span className="priority-card__content">
                  <span className="priority-card__meta">
                    <span>{risk} risk · {record.city || 'Unknown city'}</span>
                    <time>{formatRelativeTime(record.generated_at)}</time>
                  </span>
                  <strong>{record.recommendation || 'Agricultural recommendation available'}</strong>
                  <span className="priority-card__action">Open details <Icon name="chevron" size={15} /></span>
                </span>
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}
