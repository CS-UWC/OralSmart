# AI Risk Assessment Integration - Quick Reference

## Overview

OralSmart's AI risk assessment system provides **real-time oral health risk predictions** integrated into the report generation system. The system ensures **patient privacy** while providing **clinical decision support** to healthcare professionals.

## Key Features

### 🎯 3-Class Risk Prediction
- **Low Risk**: Continue preventive care, regular check-ups
- **Medium Risk**: Regular monitoring, follow-up in 3-6 months  
- **High Risk**: Immediate dental intervention recommended

### 👥 Dual Report System
- **Patient Reports**: Clean, AI-free versions for patients
- **Professional Reports**: Enhanced versions with full AI analysis

### 🔒 Privacy Protection
- Patients never see technical risk classifications
- Healthcare providers get clinical decision support
- Separate email workflows for different audiences

## Report Types

| Report Type | AI Assessment | Audience | Purpose |
|-------------|---------------|----------|---------|
| Browser View | ❌ No | Patient | Review screening data |
| Patient Email | ❌ No | Patient | Personal records |
| Professional Email | ✅ Yes | Healthcare Providers | Clinical decisions |

## AI Assessment Components

### Risk Level Display
```
🔴 HIGH RISK
- Confidence: 95.2%
- Immediate intervention recommended
```

### Probability Breakdown
- Low Risk: 2.1%
- Medium Risk: 2.7% 
- High Risk: 95.2%

### Clinical Recommendations
- **High Risk**: ⚠️ Immediate dental intervention recommended
- **Medium Risk**: ⚡ Regular monitoring, follow-up in 3-6 months
- **Low Risk**: ✅ Continue preventive care, regular check-ups

## Technical Implementation

### Email Workflow
1. **Patient Email**: Generated with `include_ai_assessment=False`
2. **Professional Email**: Generated with `include_ai_assessment=True`
3. **Separate Subjects**: Professional emails get `[PROFESSIONAL]` prefix

### PDF Generation
```python
# Patient version (clean)
patient_pdf = generate_pdf_buffer(patient, sections, include_ai_assessment=False)

# Professional version (with AI)
professional_pdf = generate_pdf_buffer(patient, sections, include_ai_assessment=True)
```

### ML Prediction
```python
from reports.views import get_ml_risk_prediction

# Get prediction for patient
ml_prediction = get_ml_risk_prediction(dental_data, dietary_data)

# Returns:
{
    'risk_level': 'high',
    'confidence': 95.2,
    'probability_low_risk': 2.1,
    'probability_medium_risk': 2.7, 
    'probability_high_risk': 95.2,
    'available': True,
    'error': None
}
```

## Testing

### Quick Test
```bash
cd src
python manage.py test_ai_integration
```

### Expected Output
```
🧪 Testing AI Risk Assessment Integration in Reports
============================================================
✅ Using test patient: Carmen Casey (ID: 2)

🔬 Test 1: ML Risk Prediction Function
✅ ML Prediction successful:
   Risk Level: high
   Confidence: 99.9%
   Probabilities: Low=0.0%, Medium=0.0%, High=99.9%

📄 Test 2: Patient PDF Generation (without AI)
✅ Patient PDF generated successfully (5,384 bytes)

🏥 Test 3: Professional PDF Generation (with AI)
✅ Professional PDF generated successfully (5,981 bytes)
✅ Professional PDF is larger than patient PDF (597 bytes difference)

🤖 Test 4: ML Model Status
✅ ML model is trained and ready
```

## Benefits

### For Patients
- ✅ Clean, understandable reports
- ✅ No confusing technical data
- ✅ Privacy protection
- ✅ Focus on screening results

### For Healthcare Professionals
- ✅ Real-time AI decision support
- ✅ Risk level classifications
- ✅ Confidence scoring
- ✅ Clinical recommendations
- ✅ Evidence-based guidance

## Model Performance

The current ML model achieves:
- **93.01% accuracy** on test data
- **3-class classification** (Low/Medium/High)
- **68 features** from dental and dietary assessments
- **Neural network architecture** (MLPClassifier)

## Files Modified

### Core Integration
- `reports/views.py` - Main integration logic
- `reports/views.py::get_ml_risk_prediction()` - ML prediction function
- `reports/views.py::generate_pdf_buffer()` - Dual PDF generation

### Email Templates
- `templates/reports/email_template.html` - Patient-friendly email template

### Testing
- `ml_models/management/commands/test_ai_integration.py` - Integration testing

## Future Enhancements

### Planned Features
- Dashboard risk summaries for clinics
- Risk trend analysis over time
- Batch risk assessment for multiple patients
- Integration with clinical workflows

### Model Improvements
- Continuous learning from clinical outcomes
- Feature importance analysis
- Threshold optimization based on clinical feedback
- Multi-language support for recommendations
