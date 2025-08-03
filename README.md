# 🦷 OralSmart

OralSmart is a Django web application for pediatric oral health risk assessment with AI-powered predictions. It provides comprehensive dental and dietary screening with machine learning-based risk classification for healthcare professionals.

## 🚀 Key Features

- **Patient Management**: Registration and demographic tracking
- **Comprehensive Screening**: Dental and dietary assessments
- **AI Risk Assessment**: 3-class prediction (Low/Medium/High risk)
- **Dual Report System**: Patient-friendly and professional versions
- **ML Model Training**: Advanced feature selection and hyperparameter tuning
- **Factory Data Generation**: Realistic test data for ML training
- **Clinical Decision Support**: Evidence-based recommendations

## 🎯 AI Risk Assessment System

### Risk Classification
- **🟢 Low Risk**: Continue preventive care, regular check-ups
- **🟡 Medium Risk**: Regular monitoring, follow-up in 3-6 months  
- **🔴 High Risk**: Immediate dental intervention recommended

### Dual Report System
- **Patient Reports**: Clean, privacy-focused versions without AI risk data
- **Professional Reports**: Enhanced versions with full AI analysis and clinical recommendations

### ML Model Features
- **Feature Selection**: 3 methods (Random Forest importance, K-Best, RFE)
- **Hyperparameter Tuning**: Automated GridSearchCV optimization
- **Cross-Validation**: 5-fold validation for robust performance
- **Enhanced Training**: Terminal-based training with comprehensive reporting

## 🧪 Quick Start & Testing

### Model Training Commands
```bash
# Navigate to Django project
cd src

# Basic enhanced training (recommended)
python manage.py train_ml_model balanced_3class_training_data.csv

# Fast training (feature selection only)
python manage.py train_ml_model balanced_3class_training_data.csv --fast

# Test AI integration
python manage.py test_ai_integration

# Export training data
python manage.py export_training_data
```

## 🛠️ Tech Stack & Setup

### Technology Stack
- **Backend**: Python 3.11.0, Django 3.2.25
- **Database**: SQLite/MySQL  
- **ML**: Neural Networks (MLPClassifier), scikit-learn
- **Frontend**: HTML/CSS (Django templates)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/vhutali01/oralsmart.git
cd oralsmart

# 2. Create virtual environment
python -m venv venv

# Windows
./venv/Scripts/activate

# Mac/Linux  
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database and run
cd src
python manage.py migrate
python manage.py runserver
```

Visit http://127.0.0.1:8000 to access the application.

## 🏭 Data Generation & ML Training

### Factory System for Test Data
Generate realistic patient data for ML training:

```python
# Generate complete patient records with assessments
from patient.factory import PatientWithAssessmentsFactory

# Single patient with assessments
patient = PatientWithAssessmentsFactory()

# Bulk generation for ML training
patients = PatientWithAssessmentsFactory.create_batch(1000)
```

### Terminal Commands for Data Generation
```bash
cd src

# Generate test patients
python manage.py shell -c "
from patient.factory import PatientWithAssessmentsFactory
patients = PatientWithAssessmentsFactory.create_batch(500)
print(f'Created {len(patients)} patients with assessments')
"

# Export and train model
python manage.py export_training_data --output training.csv
python manage.py train_ml_model training.csv
```

## 📊 Clinical Algorithm Overview

The risk assessment uses evidence-based scoring:

### Major Risk Factors (+2 points each)
- Cavitated lesions, missing teeth, multiple restorations
- Enamel changes, dentin discoloration, white spot lesions

### Dietary Risk Factors (+1 point each)  
- Sweet/sugary foods, processed foods, sugar-sweetened beverages
- Additional +1 point for consumption ≥3 times daily

### Protective Factors (-1 point each)
- Fluoride water/toothpaste, regular checkups
- Professional topical fluoride, pit and fissure sealants

### Risk Thresholds
- **High Risk**: ≥8.0 points (immediate intervention)
- **Medium Risk**: 5.2-7.9 points (regular monitoring)  
- **Low Risk**: <5.2 points (preventive care)

*Thresholds adjust based on data completeness for conservative assessment*

## 🔧 Development & Testing

### Available Test Scripts
```bash
# Test ML predictions
python test_3class_predictions.py

# Test Django training integration  
python test_django_training.py

# Test enhanced ML features
python test_enhanced_ml_model.py

# Test report AI integration
python test_report_ai_integration.py
```

### Factory Usage in Tests
```python
from patient.factory import PatientWithAssessmentsFactory

class TestPatientViews(TestCase):
    def setUp(self):
        self.patient = PatientWithAssessmentsFactory()
        
    def test_patient_has_assessments(self):
        self.assertTrue(self.patient.dental_screenings.exists())
        self.assertTrue(self.patient.dietary_screenings.exists())
```

## 📈 Performance & Features

### ML Model Performance
| Training Mode | Time | Test Accuracy | Features | Use Case |
|---------------|------|---------------|----------|----------|
| **Full Enhancement** | 10-30 min | ~87% | 40/68 | Production |
| **Fast Mode** | 2-5 min | ~87% | 30/68 | Development |
| **Baseline** | 1-2 min | ~87% | All | Quick testing |

### Key Capabilities
- ✅ **3-Class Risk Prediction** with confidence scores
- ✅ **Dual Report System** for patient privacy
- ✅ **Advanced ML Features** (feature selection, hyperparameter tuning)
- ✅ **Factory Data Generation** for realistic test data
- ✅ **Evidence-Based Scoring** following clinical guidelines
- ✅ **Django Integration** with management commands
- ✅ **Cross-Validation** for robust model evaluation

## 🚀 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**OralSmart** - AI-Powered Pediatric Oral Health Risk Assessment 🦷🤖
