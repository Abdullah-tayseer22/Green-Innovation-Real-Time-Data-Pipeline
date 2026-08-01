DROP TABLE IF EXISTS weather_data;

CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    temp DOUBLE PRECISION,
    humidity INTEGER,
    pressure INTEGER,
    sea_level INTEGER,
    wind_speed DOUBLE PRECISION,
    clouds INTEGER,
    rain_1h DOUBLE PRECISION,
    weather_description VARCHAR(255),
    timestamp DOUBLE PRECISION,
    weather_status VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS users_email_lower_idx ON users (LOWER(email));
