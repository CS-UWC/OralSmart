"""
Example usage of the MLPRiskPredictor class.

This file demonstrates how to use the ML predictor for training and prediction.
"""

import sys
import os
import pandas as pd

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ml_models.ml_predictor import MLPRiskPredictor

def main():
    # Initialize the predictor
    predictor = MLPRiskPredictor()
    
    # Example 1: Create sample training data
    print("Creating sample training data...")
    sample_data_path = "sample_training_data.csv"
    predictor.create_sample_training_data(sample_data_path, num_samples=1000)
    
    # Example 2: Train the model
    print("\nTraining model from CSV...")
    training_results = predictor.train_from_csv(sample_data_path, target_column='risk_level')
    print(f"Training completed. Test accuracy: {training_results['test_accuracy']:.4f}")
    
    # Example 3: Get model information
    print("\nModel information:")
    model_info = predictor.get_model_info()
    print(f"Status: {model_info['status']}")
    print(f"Features: {len(model_info['features'])}")
    
    # Example 4: Make a prediction (requires creating a mock dental data object)
    # This is just for demonstration - in practice, you'd use actual Django model instances
    class MockDentalData:
        def __init__(self):
            self.sa_citizen = 'yes'
            self.special_needs = 'no'
            self.caregiver_treatment = 'yes'
            self.sugar_meals = 'yes'
            self.sugar_snacks = 'yes'
            self.sugar_beverages = 'yes'
            self.appliance = 'no'
            self.plaque = 'yes'
            self.dry_mouth = 'no'
            self.enamel_defects = 'yes'
            self.fluoride_water = 'no'
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
            self.missing_teeth = 'no'
            self.income = '1-2500'
            self.teeth_data = {
                'tooth_1': '1',  # Decayed
                'tooth_2': '2',  # Filled
                'tooth_3': '0',  # Healthy
                'tooth_4': '1',  # Decayed
            }
    
    class MockDietaryData:
        def __init__(self):
            self.sweet_sugary_foods = 'yes'
            self.cold_drinks_juices = 'yes'
            self.takeaways_processed_foods = 'yes'
            self.salty_snacks = 'no'
            self.spreads = 'no'
    
    print("\nMaking prediction...")
    mock_dental = MockDentalData()
    mock_dietary = MockDietaryData()
    
    prediction = predictor.predict_risk(mock_dental, mock_dietary)
    print(f"Risk Level: {prediction['risk_level']}")
    print(f"Confidence: {prediction['confidence']:.4f}")
    print(f"Probability High Risk: {prediction['probability_high_risk']:.4f}")
    print(f"Top Risk Factors: {prediction['top_risk_factors'][:3]}")
    
    # Clean up
    if os.path.exists(sample_data_path):
        os.remove(sample_data_path)
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main()
