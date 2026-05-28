#!/usr/bin/env python3
"""
Manual model retraining script
Usage: python retrain_models.py [--force]
"""

import argparse
import asyncio
import sys
import os

# Add ml-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ml-service'))

from services.model_trainer import ModelTrainer

async def main(force: bool = False):
    print("=" * 50)
    print("Kenya Climate ML Model Retraining")
    print("=" * 50)

    trainer = ModelTrainer()

    print(f"\nForce retrain: {force}")
    print("Starting training...\n")

    results = trainer.train_all_models(force=force)

    print("\n" + "=" * 50)
    print("Training Results:")
    print("=" * 50)

    for model_name, metrics in results.items():
        print(f"\n{model_name.upper()}:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                print(f"  {metric}: {value:.4f}")
            else:
                print(f"  {metric}: {value}")

    print("\n" + "=" * 50)
    print("Retraining complete!")
    print("=" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrain ML models")
    parser.add_argument("--force", action="store_true", help="Force retrain even if models exist")
    args = parser.parse_args()

    asyncio.run(main(force=args.force))
