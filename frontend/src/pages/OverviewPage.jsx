import React from 'react';
import SummaryCard from '../components/SummaryCard';
import RiskDistribution from '../components/RiskDistribution';
import HighPriorityList from '../components/HighPriorityList';
import { normalizeRisk } from '../utils/recommendations';

export default function OverviewPage({ metrics, loading, error, onRetry, onOpenRecord, onNavigateRecommendations }) {
  if (loading) return <OverviewSkeleton />;
  if (error) return <StateCard title="The recommendation service is currently unavailable." message={error} actionLabel="Retry" onAction={onRetry} />;
  if (!metrics.total) return <StateCard title="No recommendations are currently available." message="Refresh the dashboard after the pipeline generates recommendation records." actionLabel="Refresh" onAction={onRetry} />;

  const highestRisk = normalizeRisk(metrics.highestRisk);
  return (
    <main className="page-shell">
      <div className="page-intro"><div><span className="eyebrow">Real-time agricultural intelligence</span><h1>Executive Overview</h1><p>Current risk and anomaly summary for the recommendations loaded from the service.</p></div></div>
      <section className="summary-grid" aria-label="Recommendation summary">
        <SummaryCard label="Total recommendations" value={metrics.total.toLocaleString()} note="Currently loaded records" icon="records" />
        <SummaryCard label="Anomalies detected" value={metrics.anomalies.toLocaleString()} note={metrics.anomalies ? 'Review flagged records' : 'No anomalies in this set'} icon="anomaly" tone={metrics.anomalies ? 'critical' : 'default'} />
        <SummaryCard label="Highest current risk" value={highestRisk.toUpperCase()} note="Across loaded records" icon="risk" tone={highestRisk} />
        <SummaryCard label="Cities represented" value={metrics.cities.toLocaleString()} note="Unique cities in this set" icon="city" />
      </section>
      <RiskDistribution distribution={metrics.distribution} total={metrics.total} />
      <HighPriorityList records={metrics.highPriority} onOpen={onOpenRecord} onViewAll={onNavigateRecommendations} />
    </main>
  );
}

function StateCard({ title, message, actionLabel, onAction }) {
  return <main className="page-shell"><div className="state-card"><span className="state-card__icon">!</span><h1>{title}</h1><p>{message}</p><button type="button" className="primary-button" onClick={onAction}>{actionLabel}</button></div></main>;
}

function OverviewSkeleton() {
  return <main className="page-shell" aria-busy="true" aria-label="Loading dashboard"><div className="skeleton skeleton--title"/><section className="summary-grid">{Array.from({ length: 4 }).map((_, index) => <div className="summary-card" key={index}><div className="skeleton skeleton--line"/><div className="skeleton skeleton--value"/><div className="skeleton skeleton--line short"/></div>)}</section><div className="panel skeleton-panel"><div className="skeleton skeleton--line"/><div className="skeleton skeleton--bar"/></div></main>;
}
