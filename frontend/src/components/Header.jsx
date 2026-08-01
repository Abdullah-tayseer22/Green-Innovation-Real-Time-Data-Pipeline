import React from 'react';
import { Icon } from './Icons';
export default function Header({ apiOnline, loading, user, onLogout }) {
  const label = loading ? 'Checking' : apiOnline ? 'Live' : 'Offline';
  return <header className="topbar"><div className="brand"><img className="brand__logo" src="/green-innovation-logo.svg" alt=""/><span className="brand__name">Green Innovation</span></div><div className="topbar__right"><div className="service-status" aria-live="polite"><span className={`service-status__dot ${apiOnline ? 'is-online' : 'is-offline'} ${loading ? 'is-checking' : ''}`}/><span>{label}</span><Icon name="live" size={22}/></div>{user && <div className="user-menu"><span>{user.full_name}</span><button type="button" onClick={onLogout}>Logout</button></div>}</div></header>;
}
