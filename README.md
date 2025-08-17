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

### ⚠️ Data Management - IMPORTANT
To clear patient data safely without deleting users:
```bash
cd src
# RECOMMENDED: Clears patients only, keeps users safe
python manage.py clear_patients
```

### Model Training Commands
```bash
# Navigate to Django project
cd src

# Basic enhanced training (recommended for production)
python manage.py train_ml_model balanced_3class_training_data.csv

# Fast training (feature selection only - for development)
python manage.py train_ml_model balanced_3class_training_data.csv --fast

# Baseline training (no enhancements - for quick testing)
python manage.py train_ml_model balanced_3class_training_data.csv --baseline

# Test AI integration
python manage.py test_ai_integration

# Export training data (UTF-8 encoding)
python manage.py export_training_data

# Export training data without encoding (system default)
python manage.py export_training_data --no-encoding

# Alternative plain CSV export (system default encoding)
python manage.py export_plain_csv output.csv
```

### Advanced ML Training Options
```bash
# Feature selection methods
python manage.py train_ml_model data.csv --feature-selection-method importance --n-features 40
python manage.py train_ml_model data.csv --feature-selection-method kbest --n-features 30
python manage.py train_ml_model data.csv --feature-selection-method rfe --n-features 35

# Disable specific features
python manage.py train_ml_model data.csv --no-hyperparameter-tuning
python manage.py train_ml_model data.csv --no-feature-selection

# Custom output
python manage.py export_training_data --output custom_data.csv

# Get help
python manage.py train_ml_model --help
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

# Generate test patients using Django management command
python manage.py create_patients --count 500

# Interactive mode (prompts for count)
python manage.py create_patients

# Force mode (skip confirmations) - uses mixed assessments by default
python manage.py create_patients --count 100 --force

# Choose assessment pattern
python manage.py create_patients --count 500 --assessment-pattern mixed      # 65% both, 20% dental, 15% dietary
python manage.py create_patients --count 500 --assessment-pattern both       # All patients have both assessments
python manage.py create_patients --count 500 --assessment-pattern dental-only    # All patients have dental only
python manage.py create_patients --count 500 --assessment-pattern dietary-only   # All patients have dietary only

# Or use the standalone script from project root
cd ..
python patient_manager.py --count 500
python patient_manager.py --clean
```

### Data Management & Cleanup Commands

⚠️ **IMPORTANT**: Choose the right command to avoid accidentally deleting users!

```bash
cd src

# 🔴 RECOMMENDED: Clear only patients & assessments (keeps users safe)
python manage.py clear_patients

# Skip confirmation prompt
python manage.py clear_patients --confirm

# 🟡 Alternative: Clear only patient data using create_patients command
python manage.py create_patients --clean-patients

# 🔴 DANGER: Clear ALL data including users (use with extreme caution!)
python manage.py create_patients --clean

# 📊 Check current patient data
python manage.py check_patients

# Skip confirmation for any cleaning command
python manage.py create_patients --clean-patients --force
```

#### Command Comparison
| Command | Deletes Patients | Deletes Assessments | Deletes Users | Use When |
|---------|:----------------:|:------------------:|:-------------:|----------|
| `clear_patients` | ✅ | ✅ | ❌ | **Recommended** - Safe cleanup |
| `create_patients --clean-patients` | ✅ | ✅ | ❌ | Alternative cleanup |
| `create_patients --clean` | ✅ | ✅ | ✅ | **DANGER** - Full reset only |

### Complete ML Training Workflow
```bash
# 1. Generate training data
cd src
python manage.py create_patients --count 1000

# 2. Export data for training
python manage.py export_training_data --output training_data.csv

# 3. Train model with full enhancements
python manage.py train_ml_model training_data.csv

# 4. Test AI integration
python manage.py test_ai_integration

# 5. For production, use the pre-balanced dataset
python manage.py train_ml_model balanced_3class_training_data.csv
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

## 🎯 Complete ML Workflow

### Step 1: Environment Setup
```bash
# Clone and setup
git clone https://github.com/vhutali01/oralsmart.git
cd oralsmart

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup database
cd src
python manage.py migrate
```

### Step 2: Generate Training Data
```bash
# Option A: Use existing balanced dataset (recommended)
# balanced_3class_training_data.csv is already included

# Option B: Generate fresh data
python manage.py create_patients --count 1500 --force
python manage.py export_training_data --output fresh_training_data.csv
```

### Step 3: Train ML Model
```bash
# Production training (best accuracy)
python manage.py train_ml_model balanced_3class_training_data.csv

# Development training (faster)
python manage.py train_ml_model balanced_3class_training_data.csv --fast

# Custom training
python manage.py train_ml_model balanced_3class_training_data.csv \
    --feature-selection-method importance \
    --n-features 35
```

### Step 4: Test & Validate
```bash
# Test AI integration
python manage.py test_ai_integration

# Run test scripts
python test_3class_predictions.py
python test_enhanced_ml_model.py
```

### Step 5: Deploy & Use
```bash
# Start Django server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Access application at http://127.0.0.1:8000
```

## 🚀 Production Deployment Checklist

### Pre-Deployment
- [ ] Train model with full enhancement mode
- [ ] Test AI integration passes
- [ ] Validate model accuracy >85%
- [ ] Test with realistic patient data
- [ ] Verify report generation works

### Model Training for Production
```bash
# 1. Clean existing patient data (keeps users safe)
python manage.py clear_patients --confirm

# 2. Generate large, balanced dataset with mixed assessment patterns
python manage.py create_patients --count 2000 --assessment-pattern mixed --force

# 3. Export training data
python manage.py export_training_data --output production_data.csv

# 4. Train with full enhancements
python manage.py train_ml_model production_data.csv

# 5. Validate results
python manage.py test_ai_integration
```

### Performance Optimization
```bash
# For faster training during development
python manage.py train_ml_model data.csv --fast --n-features 25

# For maximum accuracy in production
python manage.py train_ml_model data.csv \
    --feature-selection-method importance \
    --n-features 40

# For memory-constrained environments
python manage.py train_ml_model data.csv \
    --no-hyperparameter-tuning \
    --n-features 20
```

## 📈 Performance & Features

### ML Model Performance
| Training Mode | Time | Test Accuracy | Features | Use Case |
|---------------|------|---------------|----------|----------|
| **Full Enhancement** | 10-30 min | ~87% | 40/68 | Production |
| **Fast Mode** | 2-5 min | ~87% | 30/68 | Development |
| **Baseline** | 1-2 min | ~87% | All | Quick testing |

### ML Training Features
- **Neural Network**: MLPClassifier with optimized hyperparameters
- **Feature Selection**: 3 methods (Random Forest importance, K-Best, RFE)
- **Hyperparameter Tuning**: Automated GridSearchCV optimization
- **Cross-Validation**: 5-fold stratified validation for robust performance
- **3-Class Prediction**: Low/Medium/High risk levels with confidence scores

### Key Capabilities
- ✅ **3-Class Risk Prediction** with confidence scores
- ✅ **Dual Report System** for patient privacy
- ✅ **Advanced ML Features** (feature selection, hyperparameter tuning)
- ✅ **Factory Data Generation** for realistic test data
- ✅ **Evidence-Based Scoring** following clinical guidelines
- ✅ **Django Integration** with management commands
- ✅ **Cross-Validation** for robust model evaluation

## 📊 ML Training Guide

### Prerequisites
```bash
# Ensure you're in the Django project directory
cd c:\Users\vhuta\dev\oralsmart\src

# Activate virtual environment if needed
..\venv\Scripts\Activate.ps1
```

### Training Modes Explained

#### 🚀 Production Mode (Full Enhancement)
```bash
python manage.py train_ml_model balanced_3class_training_data.csv
```
**Features:**
- ✅ Random Forest feature importance selection
- ✅ GridSearchCV hyperparameter optimization
- ✅ 5-fold cross-validation
- ✅ Comprehensive performance metrics

**Best for:** Final model deployment, maximum accuracy

#### ⚡ Development Mode (Fast)
```bash
python manage.py train_ml_model balanced_3class_training_data.csv --fast
```
**Features:**
- ✅ Feature selection only
- ❌ No hyperparameter tuning (uses defaults)
- ✅ Quick validation

**Best for:** Iterative development, testing changes

#### 🧪 Testing Mode (Baseline)
```bash
python manage.py train_ml_model balanced_3class_training_data.csv --baseline
```
**Features:**
- ❌ No feature selection
- ❌ No hyperparameter tuning
- ✅ Uses all 68 features

**Best for:** Quick testing, baseline comparisons

### Feature Selection Methods

#### Random Forest Importance (Default)
```bash
python manage.py train_ml_model data.csv --feature-selection-method importance --n-features 40
```
- Uses feature importance scores from Random Forest
- Good for dental/medical data
- Recommended for production

#### ANOVA F-Test (K-Best)
```bash
python manage.py train_ml_model data.csv --feature-selection-method kbest --n-features 30
```
- Statistical significance testing
- Fast and reliable
- Good for linear relationships

#### Recursive Feature Elimination (RFE)
```bash
python manage.py train_ml_model data.csv --feature-selection-method rfe --n-features 35
```
- Iterative feature removal
- More thorough but slower
- Best accuracy but longest training time

### Custom Training Options

#### Disable Specific Features
```bash
# Skip hyperparameter tuning (faster training)
python manage.py train_ml_model data.csv --no-hyperparameter-tuning

# Skip feature selection (use all features)
python manage.py train_ml_model data.csv --no-feature-selection

# Combine both for fastest training
python manage.py train_ml_model data.csv --no-hyperparameter-tuning --no-feature-selection
```

#### Custom Feature Count
```bash
# Select fewer features for faster inference
python manage.py train_ml_model data.csv --n-features 20

# Select more features for potentially better accuracy
python manage.py train_ml_model data.csv --n-features 50
```

### Data Management Commands

#### Export Training Data
```bash
# Export current database to CSV
python manage.py export_training_data

# Export to custom filename
python manage.py export_training_data --output my_training_data.csv

# Export and immediately train
python manage.py export_training_data --output fresh_data.csv
python manage.py train_ml_model fresh_data.csv
```

#### Test AI Integration
```bash
# Test the trained model with sample data
python manage.py test_ai_integration

# This command:
# 1. Loads the saved model
# 2. Tests with sample patient data
# 3. Validates prediction pipeline
# 4. Shows performance metrics
```

### Troubleshooting Training Issues

#### Common Problems and Solutions

**Problem:** "No training data found"
```bash
# Solution: Generate or import training data first
python manage.py create_patients --count 500
python manage.py export_training_data
```

**Problem:** "Model training too slow"
```bash
# Solution: Use fast mode or reduce features
python manage.py train_ml_model data.csv --fast
python manage.py train_ml_model data.csv --n-features 20
```

**Problem:** "Low accuracy results"
```bash
# Solution: Use full enhancement mode with more data
python manage.py create_patients --count 2000
python manage.py export_training_data --output large_dataset.csv
python manage.py train_ml_model large_dataset.csv
```

**Problem:** "Memory issues during training"
```bash
# Solution: Use smaller feature sets or batch processing
python manage.py train_ml_model data.csv --n-features 25 --no-hyperparameter-tuning
```

### Expected Training Output

```
🚀 Starting Enhanced ML Training Pipeline
📊 Dataset: balanced_3class_training_data.csv (2000 samples, 68 features)

🔍 Feature Selection (Random Forest Importance)
   → Selected 40 best features (59% of original)
   → Top features: cavitated_lesions, multiple_restorations, white_spot_lesions

🎯 Hyperparameter Tuning (GridSearchCV)
   → Testing 24 parameter combinations
   → Best params: {'hidden_layer_sizes': (100, 50), 'alpha': 0.001}

📈 Cross-Validation Results:
   → Accuracy: 87.3% (±2.1%)
   → Precision: 86.8%
   → Recall: 87.1%
   → F1-Score: 86.9%

💾 Model saved to: ml_models/saved_models/
✅ Training completed successfully in 15.2 minutes
```

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
