#!/usr/bin/env python
"""
Complete example of exporting data and training the ML model
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oralsmart.settings')
django.setup()

from ml_models.ml_predictor import MLPRiskPredictor
from django.core.management import call_command

def main():
    print("="*60)
    print("COMPLETE ML MODEL TRAINING WORKFLOW")
    print("="*60)
    
    # Step 1: Export data with dry run to check statistics
    print("\n1. Checking data statistics...")
    call_command('export_training_data', dry_run=True, risk_threshold=15)
    
    # Step 2: Export actual training data
    print("\n2. Exporting training data...")
    call_command('export_training_data', 
                 output='workflow_training_data.csv', 
                 risk_threshold=15)
    
    # Step 3: Train the model
    print("\n3. Training ML model...")
    predictor = MLPRiskPredictor()
    results = predictor.train_from_csv('workflow_training_data.csv')
    
    # Step 4: Display results
    print("\n4. Training completed!")
    print("="*50)
    print("FINAL RESULTS")
    print("="*50)
    print(f"✅ Test Accuracy: {results['test_accuracy']:.4f}")
    print(f"✅ Training Samples: {results['train_samples']:,}")
    print(f"✅ Test Samples: {results['test_samples']:,}")
    print(f"✅ Features Used: {results['features_used']}")
    print(f"✅ Training Iterations: {results['iterations']}")
    print(f"✅ Final Loss: {results['loss']:.6f}")
    print(f"✅ Model Type: {results['model_type']}")
    
    # Step 5: Model is now ready for predictions
    print(f"\n5. Model saved and ready for predictions!")
    print(f"   📁 Model file: {predictor.model_path}")
    print(f"   📁 Scaler file: {predictor.scaler_path}")
    
    print("\n" + "="*60)
    print("WORKFLOW COMPLETE! 🎉")
    print("Your ML model is now trained and ready to predict oral health risk.")
    print("="*60)

if __name__ == "__main__":
    main()
