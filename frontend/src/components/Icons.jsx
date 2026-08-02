import React from 'react';

export function Icon({ name, size = 24, className = '', title }) {
  const paths = {
    brand: <><path d="M4 13h3l2-5h5l2 5h4"/><circle cx="7" cy="17" r="3"/><circle cx="18" cy="17" r="3"/><path d="M9 8V5h4"/></>,
    live: <><path d="M5 9a10 10 0 0 0 0 6"/><path d="M19 9a10 10 0 0 1 0 6"/><path d="M8 11a5 5 0 0 0 0 2"/><path d="M16 11a5 5 0 0 1 0 2"/><circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"/></>,
    records: <><path d="M5 4h14v16H5z"/><path d="M8 8h8M8 12h8M8 16h5"/></>,
    anomaly: <><path d="M12 3 2.8 20h18.4L12 3Z"/><path d="M12 9v4M12 17h.01"/></>,
    risk: <><path d="M4 17 10 11l4 4 6-8"/><path d="M15 7h5v5"/></>,
    city: <><path d="M4 20V8h6v12M10 20V4h7v16M17 20v-9h3v9"/><path d="M7 11h.01M7 15h.01M13 8h.01M13 12h.01M13 16h.01"/></>,
    home: <><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10v10h13V10"/><path d="M9.5 20v-6h5v6"/></>,
    overview: <><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></>,
    recommendations: <><path d="M5 20V10M12 20V4M19 20v-7"/><path d="M3 20h18"/></>,
    chevron: <path d="m9 18 6-6-6-6"/>,
    refresh: <><path d="M20 11a8 8 0 1 0 1 5"/><path d="M20 4v7h-7"/></>,
    close: <path d="M6 6l12 12M18 6 6 18"/>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    location: <><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></>,
    analyze: <><path d="M4 19h16"/><path d="M6 16l4-5 3 3 5-8"/><circle cx="18" cy="6" r="1.5" fill="currentColor" stroke="none"/></>,
    leaf: <><path d="M20 4C12 4 6 8 6 14c0 4 3 6 6 6 6 0 8-8 8-16Z"/><path d="M5 21c3-7 7-10 13-13"/></>,
  };

  return (
    <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden={title ? undefined : true} role={title ? 'img' : undefined}>
      {title ? <title>{title}</title> : null}
      {paths[name] || paths.records}
    </svg>
  );
}
