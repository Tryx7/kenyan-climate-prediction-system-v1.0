# Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Production Deployment](#production-deployment)
6. [Aiven PostgreSQL Setup](#aiven-postgresql-setup)
7. [Vercel Frontend Deployment](#vercel-frontend-deployment)
8. [SSL Configuration](#ssl-configuration)
9. [Monitoring Setup](#monitoring-setup)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- Docker 24.0+ and Docker Compose v2.20+
- Node.js 20+ and npm 10+
- Python 3.11+ and pip
- Git

### Accounts Needed
- [Aiven](https://aiven.io) for PostgreSQL hosting
- [Vercel](https://vercel.com) for frontend deployment
- [Docker Hub](https://hub.docker.com) for image registry (optional)

## Environment Setup

### 1. Clone and Configure
```bash
# Clone repository
git clone https://github.com/your-org/kenyan-climate-prediction-system.git
cd kenyan-climate-prediction-system

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Environment Variables

#### Required Variables
```env
# Database (Aiven PostgreSQL)
AIVEN_PG_HOST=your-project.aivencloud.com
AIVEN_PG_PORT=25060
AIVEN_PG_DATABASE=kenyan_climate_db
AIVEN_PG_USER=avnadmin
AIVEN_PG_PASSWORD=your-secure-password
AIVEN_PG_SSL_MODE=require

# Backend
SECRET_KEY=your-super-secret-key-min-32-chars
JWT_SECRET=your-jwt-secret-key
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# API Keys
NOAA_API_KEY=your-noaa-api-key

# Frontend
NEXT_PUBLIC_API_URL=https://your-api-domain.com

# Grafana
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=strong-password-here

# Nginx
DOMAIN=your-domain.com
NGINX_PORT=80
NGINX_SSL_PORT=443
```

## Local Development

### Start All Services
```bash
# Quick start with Docker
./scripts/deploy.sh

# Or manual Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Individual Services

#### Backend Only
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend Only
```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:3000
```

#### ML Service Only
```bash
cd ml-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
# Or: uvicorn app:app --reload --port 5001
```

## Docker Deployment

### Build and Start
```bash
# Build all images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f ml-service
docker-compose logs -f grafana
```

### Scale Services
```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Update Nginx upstream to match
# Edit nginx/nginx.conf upstream block
```

### Database Initialization
```bash
# Run initialization script
docker-compose exec db psql -U climate_user -d kenyan_climate_db -f /docker-entrypoint-initdb.d/01_init.sql

# Seed sample data
python scripts/seed_data.py
```

## Production Deployment

### Server Requirements
- Ubuntu 22.04 LTS or CentOS 8
- 4 CPU cores
- 8GB RAM minimum (16GB recommended)
- 50GB SSD storage
- Static IP address

### Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    image: your-dockerhub/kenya-climate-backend:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=WARNING

  ml-service:
    image: your-dockerhub/kenya-climate-ml:latest
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
```

### SSL Certificate Setup
```bash
# Using Let's Encrypt
docker run -it --rm \
  -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
  -v "$(pwd)/nginx/www:/var/www/certbot" \
  certbot/certbot certonly \
  --standalone \
  -d your-domain.com \
  -d www.your-domain.com

# Auto-renewal cron job
0 12 * * * docker run -it --rm -v "$(pwd)/nginx/ssl:/etc/letsencrypt" -v "$(pwd)/nginx/www:/var/www/certbot" certbot/certbot renew
```

## Aiven PostgreSQL Setup

### 1. Create Service
1. Log in to [Aiven Console](https://console.aiven.io)
2. Click "Create Service"
3. Select "PostgreSQL"
4. Choose plan (Startup-4 recommended for production)
5. Select cloud region (e.g., AWS Europe)
6. Set service name: `kenya-climate-db`

### 2. Connection Details
```bash
# Download CA certificate from Aiven Console
# Save to: backend/ca.pem

# Connection string format
postgresql://avnadmin:PASSWORD@HOST:PORT/DATABASE?sslmode=require
```

### 3. Update .env
```env
AIVEN_PG_HOST=kenya-climate-db-your-project.aivencloud.com
AIVEN_PG_PORT=25060
AIVEN_PG_DATABASE=defaultdb
AIVEN_PG_USER=avnadmin
AIVEN_PG_PASSWORD=your-password
AIVEN_PG_SSL_MODE=require
```

### 4. Initialize Database
```bash
# Connect to Aiven PostgreSQL
psql "$(cat .env | grep DATABASE_URL | cut -d= -f2-)"

# Run initialization script
\i database/init/01_init.sql
```

## Vercel Frontend Deployment

### 1. Prepare Frontend
```bash
cd frontend

# Ensure next.config.js has output: 'standalone'
# Update NEXT_PUBLIC_API_URL in .env
```

### 2. Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Or connect GitHub repository to Vercel
# Settings -> Git -> Connect Repository
```

### 3. Environment Variables in Vercel
```bash
vercel env add NEXT_PUBLIC_API_URL production
# Enter value: https://your-api-domain.com
```

### 4. Custom Domain
1. Go to Vercel Dashboard -> Project Settings
2. Domains -> Add Domain
3. Follow DNS configuration instructions
4. Wait for SSL certificate provisioning

## SSL Configuration

### Self-Signed Certificate (Development)
```bash
# Generate certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=KE/ST=Nairobi/L=Nairobi/O=ClimatePredict/CN=localhost"
```

### Let's Encrypt (Production)
```bash
# Install certbot
sudo apt-get install certbot

# Obtain certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy to nginx directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem

# Update nginx.conf to use SSL
# Uncomment HTTPS server block
```

## Monitoring Setup

### Grafana Configuration
1. Access Grafana at `http://your-domain.com/grafana`
2. Login with admin credentials
3. Navigate to Dashboards -> Manage
4. Import dashboard from `grafana/dashboards/kenya-climate-dashboard.json`

### Prometheus Metrics (Optional)
```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus:/etc/prometheus
  ports:
    - "9090:9090"
```

### Alerting Rules
```yaml
# prometheus/alerts.yml
groups:
  - name: climate_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(api_requests_total{status="500"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
```

## Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Common fixes
# 1. Database connection failed
#    - Verify DATABASE_URL in .env
#    - Check Aiven connection details
#    - Ensure SSL certificate is downloaded

# 2. Port already in use
#    - Change BACKEND_PORT in .env
#    - Or: sudo lsof -i :8000 && kill -9 PID
```

#### Frontend Build Fails
```bash
# Clear cache
rm -rf frontend/.next frontend/node_modules
rm frontend/package-lock.json

# Reinstall
cd frontend
npm install
npm run build
```

#### ML Model Loading Fails
```bash
# Retrain models
docker-compose exec ml-service python -c "
from services.model_trainer import ModelTrainer
trainer = ModelTrainer()
trainer.train_all_models(force=True)
"

# Or use script
python scripts/retrain_models.py --force
```

#### Database Connection Issues
```bash
# Test connection
psql "$(grep DATABASE_URL .env | cut -d= -f2-)"

# Check SSL
# Download CA certificate from Aiven Console
# Place in backend/ca.pem
```

#### Redis Connection Failed
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Should return: PONG
```

### Performance Tuning

#### Backend
```env
# .env
BACKEND_WORKERS=4
BACKEND_TIMEOUT=60
```

#### Database
```sql
-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_weather_location_date ON weather_data(location, date);
CREATE INDEX CONCURRENTLY idx_predictions_date ON predictions(created_at DESC);
```

#### Nginx
```nginx
# nginx.conf
worker_processes auto;
worker_connections 4096;
```

### Log Locations
```bash
# Docker logs
docker-compose logs -f [service-name]

# Application logs
./logs/app.log
./logs/ml.log

# Nginx logs
docker-compose exec nginx cat /var/log/nginx/access.log
docker-compose exec nginx cat /var/log/nginx/error.log
```

## Backup and Recovery

### Database Backup
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump "$DATABASE_URL" > "backups/kenya_climate_$DATE.sql"
```

### Model Backup
```bash
# Backup trained models
tar -czf "models_backup_$(date +%Y%m%d).tar.gz" ml-service/models/
```

## Security Checklist

- [ ] Change default Grafana password
- [ ] Enable SSL/HTTPS
- [ ] Set strong JWT_SECRET
- [ ] Configure CORS origins properly
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Database encryption at rest
- [ ] Secure API keys in environment variables
- [ ] Enable audit logging

---

For additional support, refer to:
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Next.js Documentation](https://nextjs.org/docs)
- [Grafana Documentation](https://grafana.com/docs)
- [Aiven Documentation](https://docs.aiven.io)
