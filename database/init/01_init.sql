-- Initialize Kenya Climate Database

-- Weather data table
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    date DATE NOT NULL,
    temperature_max DECIMAL(5, 2),
    temperature_min DECIMAL(5, 2),
    temperature_mean DECIMAL(5, 2),
    precipitation DECIMAL(6, 2),
    humidity DECIMAL(5, 2),
    wind_speed DECIMAL(5, 2),
    pressure DECIMAL(8, 2),
    cloud_cover DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(location, date)
);

-- ENSO data table
CREATE TABLE IF NOT EXISTS enso_data (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    oni_value DECIMAL(4, 2) NOT NULL,
    enso_phase VARCHAR(20) NOT NULL,
    sst_anomaly DECIMAL(5, 2),
    soi_value DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(year, month)
);

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    prediction_date DATE NOT NULL,
    predicted_value DECIMAL(8, 2),
    confidence_score DECIMAL(4, 2),
    enso_phase VARCHAR(20),
    model_version VARCHAR(20),
    actual_value DECIMAL(8, 2),
    accuracy DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Climate alerts table
CREATE TABLE IF NOT EXISTS climate_alerts (
    id SERIAL PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alert subscriptions table - FIXED
CREATE TABLE IF NOT EXISTS alert_subscriptions (
    id SERIAL PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    alert_types TEXT[] NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Search logs table
CREATE TABLE IF NOT EXISTS search_logs (
    id SERIAL PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    search_query VARCHAR(200),
    user_ip VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);

-- API logs table
CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time_ms DECIMAL(8, 2),
    user_ip VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Model performance table
CREATE TABLE IF NOT EXISTS model_performance (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(8, 4) NOT NULL,
    training_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_weather_location_date ON weather_data(location, date);
CREATE INDEX IF NOT EXISTS idx_enso_year_month ON enso_data(year, month);
CREATE INDEX IF NOT EXISTS idx_predictions_location ON predictions(location, prediction_type);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_location ON climate_alerts(location, is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_active ON climate_alerts(is_active, expires_at);
CREATE INDEX IF NOT EXISTS idx_api_logs_created ON api_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_search_logs_location ON search_logs(location);
CREATE INDEX IF NOT EXISTS idx_search_logs_created ON search_logs(created_at);

-- Insert sample ENSO data (historical)
INSERT INTO enso_data (year, month, oni_value, enso_phase, sst_anomaly, soi_value) VALUES
(2023, 1, -0.8, 'La Nina', -0.9, 1.2),
(2023, 2, -0.7, 'La Nina', -0.8, 1.0),
(2023, 3, -0.5, 'La Nina', -0.6, 0.8),
(2023, 4, -0.3, 'Neutral', -0.4, 0.5),
(2023, 5, 0.1, 'Neutral', 0.0, -0.1),
(2023, 6, 0.4, 'Neutral', 0.3, -0.4),
(2023, 7, 0.7, 'El Nino', 0.8, -0.8),
(2023, 8, 1.2, 'El Nino', 1.3, -1.2),
(2023, 9, 1.5, 'El Nino', 1.6, -1.5),
(2023, 10, 1.8, 'El Nino', 1.9, -1.8),
(2023, 11, 2.0, 'El Nino', 2.1, -2.0),
(2023, 12, 1.9, 'El Nino', 2.0, -1.9),
(2024, 1, 1.5, 'El Nino', 1.6, -1.5),
(2024, 2, 1.0, 'El Nino', 1.1, -1.0),
(2024, 3, 0.5, 'El Nino', 0.6, -0.5),
(2024, 4, 0.1, 'Neutral', 0.0, -0.1),
(2024, 5, -0.3, 'Neutral', -0.4, 0.3),
(2024, 6, -0.6, 'La Nina', -0.7, 0.6),
(2024, 7, -0.8, 'La Nina', -0.9, 0.8),
(2024, 8, -0.9, 'La Nina', -1.0, 0.9),
(2024, 9, -1.0, 'La Nina', -1.1, 1.0),
(2024, 10, -0.9, 'La Nina', -1.0, 0.9),
(2024, 11, -0.7, 'La Nina', -0.8, 0.7),
(2024, 12, -0.5, 'La Nina', -0.6, 0.5)
ON CONFLICT (year, month) DO NOTHING;

-- Insert sample weather data for Nairobi
INSERT INTO weather_data (location, latitude, longitude, date, temperature_max, temperature_min, precipitation, humidity, wind_speed, pressure) VALUES
('Nairobi', -1.2921, 36.8219, '2024-01-01', 28.5, 14.2, 45.2, 65, 12, 1015),
('Nairobi', -1.2921, 36.8219, '2024-01-02', 29.1, 14.8, 12.5, 62, 14, 1014),
('Nairobi', -1.2921, 36.8219, '2024-01-03', 27.8, 13.9, 0.0, 68, 10, 1016),
('Nairobi', -1.2921, 36.8219, '2024-01-04', 28.2, 14.1, 8.3, 70, 11, 1015),
('Nairobi', -1.2921, 36.8219, '2024-01-05', 29.5, 15.0, 0.0, 60, 11, 1013)
ON CONFLICT (location, date) DO NOTHING;

-- Insert sample predictions
INSERT INTO predictions (location, prediction_type, prediction_date, predicted_value, confidence_score, enso_phase, model_version) VALUES
('Nairobi', 'rainfall', '2024-06-01', 150.5, 0.72, 'La Nina', '1.0.0'),
('Nairobi', 'drought', '2024-06-01', 0.65, 0.68, 'La Nina', '1.0.0'),
('Nairobi', 'temperature', '2024-06-01', 22.5, 0.75, 'La Nina', '1.0.0'),
('Mombasa', 'rainfall', '2024-06-01', 200.3, 0.70, 'La Nina', '1.0.0'),
('Kisumu', 'rainfall', '2024-06-01', 180.7, 0.74, 'La Nina', '1.0.0')
ON CONFLICT DO NOTHING;

-- Insert sample alerts
INSERT INTO climate_alerts (location, alert_type, severity, title, description, start_date, end_date, is_active) VALUES
('Nairobi', 'drought', 'medium', 'Drought Warning - Nairobi', 
 'Below-normal rainfall expected due to La Nina conditions. Water conservation advised.', 
 '2024-06-01', '2024-08-31', true),
('Mombasa', 'flood', 'high', 'Flood Alert - Mombasa', 
 'Heavy rainfall expected during OND season. Coastal flooding risk elevated.', 
 '2024-10-01', '2024-12-31', true),
('Turkana', 'drought', 'critical', 'Severe Drought Alert - Turkana', 
 'Critical drought conditions expected. Emergency water and food aid required.', 
 '2024-05-01', '2024-09-30', true)
ON CONFLICT DO NOTHING;

-- Insert sample model performance
INSERT INTO model_performance (model_name, model_version, metric_name, metric_value, training_date) VALUES
('rainfall', '1.0.0', 'r2_score', 0.8234, '2024-05-25'),
('drought', '1.0.0', 'accuracy', 0.8912, '2024-05-25'),
('flood', '1.0.0', 'accuracy', 0.8567, '2024-05-25'),
('temperature', '1.0.0', 'r2_score', 0.7856, '2024-05-25')
ON CONFLICT DO NOTHING;
