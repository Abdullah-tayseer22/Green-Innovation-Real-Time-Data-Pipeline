import React from 'react';
import { Icon } from './Icons';

const items = [
  ['overview', 'overview', 'Overview'],
  ['location', 'location', 'Analyze Location'],
  ['recommendations', 'recommendations', 'Recommendations'],
];

export default function BottomNav({ activeView, onNavigate }) {
  return <nav className="bottom-nav" aria-label="Primary navigation">{items.map(([view, icon, label]) => <button key={view} className={`bottom-nav__item ${activeView === view ? 'is-active' : ''}`} onClick={() => onNavigate(view)} type="button"><Icon name={icon} size={22}/><span>{label}</span></button>)}</nav>;
}
