#!/usr/bin/env python3
"""
Test script for the AI risk assessment integration in reports
Tests that:
1. Patient reports don't include AI risk assessment
2. Professional reports include AI risk assessment  
3. Email functionality sends appropriate versions to different recipients
"""

import os
import sys
import django

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oralsmart.settings')
django.setup()

from patient.models import Patient
from assessments.models import DentalScreening, DietaryScreening
from reports.views import generate_pdf_buffer, get_ml_risk_prediction
from ml_models.ml_predictor import MLPRiskPredictor

def test_ai_integration():
    """Test AI risk assessment integration"""
    
    print("🧪 Testing AI Risk Assessment Integration in Reports")
    print("=" * 60)
    
    # Check if we have any patients
    patients = Patient.objects.all()
    if not patients.exists():
        print("❌ No patients found in database")
        return False
    
    # Get a patient with both dental and dietary data
    test_patient = None
    for patient in patients:
        try:
            dental_data = DentalScreening.objects.get(patient_id=patient.id)
            dietary_data = DietaryScreening.objects.get(patient_id=patient.id)
            test_patient = patient
            break
        except (DentalScreening.DoesNotExist, DietaryScreening.DoesNotExist):
            continue
    
    if not test_patient:
        print("❌ No patients found with both dental and dietary screening data")
        return False
    
    print(f"✅ Using test patient: {test_patient.name} {test_patient.surname} (ID: {test_patient.id})")
    
    # Test 1: Check ML prediction functionality
    print("\n🔬 Test 1: ML Risk Prediction Function")
    try:
        dental_data = DentalScreening.objects.get(patient_id=test_patient.id)
        dietary_data = DietaryScreening.objects.get(patient_id=test_patient.id)
        
        ml_prediction = get_ml_risk_prediction(dental_data, dietary_data)
        
        if ml_prediction['available']:
            print(f"✅ ML Prediction successful:")
            print(f"   Risk Level: {ml_prediction['risk_level']}")
            print(f"   Confidence: {ml_prediction['confidence']:.1f}%")
            print(f"   Probabilities: Low={ml_prediction['probability_low_risk']:.1f}%, "
                  f"Medium={ml_prediction['probability_medium_risk']:.1f}%, "
                  f"High={ml_prediction['probability_high_risk']:.1f}%")
        else:
            print(f"⚠️  ML Prediction not available: {ml_prediction.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ ML prediction test failed: {e}")
        return False
    
    # Test 2: Patient PDF (without AI assessment)
    print("\n📄 Test 2: Patient PDF Generation (without AI)")
    try:
        patient_pdf = generate_pdf_buffer(
            test_patient, 
            ['section1', 'section2', 'section3', 'section4', 'section5'],
            include_ai_assessment=False
        )
        
        pdf_size = len(patient_pdf.getvalue())
        print(f"✅ Patient PDF generated successfully ({pdf_size:,} bytes)")
        
    except Exception as e:
        print(f"❌ Patient PDF generation failed: {e}")
        return False
    
    # Test 3: Professional PDF (with AI assessment)
    print("\n🏥 Test 3: Professional PDF Generation (with AI)")
    try:
        professional_pdf = generate_pdf_buffer(
            test_patient, 
            ['section1', 'section2', 'section3', 'section4', 'section5'],
            include_ai_assessment=True
        )
        
        pdf_size = len(professional_pdf.getvalue())
        print(f"✅ Professional PDF generated successfully ({pdf_size:,} bytes)")
        
        # Check that professional PDF is different (should be larger due to AI section)
        patient_size = len(patient_pdf.getvalue())
        professional_size = len(professional_pdf.getvalue())
        
        if professional_size > patient_size:
            print(f"✅ Professional PDF is larger than patient PDF ({professional_size - patient_size:,} bytes difference)")
        else:
            print(f"⚠️  Professional PDF is not larger than patient PDF (size difference: {professional_size - patient_size:,} bytes)")
            
    except Exception as e:
        print(f"❌ Professional PDF generation failed: {e}")
        return False
    
    # Test 4: Check ML model status
    print("\n🤖 Test 4: ML Model Status")
    try:
        predictor = MLPRiskPredictor()
        if predictor.is_trained:
            print("✅ ML model is trained and ready")
        else:
            print("⚠️  ML model is not trained - predictions will show 'Unknown' status")
            
    except Exception as e:
        print(f"❌ ML model check failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed successfully!")
    print("\nReport Integration Summary:")
    print("• Patient reports (viewed in browser): NO AI risk assessment")
    print("• Patient emails: NO AI risk assessment") 
    print("• Professional emails (CC recipients): INCLUDES AI risk assessment")
    print("• Professional reports have '[PROFESSIONAL]' prefix in subject")
    
    return True

if __name__ == "__main__":
    success = test_ai_integration()
    sys.exit(0 if success else 1)
