# 🦷 OralSmart

OralSmart is a Django web application that allows users to register patients, screen for dental/dietary conditions, and predict oral health risk using machine learning.

## 🚀 Features

- Patient Registration
- Dental Screening
- Dietary Screening
- **AI-Powered Risk Assessment** (3-class: Low/Medium/High)
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
