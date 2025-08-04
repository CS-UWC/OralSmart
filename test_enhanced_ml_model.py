#!/usr/bin/env python
"""
Enhanced ML Model Training Test Script with Feature Selection, Hyperparameter Tuning, and 5-Fold CV

This script demonstrates the new enhanced features:
1. Feature Selection using Random Forest importance, K-best, or RFE
2. Hyperparameter Tuning using GridSearchCV
3. 5-Fold Cross-Validation for robust model evaluation
4. Comprehensive validation reporting

Usage:
    python test_enhanced_ml_model.py

Make sure you have training data available before running this script.
"""

import os
import sys
import django

# Setup Django environment
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oralsmart.settings')
django.setup()

from ml_models.ml_predictor import MLPRiskPredictor

def test_enhanced_training():
    """Test the enhanced training features."""
    print("🚀 Testing Enhanced ML Model Training")
    print("=" * 60)
    
    # Initialize predictor
    predictor = MLPRiskPredictor()
    
    # Check for training data
    training_data_path = os.path.join(project_root, 'src', 'balanced_3class_training_data.csv')
    if not os.path.exists(training_data_path):
        print("❌ Training data not found!")
        print(f"Expected: {training_data_path}")
        print("\nPlease run the following command first:")
        print("python manage.py export_training_data --risk-threshold 15 --output balanced_3class_training_data.csv")
        return
    
    print(f"✅ Found training data: {training_data_path}")
    print()
    
    # Test 1: Basic training with all enhancements
    print("🧪 Test 1: Full Enhancement Training")
    print("-" * 40)
    try:
        results = predictor.train_from_csv(
            csv_file_path=training_data_path,
            use_feature_selection=True,
            use_hyperparameter_tuning=True,
            feature_selection_method='importance',
            n_features=40  # Select top 40 features
        )
        print("✅ Full enhancement training completed successfully!")
        print(f"   Test Accuracy: {results['test_accuracy']:.4f}")
        print(f"   CV Mean: {results['cross_validation']['cv_mean']:.4f}")
        print(f"   Features: {results['original_features']} → {results['features_used']}")
        print()
        
    except Exception as e:
        print(f"❌ Full enhancement training failed: {e}")
        return
    
    # Test 2: Feature selection only (faster)
    print("🧪 Test 2: Feature Selection Only")
    print("-" * 40)
    try:
        results = predictor.train_from_csv(
            csv_file_path=training_data_path,
            use_feature_selection=True,
            use_hyperparameter_tuning=False,  # Skip tuning for speed
            feature_selection_method='kbest',
            n_features=30
        )
        print("✅ Feature selection training completed!")
        print(f"   Test Accuracy: {results['test_accuracy']:.4f}")
        print(f"   CV Mean: {results['cross_validation']['cv_mean']:.4f}")
        print()
        
    except Exception as e:
        print(f"❌ Feature selection training failed: {e}")
    
    # Test 3: Traditional training (no enhancements)
    print("🧪 Test 3: Traditional Training (Baseline)")
    print("-" * 40)
    try:
        results = predictor.train_from_csv(
            csv_file_path=training_data_path,
            use_feature_selection=False,
            use_hyperparameter_tuning=False
        )
        print("✅ Traditional training completed!")
        print(f"   Test Accuracy: {results['test_accuracy']:.4f}")
        print(f"   CV Mean: {results['cross_validation']['cv_mean']:.4f}")
        print()
        
    except Exception as e:
        print(f"❌ Traditional training failed: {e}")
    
    # Test 4: Test prediction with enhanced model
    print("🧪 Test 4: Testing Prediction")
    print("-" * 40)
    try:
        # Create mock data for prediction
        class MockDentalData:
            def __init__(self):
                self.sa_citizen = 'yes'
                self.special_needs = 'no'
                self.caregiver_treatment = 'no'
                self.appliance = 'no'
                self.plaque = 'yes'
                self.dry_mouth = 'no'
                self.enamel_defects = 'yes'
                self.fluoride_water = 'yes'
                self.fluoride_toothpaste = 'yes'
                self.topical_fluoride = 'no'
                self.regular_checkups = 'no'
                self.sealed_pits = 'no'
                self.restorative_procedures = 'yes'
                self.enamel_change = 'yes'
                self.dentin_discoloration = 'no'
                self.white_spot_lesions = 'yes'
                self.cavitated_lesions = 'yes'
                self.multiple_restorations = 'no'
                self.missing_teeth = 'yes'
                self.teeth_data = '{"1": "decayed", "2": "healthy", "3": "filled"}'  # Sample teeth data

        class MockDietaryData:
            def __init__(self):
                self.sweet_sugary_foods = 'yes'
                self.sweet_sugary_foods_daily = '2-3 times'
                self.sweet_sugary_foods_weekly = '4-5 times'
                self.sweet_sugary_foods_timing = 'between meals'
                self.sweet_sugary_foods_bedtime = 'yes'
                self.takeaways_processed_foods = 'yes'
                self.takeaways_processed_foods_daily = '1 time'
                self.takeaways_processed_foods_weekly = '2-3 times'
                self.fresh_fruit = 'yes'
                self.fresh_fruit_daily = '2-3 times'
                self.fresh_fruit_weekly = '4-6_week'
                self.fresh_fruit_timing = 'with meals'
                self.fresh_fruit_bedtime = 'no'
                self.cold_drinks_juices = 'yes'
                self.cold_drinks_juices_daily = '1-3_day'
                self.cold_drinks_juices_weekly = '3-4 times'
                self.cold_drinks_juices_timing = 'both'
                self.cold_drinks_juices_bedtime = 'no'
                self.processed_fruit = 'no'
                self.processed_fruit_daily = '0'
                self.processed_fruit_weekly = '0'
                self.processed_fruit_timing = ''
                self.processed_fruit_bedtime = 'no'
                self.spreads = 'yes'
                self.spreads_daily = '1 time'
                self.spreads_weekly = '3-4 times'
                self.spreads_timing = 'with meals'
                self.spreads_bedtime = 'no'
                self.added_sugars = 'yes'
                self.added_sugars_daily = '1-3_day'
                self.added_sugars_weekly = '2-3 times'
                self.added_sugars_timing = 'both'
                self.added_sugars_bedtime = 'no'
                self.salty_snacks = 'yes'
                self.salty_snacks_daily = '1 time'
                self.salty_snacks_weekly = '2-3 times'
                self.salty_snacks_timing = 'between meals'
                self.dairy_products = 'yes'
                self.dairy_products_daily = '2-3 times'
                self.dairy_products_weekly = '4-6_week'
                self.vegetables = 'yes'
                self.vegetables_daily = '1-3_day'
                self.vegetables_weekly = '4-5 times'
                self.water = 'yes'
                self.water_timing = 'with_meals'
                self.water_glasses = '2-4'

        # Make prediction
        mock_dental = MockDentalData()
        mock_dietary = MockDietaryData()
        
        prediction = predictor.predict_risk(mock_dental, mock_dietary)
        
        print("✅ Prediction successful!")
        print(f"   Risk Level: {prediction['risk_level']}")
        print(f"   Confidence: {prediction['confidence']:.4f}")
        print(f"   Probabilities:")
        print(f"     Low: {prediction['probability_low_risk']:.4f}")
        print(f"     Medium: {prediction['probability_medium_risk']:.4f}")
        print(f"     High: {prediction['probability_high_risk']:.4f}")
        print(f"   Top Risk Factors: {prediction['top_risk_factors'][:3]}")
        
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced ML Model Testing Completed!")
    print("\nNew Features Available:")
    print("✓ Feature Selection (Random Forest, K-best, RFE)")
    print("✓ Hyperparameter Tuning (GridSearchCV)")
    print("✓ 5-Fold Cross-Validation")
    print("✓ Comprehensive Validation Reporting")
    print("✓ Feature Importance Analysis")

if __name__ == "__main__":
    test_enhanced_training()
