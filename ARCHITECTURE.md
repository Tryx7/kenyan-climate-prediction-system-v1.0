# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Web App    │  │  Mobile App │  │   API Clients│       │
│  │  (Next.js)   │  │   (Future)  │  │   (Scripts)  │       │
│  └──────┬───────┘  └──────┬──────┘  └──────┬───────┘       │
└─────────┼─────────────────┼─────────────────┼─────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │ HTTPS
┌───────────────────────────▼───────────────────────────────┐
│                      GATEWAY LAYER                        │
│                    ┌─────────────┐                        │
│                    │    Nginx    │                        │
│                    │  (Reverse   │                        │
│                    │   Proxy)    │                        │
│                    │  SSL/TLS    │                        │
│                    │ Rate Limit  │                        │
│                    └──────┬──────┘                        │
└───────────────────────────┼───────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
┌─────────▼─────────┐ ┌────▼────┐ ┌───────────▼────────────┐
│   APPLICATION     │ │         │ │     MONITORING         │
│     LAYER         │ │         │ │                        │
│  ┌─────────────┐  │ │         │ │  ┌─────────────────┐   │
│  │   FastAPI   │  │ │  Redis  │ │  │     Grafana     │   │
│  │   Backend   │◀─┼─┤ Cache  │◀─┼──┤   Dashboards    │   │
│  │  (Port 8000)│  │ │         │ │  │   (Port 3001)   │   │
│  └──────┬──────┘  │ └─────────┘ │  └─────────────────┘   │
│         │         │             │                        │
│  ┌──────▼──────┐  │             │  ┌─────────────────┐   │
│  │  ML Service │  │             │  │   Prometheus    │   │
│  │  (Port 5001)│  │             │  │   (Optional)    │   │
│  └─────────────┘  │             │  └─────────────────┘   │
└───────────────────┘             └────────────────────────┘
          │
          │ SQL
┌─────────▼────────────────────────────────────────────────┐
│                    DATA LAYER                             │
│              ┌─────────────────────┐                      │
│              │  Aiven PostgreSQL   │                      │
│              │    (Primary DB)     │                      │
│              │  ┌───────────────┐  │                      │
│              │  │  weather_data │  │                      │
│              │  │   enso_data   │  │                      │
│              │  │  predictions  │  │                      │
│              │  │ climate_alerts│  │                      │
│              │  │     logs      │  │                      │
│              │  └───────────────┘  │                      │
│              └─────────────────────┘                      │
│                                                           │
│              ┌─────────────────────┐                      │
│              │    Redis Cache      │                      │
│              │   (Session/Cache)   │                      │
│              └─────────────────────┘                      │
└───────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Weather Data Collection
```
Open-Meteo API → Backend → PostgreSQL (weather_data table)
                    ↓
                 Redis Cache (10 min TTL)
```

### 2. ENSO Data Update
```
NOAA CPC API → Backend → PostgreSQL (enso_data table)
                  ↓
               Daily at 6:00 AM (APScheduler)
```

### 3. Prediction Request
```
User Request → Nginx → Backend → Redis (check cache)
                                    ↓
                              Cache Miss
                                    ↓
                              ML Service → Prediction
                                    ↓
                              PostgreSQL (predictions table)
                                    ↓
                              Redis Cache (1 hour TTL)
                                    ↓
                              Response to User
```

### 4. Model Retraining
```
APScheduler (Sat 12:00 PM) → ML Service
                                    ↓
                              Load Historical Data
                                    ↓
                              Train Models
                                    ↓
                              Save to Disk (.pkl files)
                                    ↓
                              Log Performance (PostgreSQL)
```

## Component Details

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom climate theme
- **Charts**: Chart.js via react-chartjs-2
- **State**: React hooks + SWR for data fetching
- **Animations**: Framer Motion
- **Deployment**: Vercel with edge caching

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **Database**: AsyncPG for PostgreSQL
- **Cache**: Redis with 1-hour TTL for predictions
- **Scheduler**: APScheduler for background tasks
- **Documentation**: Auto-generated OpenAPI/Swagger
- **Monitoring**: Prometheus metrics endpoint

### ML Service
- **Framework**: FastAPI + Scikit-Learn
- **Models**: 
  - Random Forest (rainfall, drought, flood)
  - Gradient Boosting (temperature)
  - Logistic Regression (flood probability)
- **Features**: 14-dimensional feature vector
- **Training**: Automated weekly retraining
- **Storage**: Joblib serialized models

### Database (PostgreSQL)
- **Provider**: Aiven (cloud-hosted)
- **Tables**: 7 core tables
- **Indexes**: Optimized for location-based queries
- **Backup**: Automated daily snapshots

### Nginx
- **Role**: Reverse proxy + load balancer
- **Features**: 
  - SSL termination
  - Rate limiting (10 req/s)
  - Static file serving
  - Health checks
- **SSL**: Let's Encrypt certificates

### Grafana
- **Dashboards**: 6-panel climate monitoring
- **Data Sources**: PostgreSQL + Prometheus
- **Alerts**: Configurable threshold alerts
- **Access**: Admin authentication

## Scalability Considerations

### Horizontal Scaling
```
                    ┌─────────────┐
                    │    Nginx    │
                    │   (LB)      │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
    │  Backend 1  │ │ Backend 2  │ │ Backend 3  │
    │  (Port 8000)│ │ (Port 8001)│ │ (Port 8002)│
    └─────────────┘ └────────────┘ └────────────┘
```

### Caching Strategy
- **Weather Data**: 10 minutes (changes frequently)
- **Predictions**: 1 hour (computationally expensive)
- **ENSO Status**: 6 hours (slowly changing)
- **Location Data**: 24 hours (static)

### Database Optimization
- **Read Replicas**: For analytics queries
- **Partitioning**: By date for weather_data
- **Indexing**: Composite indexes on (location, date)
- **Connection Pooling**: PgBouncer for high load

## Security Architecture

### Authentication Flow
```
User → Nginx → Backend → JWT Verification → Resource Access
```

### Data Protection
- **Transit**: TLS 1.3 for all communications
- **Rest**: PostgreSQL encryption at rest
- **Keys**: Environment variables only
- **API Keys**: Rotated quarterly

### Network Security
- **Firewall**: UFW/iptables rules
- **Rate Limiting**: Nginx + Redis
- **CORS**: Whitelist only trusted domains
- **DDoS**: Cloudflare (optional)

## Monitoring & Alerting

### Metrics Collected
- API request latency (p50, p95, p99)
- Prediction accuracy over time
- Model performance (R², accuracy)
- Database connection pool usage
- Cache hit/miss ratios
- ENSO phase transitions

### Alert Conditions
- API error rate > 1%
- Prediction accuracy < 70%
- Database connections > 80%
- ML model stale (> 7 days)
- ENSO phase change detected

---

*Architecture Version: 1.0.0*
*Last Updated: 2024-05-26*
