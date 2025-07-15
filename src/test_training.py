#!/usr/bin/env python
"""
Test script to train the ML model with exported data
"""
import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oralsmart.settings')
django.setup()

from ml_models.ml_predictor import MLPRiskPredictor

def main():
    print("Loading ML predictor...")
    predictor = MLPRiskPredictor()
    
    print("Training model with exported data...")
    results = predictor.train_from_csv('balanced_training_data.csv')
    
    print("\n" + "="*50)
    print("TRAINING RESULTS")
    print("="*50)
    print(f"Train Accuracy: {results['train_accuracy']:.4f}")
    print(f"Test Accuracy: {results['test_accuracy']:.4f}")
    print(f"Training Samples: {results['train_samples']}")
    print(f"Test Samples: {results['test_samples']}")
    print(f"Features Used: {results['features_used']}")
    print(f"Model Type: {results['model_type']}")
    print(f"Iterations: {results['iterations']}")
    print(f"Final Loss: {results['loss']:.6f}")
    
    print("\nClassification Report:")
    print(results['classification_report'])

if __name__ == "__main__":
    main()
