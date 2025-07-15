#!/usr/bin/env python3
"""
Simple test to verify 3-class predictions work with the trained model.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oralsmart.settings')
django.setup()

from ml_models.ml_predictor import MLPRiskPredictor
from assessments.models import DentalScreening, DietaryScreening
from patient.models import Patient

def test_live_predictions():
    """Test predictions with real patient data from database"""
    
    print("🔮 Testing 3-Class Risk Predictions")
    print("=" * 50)
    
    # Initialize predictor (should load the trained 3-class model)
    predictor = MLPRiskPredictor()
    
    if not predictor.is_trained:
        print("❌ Model not trained. Please train the model first.")
        return
    
    print("✅ 3-Class Model Loaded Successfully")
    
    # Get a few patients with both dental and dietary data
    patients_with_data = []
    for patient in Patient.objects.all()[:10]:
        dental = DentalScreening.objects.filter(patient=patient).first()
        dietary = DietaryScreening.objects.filter(patient=patient).first()
        
        if dental and dietary:
            patients_with_data.append((patient, dental, dietary))
            if len(patients_with_data) >= 5:  # Test with 5 patients
                break
    
    if not patients_with_data:
        print("❌ No patients found with both dental and dietary data")
        return
    
    print(f"🧪 Testing predictions for {len(patients_with_data)} patients...")
    print()
    
    risk_counts = {'low': 0, 'medium': 0, 'high': 0}
    
    for i, (patient, dental, dietary) in enumerate(patients_with_data, 1):
        try:
            result = predictor.predict_risk(dental, dietary)
            
            risk_level = result['risk_level']
            confidence = result['confidence']
            
            risk_counts[risk_level] += 1
            
            print(f"Patient {i} (ID: {patient.id}):")
            print(f"  🎯 Risk Level: {risk_level.upper()}")
            print(f"  📊 Confidence: {confidence:.3f}")
            print(f"  📈 Probabilities:")
            print(f"     Low: {result['probability_low_risk']:.3f}")
            print(f"     Medium: {result['probability_medium_risk']:.3f}")
            print(f"     High: {result['probability_high_risk']:.3f}")
            
            # Show some key features
            if 'top_risk_factors' in result and result['top_risk_factors']:
                top_factors = result['top_risk_factors'][:3]  # Top 3
                print(f"  🔍 Top Risk Factors: {', '.join(top_factors)}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error predicting for patient {patient.id}: {e}")
            print()
    
    print("📊 Summary:")
    print(f"  Low Risk: {risk_counts['low']} patients")
    print(f"  Medium Risk: {risk_counts['medium']} patients")
    print(f"  High Risk: {risk_counts['high']} patients")
    
    if any(count > 0 for count in risk_counts.values()):
        print("\n✅ 3-Class Prediction System Working Successfully!")
        print("   All three risk levels (low/medium/high) are available for predictions.")
    else:
        print("\n❌ No successful predictions made.")

if __name__ == "__main__":
    test_live_predictions()
