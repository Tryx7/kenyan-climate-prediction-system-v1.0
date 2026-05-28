#!/bin/bash
set -e

echo "================================"
echo "Kenya Climate Prediction System"
echo "Deployment Script"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your settings."
    exit 1
fi

echo -e "${YELLOW}Step 1: Building Docker images...${NC}"
docker-compose build

echo -e "${YELLOW}Step 2: Starting services...${NC}"
docker-compose up -d

echo -e "${YELLOW}Step 3: Waiting for database...${NC}"
sleep 10

echo -e "${YELLOW}Step 4: Running database migrations...${NC}"
docker-compose exec -T db psql -U climate_user -d kenyan_climate_db -f /docker-entrypoint-initdb.d/01_init.sql

echo -e "${YELLOW}Step 5: Training ML models...${NC}"
docker-compose exec -T ml-service python -c "
import asyncio
from services.model_trainer import ModelTrainer
trainer = ModelTrainer()
asyncio.run(trainer.train_all_models())
"

echo -e "${YELLOW}Step 6: Health checks...${NC}"
sleep 5

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
fi

# Check ML service health
if curl -f http://localhost:5001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ ML Service is healthy${NC}"
else
    echo -e "${RED}✗ ML Service health check failed${NC}"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Services:"
echo "  - Frontend: http://localhost"
echo "  - API: http://localhost/api"
echo "  - API Docs: http://localhost/api/docs"
echo "  - Grafana: http://localhost/grafana"
echo "  - Grafana Login: admin/admin123"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f backend    # View backend logs"
echo "  docker-compose logs -f ml-service # View ML logs"
echo "  docker-compose ps                 # Check service status"
echo ""
