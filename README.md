# Green Innovation: Real-Time Agricultural Data Pipeline

A comprehensive real-time data pipeline and intelligence framework designed for monitoring, processing, and analyzing agricultural and weather data. The platform empowers farmers and decision-makers with actionable insights, anomaly detection, and automated farming recommendations.

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Usage](#usage)
- [Project Structure](#project-structure)

## Project Overview
This project demonstrates a complete, end-to-end real-time data pipeline. It ingests environmental data, processes it through machine learning models to detect anomalies, and serves the results via a fast API to an interactive frontend dashboard. The system is designed to be highly responsive, providing real-time agricultural intelligence to optimize resource usage and improve crop yield.

## Key Features
- **Executive Overview Dashboard:** Real-time monitoring of current risks, total loaded recommendations, and anomaly summaries across represented cities. Includes visual risk distribution and high-priority alerts.
- **Farm Location Intelligence:** Interactive map allowing users to use device GPS or input specific latitude/longitude coordinates. Generates immediate irrigation, spraying, and risk guidance based on live weather data.
- **Smart Recommendation Engine:** Provides detailed risk assessments (Anomaly Scores and Status) and explicit recommended actions for irrigation and agricultural spraying.
- **Live Agricultural Recommendation Feed:** A comprehensive, searchable read-only feed of all historical and current weather-based guidance records.
- **Efficient Streaming:** Utilizes Apache Kafka for seamless, delay-free data streaming.

## Architecture
1. **Data Ingestion:** Fetching external environmental and weather data (`ingestion` module).
2. **Message Brokering:** Real-time streaming and event management using Apache Kafka & Zookeeper.
3. **Data Processing & ML:** Processing incoming streams and applying machine learning models (Scikit-learn) for anomaly detection and scoring.
4. **Data Storage:** Relational storage of processed data and recommendations in PostgreSQL.
5. **Backend API:** A high-performance FastAPI server serving processed insights to the client.
6. **Frontend UI:** A responsive React-based interface for data visualization and user interaction.

## Tech Stack
### Frontend
- **React.js** (Vite)
- Interactive mapping libraries

### Backend & Data Processing
- **Python**
- **FastAPI** (with Uvicorn)
- **Scikit-learn / Pandas / NumPy** (Machine Learning & Data Processing)

### Infrastructure & Streaming
- **Apache Kafka** & **Zookeeper**
- **Docker** & **Docker Compose** (Containerization)
- **PostgreSQL** (Database)
- **pgAdmin** (Database Management)

## Usage
1. Ensure **Docker Desktop** is running.
2. Spin up the infrastructure (Kafka, Zookeeper, PostgreSQL, pgAdmin) using Docker Compose:
   ```bash
   docker-compose up -d --build