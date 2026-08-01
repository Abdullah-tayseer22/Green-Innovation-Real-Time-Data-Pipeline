import React from 'react';
import { Icon } from '../components/Icons';

const FeatureCard = ({ icon, title, children }) => (
  <article className="home-feature-card">
    <span className="home-feature-card__icon"><Icon name={icon} size={28} /></span>
    <h3>{title}</h3>
    <p>{children}</p>
  </article>
);

export default function HomePage({ onNavigate, onOpenAuth }) {
  return (
    <div className="home-page">
      <section className="home-hero">
        <header className="home-header">
          <button className="home-brand" type="button" onClick={() => onNavigate('home')}>
            <img src="/green-innovation-logo.svg" alt="Green Innovation logo" />
            <span>Green Innovation</span>
          </button>
          <nav aria-label="Public navigation">
            <button className="is-active" type="button" onClick={() => onNavigate('home')}>Home</button>
            <button type="button" onClick={() => onOpenAuth('login')}>Login</button>
            <button className="home-header__account" type="button" onClick={() => onOpenAuth('register')}>Create Account</button>
          </nav>
        </header>

        <div className="home-hero__content">
          <div className="home-hero__copy">
            <span className="home-kicker">Real-time agricultural decision support</span>
            <h1>Smarter Agricultural Decisions, Powered by Real-Time Data</h1>
            <p>Turn real-time weather and location data into clear agricultural insights. Analyze a selected location, understand current risk conditions, and receive practical recommendations that support better farming decisions.</p>
            <div className="home-hero__actions">
              <button className="home-button home-button--primary" type="button" onClick={() => onNavigate('location')}>Analyze Your Location</button>
              <button className="home-button home-button--outline" type="button" onClick={() => onOpenAuth('register')}>Create Account</button>
            </div>
          </div>

          <div className="home-flow" aria-label="How Green Innovation processes agricultural data">
            <div className="home-flow__card home-flow__card--glass">
              <span className="home-flow__icon"><Icon name="location" size={23} /></span>
              <div><small>Input</small><strong>Location Coordinates</strong><code>30.0444° N, 31.2357° E</code></div>
            </div>
            <span className="home-flow__line" />
            <div className="home-flow__weather home-flow__card--glass">
              <small>Real-Time Weather Data</small>
              <div className="home-weather-grid"><span>Temperature<strong>24°C</strong></span><span>Humidity<strong>62%</strong></span><span>Wind<strong>12 km/h</strong></span><span>Rainfall<strong>0.2 mm</strong></span></div>
            </div>
            <span className="home-flow__line" />
            <div className="home-flow__card home-flow__card--glass">
              <span className="home-flow__icon"><Icon name="analyze" size={23} /></span>
              <div><small>Processing</small><strong>Location Risk Analysis</strong></div>
              <em><i /> Live</em>
            </div>
            <span className="home-flow__line" />
            <div className="home-flow__result">
              <span><Icon name="recommendations" size={22} /></span>
              <div><small>Output</small><strong>Agricultural Recommendation</strong><p>Monitor current field conditions and follow the recommended action for the detected risk level.</p></div>
            </div>
          </div>
        </div>
      </section>

      <main className="home-main">
        <section className="home-section">
          <div className="home-section__heading"><span>How it works</span><h2>From Real-Time Data to Agricultural Recommendations</h2><p>A direct workflow from a selected location to a clear, practical action.</p></div>
          <div className="home-steps">
            <FeatureCard icon="location" title="1. Select a Location">Enter the latitude and longitude of the agricultural location you want to analyze.</FeatureCard>
            <FeatureCard icon="analyze" title="2. Analyze Current Conditions">The system retrieves available weather data and evaluates conditions associated with the selected location.</FeatureCard>
            <FeatureCard icon="recommendations" title="3. Receive a Recommendation">The analysis is transformed into a practical recommendation with clear risk and action information.</FeatureCard>
          </div>
        </section>

        <section className="home-section home-section--screens">
          <div className="home-section__heading"><span>Inside the platform</span><h2>Explore Green Innovation</h2><p>Every screen supports the same weather-to-recommendation workflow.</p></div>
          <div className="home-steps">
            <FeatureCard icon="overview" title="Overview">Review main system metrics, risk distribution, and high-priority recommendations in one clear view.</FeatureCard>
            <FeatureCard icon="location" title="Analyze Location">Enter coordinates, preview the selected point on the map, and request a weather-based agricultural analysis.</FeatureCard>
            <FeatureCard icon="recommendations" title="Recommendations">Search, review, and open the agricultural recommendations generated from available data.</FeatureCard>
          </div>
        </section>

        <section className="home-cta">
          <div><span>Ready to begin?</span><h2>Turn Weather Data into Clear Agricultural Action</h2><p>Choose a location, analyze its current conditions, and receive a practical recommendation through Green Innovation.</p></div>
          <button className="home-button home-button--primary" type="button" onClick={() => onNavigate('location')}>Start Location Analysis</button>
        </section>
      </main>

      <footer className="home-footer">
        <div className="home-footer__brand"><img src="/green-innovation-logo.svg" alt="" /><div><strong>Green Innovation</strong><p>A real-time agricultural decision-support platform that transforms weather and location data into practical recommendations.</p></div></div>
        <nav><button onClick={() => onNavigate('home')} type="button">Home</button><button onClick={() => onOpenAuth('login')} type="button">Login</button><button onClick={() => onOpenAuth('register')} type="button">Create Account</button></nav>
        <small>© 2026 Green Innovation. All rights reserved.</small>
      </footer>
    </div>
  );
}
