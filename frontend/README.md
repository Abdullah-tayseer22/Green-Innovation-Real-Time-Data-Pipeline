# Green Innovation Frontend

React/Vite frontend for the existing FastAPI recommendation service.

## Run

1. Copy `.env.example` to `.env`.
2. Set `VITE_API_BASE_URL` to the FastAPI URL (default: `http://localhost:8000`).
3. Install and start:

```bash
npm install
npm run dev
```

The interface calls only:

- `GET /api/v1/health`
- `GET /api/v1/recommendations?limit=...`
- `GET /api/v1/recommendations/{city}?limit=...`

All dashboard metrics are calculated from the records currently returned by those endpoints. No trend, field, sensor, crop, satellite, valve, or farm-management data is invented.
