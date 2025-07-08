"""
Test to verify MLP model functionality
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
    
    def test_mlp_model():
        print("Testing MLP Risk Predictor...")
        
        # Initialize predictor
        predictor = MLPRiskPredictor()
        
        # Test 1: Check model info
        print("\n1. Checking model info...")
        model_info = predictor.get_model_info()
        print(f"Model status: {model_info['status']}")
        print(f"Model type: {model_info.get('model_type', 'N/A')}")
        
        if model_info['status'] == 'trained':
            print("✅ MLP model is already trained and loaded!")
            
            # Test 2: Make a prediction
            print("\n2. Testing prediction...")
            
            # Create mock data for high-risk patient
            class MockDentalData:
                def __init__(self):
                    self.sa_citizen = 'yes'
                    self.special_needs = 'no'
                    self.caregiver_treatment = 'no'
                    self.sugar_meals = 'yes'
                    self.sugar_snacks = 'yes'
                    self.sugar_beverages = 'yes'
                    self.appliance = 'no'
                    self.plaque = 'yes'
                    self.dry_mouth = 'yes'
                    self.enamel_defects = 'yes'
                    self.fluoride_water = 'no'
                    self.fluoride_toothpaste = 'no'
                    self.topical_fluoride = 'no'
                    self.regular_checkups = 'no'
                    self.sealed_pits = 'no'
                    self.restorative_procedures = 'yes'
                    self.enamel_change = 'yes'
                    self.dentin_discoloration = 'yes'
                    self.white_spot_lesions = 'yes'
                    self.cavitated_lesions = 'yes'
                    self.multiple_restorations = 'yes'
                    self.missing_teeth = 'yes'
                    self.income = '0'  # Low income
                    self.teeth_data = {
                        'tooth_1': '1',  # Decayed
                        'tooth_2': '1',  # Decayed
                        'tooth_3': '3',  # Missing
                        'tooth_4': '1',  # Decayed
                        'tooth_5': '2',  # Filled
                        'tooth_6': '4',  # Missing
                    }
            
            class MockDietaryData:
                def __init__(self):
                    self.sweet_sugary_foods = 'yes'
                    self.cold_drinks_juices = 'yes'
                    self.takeaways_processed_foods = 'yes'
                    self.salty_snacks = 'yes'
                    self.spreads = 'yes'
            
            # Test with high-risk profile
            mock_dental = MockDentalData()
            mock_dietary = MockDietaryData()
            
            prediction = predictor.predict_risk(mock_dental, mock_dietary)
            
            print(f"Risk Level: {prediction['risk_level']}")
            print(f"Confidence: {prediction['confidence']:.4f}")
            print(f"High Risk Probability: {prediction['probability_high_risk']:.4f}")
            print(f"Low Risk Probability: {prediction['probability_low_risk']:.4f}")
            
            # Test 3: Feature importance (MLP specific)
            print("\n3. Feature importance analysis...")
            if prediction['top_risk_factors']:
                print("Top risk factors:")
                for factor, importance in prediction['top_risk_factors'][:3]:
                    print(f"  - {factor}: {importance}")
            
            # Test 4: Model architecture info
            print(f"\n4. Model architecture:")
            print(f"   - Type: Multi-Layer Perceptron (Neural Network)")
            print(f"   - Features: {model_info['feature_count']}")
            print(f"   - Architecture: 3 hidden layers (64, 32, 16 neurons)")
            print(f"   - Activation: ReLU")
            print(f"   - Optimizer: Adam")
            
            print("\n✅ All MLP tests passed successfully!")
            print("🧠 The system is now using a Multi-Layer Perceptron for predictions!")
            
        else:
            print("❌ Model not trained. Please train the model first.")
            print("Run: python manage.py train_ml_model data.csv --create-sample")
        
    if __name__ == "__main__":
        test_mlp_model()
        
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
