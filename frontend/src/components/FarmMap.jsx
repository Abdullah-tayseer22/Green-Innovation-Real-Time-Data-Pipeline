import React, { useMemo } from 'react';
import { normalizeRisk } from '../utils/recommendations';

const riskHex = {
  normal: '#0bb387',
  low: '#2b82b8',
  medium: '#ffc51b',
  high: '#ff7416',
  critical: '#bc151b',
};

export default function FarmMap({ latitude, longitude, riskLevel = 'normal', height = 360 }) {
  const lat = Number(latitude);
  const lon = Number(longitude);
  const valid = Number.isFinite(lat) && Number.isFinite(lon);
  const risk = normalizeRisk(riskLevel);
  const color = riskHex[risk] || riskHex.normal;

  const src = useMemo(() => {
    if (!valid) return '';
    const delta = 0.035;
    const bbox = [lon - delta, lat - delta, lon + delta, lat + delta].join(',');
    return `https://www.openstreetmap.org/export/embed.html?bbox=${encodeURIComponent(bbox)}&layer=mapnik&marker=${encodeURIComponent(`${lat},${lon}`)}`;
  }, [lat, lon, valid]);

  if (!valid) {
    return <div className="farm-map farm-map--empty" style={{ minHeight: height }}>Enter valid coordinates to preview the farm location.</div>;
  }

  return (
    <div className="farm-map" style={{ minHeight: height }}>
      <iframe title="Selected farm location" src={src} loading="lazy" referrerPolicy="no-referrer-when-downgrade" />
      <div className="farm-map__pin" style={{ '--pin-color': color }} aria-hidden="true"><span /></div>
      <div className="farm-map__legend"><span style={{ background: color }} />{risk} risk</div>
      <a className="farm-map__open" href={`https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}#map=15/${lat}/${lon}`} target="_blank" rel="noreferrer">Open larger map</a>
    </div>
  );
}
