import React from 'react';
import { normalizeRisk } from '../utils/recommendations';

export function RiskBadge({ risk }) {
  const normalized = normalizeRisk(risk);
  return <span className={`badge badge--${normalized}`}>{normalized}</span>;
}

export function AnomalyBadge({ active }) {
  return (
    <span className={`badge ${active ? 'badge--critical' : 'badge--neutral'}`}>
      {active ? 'Anomaly detected' : 'No anomaly'}
    </span>
  );
}
