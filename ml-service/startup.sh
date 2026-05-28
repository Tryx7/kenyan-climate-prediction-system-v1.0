#!/bin/bash
set -e

echo "Starting Kenya Climate ML Service..."

# Create models directory if it doesn't exist
mkdir -p /app/models

# Check if models exist, if not train them
if [ ! -f "/app/models/rainfall_model.pkl" ]; then
    echo "Models not found. Training initial models..."
    python -c "
import asyncio
import sys
sys.path.insert(0, '/app')
from services.model_trainer import ModelTrainer

trainer = ModelTrainer()
results = trainer.train_all_models(force=True)

print('Training Results:')
for model, metrics in results.items():
    print(f'  {model}: {metrics}')
"
    echo "Models trained successfully!"
else
    echo "Models already exist."
fi

echo "Starting ML API server..."
exec uvicorn app:app --host 0.0.0.0 --port 5001
