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