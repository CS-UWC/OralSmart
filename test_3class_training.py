#!/usr/bin/env python3
"""
Test script for 3-class ML model training with low/medium/high risk classification.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oralsmart.settings')
django.setup()

from ml_models.ml_predictor import MLPRiskPredictor

def test_3class_training():
    """Test training the ML model with 3-class data"""
    
    print("🧠 Testing 3-Class ML Model Training")
    print("=" * 50)
    
    # Initialize predictor
    predictor = MLPRiskPredictor()
    
    # Train with 3-class data
    csv_path = 'src/balanced_3class_training_data.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: Training data file not found at {csv_path}")
        return
    
    print(f"📊 Training model with 3-class data from: {csv_path}")
    
    try:
        # Train the model
        results = predictor.train_from_csv(csv_path, target_column='risk_level')
        
        print("\n✅ Training Results:")
        print(f"📈 Training Accuracy: {results['train_accuracy']:.4f}")
        print(f"📈 Test Accuracy: {results['test_accuracy']:.4f}")
        print(f"📊 Training Samples: {results['train_samples']}")
        print(f"📊 Test Samples: {results['test_samples']}")
        print(f"🔧 Features Used: {results['features_used']}")
        print(f"🔄 Training Iterations: {results['iterations']}")
        print(f"📉 Final Loss: {results['loss']:.6f}")
        
        print("\n📋 Classification Report:")
        print(results['classification_report'])
        
        print("\n🔀 Confusion Matrix:")
        cm = results['confusion_matrix']
        print("     Low  Med  High")
        for i, row in enumerate(cm):
            labels = ['Low ', 'Med ', 'High']
            print(f"{labels[i]} {row}")
        
        print("\n🎯 Testing Predictions with Sample Data...")
        
        # Test some predictions
        test_cases = [
            {"name": "Low Risk Patient", "dmft": 0, "cavities": 0, "plaque": 0, "sugar_freq": 1},
            {"name": "Medium Risk Patient", "dmft": 2, "cavities": 1, "plaque": 1, "sugar_freq": 3},
            {"name": "High Risk Patient", "dmft": 8, "cavities": 1, "plaque": 1, "sugar_freq": 5}
        ]
        
        for case in test_cases:
            # Create mock dental data
            dental_data = {
                'total_dmft_score': case['dmft'],
                'cavitated_lesions': case['cavities'],
                'plaque': case['plaque']
            }
            
            # Create mock dietary data  
            dietary_data = {
                'sugar_frequency': case['sugar_freq']
            }
            
            try:
                result = predictor.predict_risk(dental_data, dietary_data)
                print(f"\n🔮 {case['name']}:")
                print(f"   Risk Level: {result['risk_level']}")
                print(f"   Confidence: {result['confidence']:.3f}")
                print(f"   Low: {result['probability_low_risk']:.3f}")
                print(f"   Medium: {result['probability_medium_risk']:.3f}")
                print(f"   High: {result['probability_high_risk']:.3f}")
            except Exception as e:
                print(f"   ❌ Prediction failed: {e}")
        
        print("\n✅ 3-Class Model Training Completed Successfully!")
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_3class_training()
