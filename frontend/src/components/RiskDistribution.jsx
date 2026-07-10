import React from 'react';

const ITEMS = [
  ['normal', 'Normal'],
  ['medium', 'Medium'],
  ['high', 'High'],
  ['critical', 'Critical'],
];

export default function RiskDistribution({ distribution, total }) {
  return (
    <section className="dashboard-section" aria-labelledby="risk-distribution-title">
      <div className="section-heading">
        <h2 id="risk-distribution-title">Risk Distribution</h2>
        <span>Loaded records</span>
      </div>
      <div className="panel risk-panel">
        <div className="risk-bar" aria-label="Risk distribution">
          {ITEMS.map(([key, label]) => {
            const count = distribution[key] || 0;
            const width = total ? (count / total) * 100 : 0;
            return <span key={key} className={`risk-bar__segment risk-bar__segment--${key}`} style={{ width: `${width}%` }} title={`${label}: ${count}`} />;
          })}
          {!total ? <span className="risk-bar__empty" /> : null}
        </div>
        <div className="risk-legend">
          {ITEMS.map(([key, label]) => (
            <div key={key} className="risk-legend__item">
              <span className={`risk-legend__dot risk-legend__dot--${key}`} />
              <span className="risk-legend__label">{label}</span>
              <strong>{distribution[key] || 0}</strong>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
