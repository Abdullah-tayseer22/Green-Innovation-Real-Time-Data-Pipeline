import React from 'react';
import { Icon } from './Icons';

export default function SummaryCard({ label, value, note, icon, tone = 'default' }) {
  return (
    <article className={`summary-card summary-card--${tone}`}>
      <div className="summary-card__top">
        <span className="summary-card__label">{label}</span>
        <Icon name={icon} size={27} className="summary-card__icon" />
      </div>
      <div>
        <div className="summary-card__value">{value}</div>
        <div className="summary-card__note">{note}</div>
      </div>
    </article>
  );
}
