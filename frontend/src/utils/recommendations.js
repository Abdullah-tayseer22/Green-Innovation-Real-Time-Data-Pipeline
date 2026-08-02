export const RISK_ORDER = ['normal', 'low', 'medium', 'high', 'critical'];

export function normalizeRisk(value) {
  const normalized = String(value || 'normal').trim().toLowerCase();
  return RISK_ORDER.includes(normalized) ? normalized : 'normal';
}

export function getOverviewMetrics(records) {
  const safeRecords = Array.isArray(records) ? records : [];
  const cities = new Set();
  const distribution = { normal: 0, medium: 0, high: 0, critical: 0 };
  let anomalyCount = 0;
  let highestRisk = 'normal';

  safeRecords.forEach((record) => {
    const risk = normalizeRisk(record.risk_level);
    if (risk === 'low') distribution.normal += 1;
    else distribution[risk] += 1;
    if (Boolean(record.is_anomaly)) anomalyCount += 1;
    if (record.city) cities.add(String(record.city).trim().toLowerCase());
    if (RISK_ORDER.indexOf(risk) > RISK_ORDER.indexOf(highestRisk)) highestRisk = risk;
  });

  return {
    total: safeRecords.length,
    anomalies: anomalyCount,
    highestRisk,
    cities: cities.size,
    distribution,
    highPriority: safeRecords.filter((record) => {
      const risk = normalizeRisk(record.risk_level);
      return risk === 'high' || risk === 'critical';
    }),
  };
}

export function formatDateTime(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

export function formatRelativeTime(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  const seconds = Math.round((date.getTime() - Date.now()) / 1000);
  const abs = Math.abs(seconds);
  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' });
  if (abs < 60) return formatter.format(seconds, 'second');
  if (abs < 3600) return formatter.format(Math.round(seconds / 60), 'minute');
  if (abs < 86400) return formatter.format(Math.round(seconds / 3600), 'hour');
  return formatter.format(Math.round(seconds / 86400), 'day');
}

export function formatScore(value) {
  if (value === '' || value === null || value === undefined) return '—';
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(4) : '—';
}
