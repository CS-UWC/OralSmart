"""
Test the ML Predictor functionality
"""
import os
import sys
import django
from django.conf import settings

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oralsmart.settings')

try:
    django.setup()
    from ml_models.ml_predictor import MLPRiskPredictor
    
    def test_ml_predictor():
        print("Testing ML Risk Predictor...")
        
        # Initialize predictor
        predictor = MLPRiskPredictor()
        
        # Test 1: Get model info
        print("\n1. Getting model info...")
        model_info = predictor.get_model_info()
        print(f"Model status: {model_info['status']}")
        
        # Test 2: Create sample data
        print("\n2. Creating sample training data...")
        sample_file = "test_sample_data.csv"
        predictor.create_sample_training_data(sample_file, num_samples=100)
        print(f"Sample data created: {sample_file}")
        
        # Test 3: Train model
        print("\n3. Training model...")
        results = predictor.train_from_csv(sample_file, target_column='risk_level')
        print(f"Training completed!")
        print(f"Test accuracy: {results['test_accuracy']:.4f}")
        print(f"Train accuracy: {results['train_accuracy']:.4f}")
        
        # Test 4: Make prediction
        print("\n4. Making prediction...")
        
        # Create mock data
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
        
        mock_dental = MockDentalData()
        mock_dietary = MockDietaryData()
        
        prediction = predictor.predict_risk(mock_dental, mock_dietary)
        
        print(f"Risk Level: {prediction['risk_level']}")
        print(f"Confidence: {prediction['confidence']:.4f}")
        print(f"High Risk Probability: {prediction['probability_high_risk']:.4f}")
        print(f"Low Risk Probability: {prediction['probability_low_risk']:.4f}")
        print(f"Top Risk Factors: {prediction['top_risk_factors'][:3]}")
        
        # Test 5: Get updated model info
        print("\n5. Getting updated model info...")
        model_info = predictor.get_model_info()
        print(f"Model status: {model_info['status']}")
        print(f"Features: {model_info['feature_count']}")
        
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)
        
        print("\n✅ All tests passed successfully!")
        
    if __name__ == "__main__":
        test_ml_predictor()
        
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
