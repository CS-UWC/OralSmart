# 🦷 OralSmart

OralSmart is a Django web application that allows users to register patients, screen for dental/dietary conditions, and predict oral health risk using machine learning.

## 🚀 Features

- Patient Registration
- Dental Screening
- Dietary Screening
- **AI-Powered Risk Assessment** (3-class: Low/Medium/High)
- **Real-time ML Predictions in Reports**
- **Professional vs Patient Report Versions**
- **Machine Learning Model Training**
- Referral System
- History & Reports
- Admin Panel

## 🧠 Documentation

### For Everyone
- 📖 **[How Risk Assessment Works](ORAL_HEALTH_RISK_EXPLAINED.md)** - Simple explanation of how the system determines oral health risk

### For Healthcare Professionals  
- 🏥 **[Clinical Algorithm Documentation](CLINICAL_ALGORITHM_DOCUMENTATION.md)** - Evidence-based clinical reasoning and algorithm details

### For Developers
- ⚙️ **[ML Model Training Guide](ML_EXPORT_README.md)** - Complete guide to training the machine learning model
- 🔧 **[ML Predictor Documentation](ML_PREDICTOR_README.md)** - Technical ML implementation details
- 🤖 **[AI Integration Guide](AI_INTEGRATION_GUIDE.md)** - Complete guide to AI risk assessment in reports

## 🧪 Testing & Validation

The system includes comprehensive testing tools for ML and report functionality:

```bash
# Test ML predictions with real patient data
python test_3class_predictions.py

# Test AI integration in reports (patient vs professional versions)
cd src && python manage.py test_ai_integration

# Export training data and train models
cd src && python manage.py export_training_data
cd src && python manage.py train_ml_model training_data.csv
```

## 🛠️ Tech Stack

- Python 3.11.0
- Django 3.2.25
- SQLite/MySQL
- HTML/CSS (Django templates)

## 🏁 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/vhutali01/oralsmart.git
cd oralsmart
```

###  2. Create a Virtual environment

#### on mac or linux

```bash
python -m venv venv
source venv/bin/activate
```
#### on Windows
```bash
python -m venv venv
./venv/Scripts/activate
```

### 3. Install dependences

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
python manage.py migrate
python manage.py runserver
```

### 5. Access the App

Visit http://127.0.0.1:8000

## 🏭 Test Data Generation with Factories

OralSmart includes comprehensive Factory Boy factories for generating realistic test data, particularly useful for machine learning model training and testing.

### Available Factories

#### 1. PatientFactory (`src/patient/factory.py`)
Creates individual patient records with realistic demographic data:

```python
from patient.factory import PatientFactory

# Create a single patient
patient = PatientFactory()

# Create multiple patients
patients = PatientFactory.create_batch(100)
```

**Features:**
- Gender-dependent name generation (male/female names based on gender field)
- Realistic parent information and contact details
- Age range appropriate for pediatric dental care (0-6 years)
- South African ID number generation

#### 2. Assessment Factories (`src/assessments/factory.py`)
Creates dental and dietary screening assessments with conditional logic:

```python
from assessments.factory import DentalFactory, DietaryFactory

# Create standalone assessments
dental_assessment = DentalFactory()
dietary_assessment = DietaryFactory()
```

**Features:**
- **Conditional Logic**: Mimics real form behavior where "yes" responses populate sub-fields with realistic values
- **Dental Screening**: Generates teeth data as JSON, various risk factors, and clinical observations
- **Dietary Screening**: Creates consumption patterns across 12 food categories with frequency and timing data

#### 3. PatientWithAssessmentsFactory (Recommended)
Creates complete patient records with both assessments automatically:

```python
from patient.factory import PatientWithAssessmentsFactory

# Create a patient with all assessments
complete_patient = PatientWithAssessmentsFactory()

# Bulk creation for ML training datasets
patients_with_data = PatientWithAssessmentsFactory.create_batch(1000)
```

### Bulk Data Generation for ML Training

To generate large datasets for machine learning model training:

```python
# Open Django shell
python manage.py shell

# Generate 7,000 complete patient records (as example)
from patient.factory import PatientWithAssessmentsFactory

# Create in batches with progress tracking
for i in range(70):
    PatientWithAssessmentsFactory.create_batch(100)
    print(f"Batch {i+1}/70 completed - {(i+1)*100} patients created")
```

### Factory Data Quality

The factories generate realistic, ML-ready data with:
- **Logical Consistency**: Food consumption data follows realistic patterns
- **Conditional Relationships**: Sub-fields populated only when relevant
- **Diverse Demographics**: Balanced gender distribution with appropriate names
- **Clinical Realism**: Dental findings and dietary patterns that reflect real-world scenarios

### Usage in Tests

```python
# In your test files
from patient.factory import PatientWithAssessmentsFactory

class TestPatientViews(TestCase):
    def setUp(self):
        self.patient = PatientWithAssessmentsFactory()
        
    def test_patient_has_assessments(self):
        self.assertTrue(self.patient.dental_screenings.exists())
        self.assertTrue(self.patient.dietary_screenings.exists())
```

This factory system enables rapid generation of comprehensive test datasets for both development testing and machine learning model training.

## 🧪 Quick Factory Usage Example

Here's a practical example of using factories to test your 3-class ML system:

```python
# Open Django shell
python manage.py shell

# Generate test data and train the ML model
from patient.factory import PatientWithAssessmentsFactory
from ml_models.ml_predictor import MLPRiskPredictor

# 1. Generate realistic test patients
print("🏭 Creating test patients...")
test_patients = PatientWithAssessmentsFactory.create_batch(500)
print(f"✅ Created {len(test_patients)} patients with assessments")

# 2. Export data for ML training
from export_training_data import export_to_csv
export_to_csv('test_training_data.csv')
print("✅ Training data exported")

# 3. Train the ML model
predictor = MLPRiskPredictor()
results = predictor.train_from_csv('test_training_data.csv')
print(f"🧠 Model trained with {results['test_accuracy']:.1%} accuracy")

# 4. Test prediction on a new patient
new_patient = PatientWithAssessmentsFactory()
dental_data = new_patient.dental_screenings.first()
dietary_data = new_patient.dietary_screenings.first()

prediction = predictor.predict_risk(dental_data, dietary_data)
print(f"🎯 Prediction: {prediction['risk_level']} risk ({prediction['confidence']:.1%} confidence)")
```

This example demonstrates the complete workflow from data generation to ML prediction using the factory system.

## 💻 Terminal Commands for Factory Usage

You can also run factory commands directly from the terminal without opening the Django shell:

### Quick Data Generation Commands

```bash
# Navigate to src directory first
cd src

# Generate 100 patients with assessments
python manage.py shell -c "
from patient.factory import PatientWithAssessmentsFactory
patients = PatientWithAssessmentsFactory.create_batch(100)
print(f'Created {len(patients)} patients with assessments')
"

# Export training data and train ML model
python manage.py shell -c "
from export_training_data import export_to_csv
from ml_models.ml_predictor import MLPRiskPredictor
export_to_csv('quick_training.csv')
predictor = MLPRiskPredictor()
results = predictor.train_from_csv('quick_training.csv')
print(f'Model trained with {results[\"test_accuracy\"]:.1%} accuracy')
"

# Test a single prediction
python manage.py shell -c "
from patient.factory import PatientWithAssessmentsFactory
from ml_models.ml_predictor import MLPRiskPredictor
patient = PatientWithAssessmentsFactory()
predictor = MLPRiskPredictor()
dental = patient.dental_screenings.first()
dietary = patient.dietary_screenings.first()
prediction = predictor.predict_risk(dental, dietary)
print(f'Prediction: {prediction[\"risk_level\"]} risk ({prediction[\"confidence\"]:.1%} confidence)')
"
```

### Batch Processing Commands

```bash
# Generate large datasets in batches (PowerShell/Command Prompt)
for /L %i in (1,1,10) do python manage.py shell -c "from patient.factory import PatientWithAssessmentsFactory; PatientWithAssessmentsFactory.create_batch(100); print('Batch %i completed')"

# For Bash/Linux/Mac
for i in {1..10}; do python manage.py shell -c "from patient.factory import PatientWithAssessmentsFactory; PatientWithAssessmentsFactory.create_batch(100); print(f'Batch $i completed')"; done
```

These terminal commands let you quickly generate test data and train models without interactive shell sessions.

## 🤖 AI Risk Assessment in Reports

OralSmart includes **real-time AI risk assessment integration** in the report system, providing clinical decision support for healthcare professionals while maintaining patient privacy.

### Report Versions

#### 👥 Patient Reports (Browser & Email)
- **Clean, patient-friendly reports** without AI risk classifications
- Focus on screening data and basic information
- No technical risk scores or medical recommendations
- Suitable for patient understanding and peace of mind

#### 🏥 Professional Reports (Email to Healthcare Providers)
- **Enhanced reports with full AI risk assessment**
- Includes risk level classification (Low/Medium/High)
- Confidence scores and probability breakdowns
- Color-coded clinical recommendations
- Professional subject line with `[PROFESSIONAL]` prefix
- Designed for clinical decision support

### How It Works

1. **Patient Views Report**: Clean version without AI assessment
2. **Patient Receives Email**: Same clean version without AI risk data
3. **Healthcare Providers (CC)**: Receive separate enhanced report with AI analysis

### Email Workflow

```
Patient Email: "OralSmart Dental Report - John Doe"
├── Clean PDF without AI assessment
└── Patient-friendly formatting

Professional Email: "[PROFESSIONAL] OralSmart Dental Report - John Doe" 
├── Enhanced PDF with AI risk assessment
├── Risk level, confidence, and probabilities
├── Clinical recommendations
└── Decision support information
```

### AI Assessment Features

- **3-Class Risk Prediction**: Low, Medium, High risk levels
- **Confidence Scoring**: Model certainty percentage
- **Probability Breakdown**: Individual class probabilities
- **Clinical Recommendations**: Actionable guidance based on risk level
- **Color-Coded Display**: Visual risk level indicators

### Testing the Integration

```bash
# Test AI integration in reports
cd src
python manage.py test_ai_integration

# View test output including:
# ✅ ML prediction functionality
# ✅ Patient PDF generation (without AI)
# ✅ Professional PDF generation (with AI)
# ✅ ML model status verification
```
