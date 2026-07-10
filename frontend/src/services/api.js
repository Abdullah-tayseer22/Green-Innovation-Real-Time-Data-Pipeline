const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        Accept: 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      let message = 'The recommendation service could not complete the request.';
      try {
        const body = await response.json();
        if (body?.detail) message = body.detail;
      } catch {
        // Keep the safe fallback message.
      }
      const error = new Error(message);
      error.status = response.status;
      throw error;
    }

    return response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('The recommendation service took too long to respond.');
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export function getHealth() {
  return request('/api/v1/health');
}

export function getRecommendations({ city = '', limit = 50 } = {}) {
  const safeLimit = Math.min(Math.max(Number(limit) || 50, 1), city ? 100 : 500);
  const encodedCity = encodeURIComponent(city.trim());
  const path = encodedCity
    ? `/api/v1/recommendations/${encodedCity}?limit=${safeLimit}`
    : `/api/v1/recommendations?limit=${safeLimit}`;
  return request(path);
}


export function analyzeLocation({ latitude, longitude }) {
  return request('/api/v1/analyze-location', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latitude, longitude }),
  });
}
