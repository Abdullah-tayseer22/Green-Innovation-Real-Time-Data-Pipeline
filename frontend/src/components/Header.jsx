import React from 'react';
import { Icon } from './Icons';
export default function Header({ apiOnline, loading }) {
  const label = loading ? 'Checking' : apiOnline ? 'Live' : 'Offline';
  return <header className="topbar"><div className="brand"><img className="brand__logo" src="/green-innovation-logo.svg" alt=""/><span className="brand__name">Green Innovation</span></div><div className="service-status" aria-live="polite"><span className={`service-status__dot ${apiOnline ? 'is-online' : 'is-offline'} ${loading ? 'is-checking' : ''}`}/><span>{label}</span><Icon name="live" size={22}/></div></header>;
}
