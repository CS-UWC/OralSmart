# ML Model Training Data Export - 3-Class Risk Prediction

This document explains how to use the `export_training_data` management command to export your database records to CSV format suitable for training the ML model with 3-class risk prediction (low/medium/high).

## Command Overview

The `export_training_data` command extracts patient assessment data from the database and converts it into a CSV file that can be used to train the ML risk prediction model. The system now supports **3-class classification**:

- **Low Risk**: Patients with minimal risk factors
- **Medium Risk**: Patients with moderate risk requiring monitoring  
- **High Risk**: Patients requiring immediate intervention

## Basic Usage

```bash
# Export all complete records (both dental and dietary data)
python manage.py export_training_data

# Export to a specific file
python manage.py export_training_data --output my_training_data.csv

# Export to a specific directory
python manage.py export_training_data --path /path/to/output --output training_data.csv

# Include incomplete records (only dental OR dietary data)
python manage.py export_training_data --include-incomplete

# See statistics without creating file
python manage.py export_training_data --dry-run
```

## Command Options

### Basic Options

- `--output FILENAME`: Output CSV file name (default: `training_data.csv`)
- `--path DIRECTORY`: Output directory path (default: project root)
- `--dry-run`: Show statistics without creating the file

### Data Selection Options

- `--include-incomplete`: Include records with only dental or only dietary data
- `--min-dmft NUMBER`: Minimum DMFT score for high risk classification (default: 8)
- `--risk-threshold NUMBER`: Custom high-risk threshold for 3-class classification (medium threshold is automatically set to 65% of this value)

### Examples

```bash
# Basic export with default settings
python manage.py export_training_data

# Export including incomplete records
python manage.py export_training_data --include-incomplete --output complete_dataset.csv

# Get balanced 3-class distribution with custom threshold
python manage.py export_training_data --risk-threshold 15 --output balanced_3class_data.csv

# Check data quality before export
python manage.py export_training_data --dry-run --include-incomplete

# Check risk distribution without exporting
python manage.py export_training_data --dry-run --risk-threshold 15
```

## 3-Class Risk Classification System

The system uses a sophisticated scoring algorithm to classify patients into three risk categories:

### Risk Calculation Method
- **Composite Risk Score**: Combines clinical findings, dietary habits, protective factors, and DMFT scores
- **Dual Thresholds**: High threshold and medium threshold (65% of high threshold)
- **Adaptive Thresholds**: Automatically adjusts based on data availability

### Risk Categories
- **Low Risk (0)**: Score below medium threshold - minimal intervention needed
- **Medium Risk (1)**: Score between medium and high thresholds - monitoring and preventive care
- **High Risk (2)**: Score above high threshold - immediate intervention required

### Default Thresholds
- Complete data (both assessments): High=8, Medium=5.2
- Partial data (one assessment): High=6, Medium=3.9  
- Custom threshold recommended: 15 for balanced distribution

### Optimal Training Distribution
With `--risk-threshold 15`:
- Low Risk: 18.3% (1,282 patients)
- Medium Risk: 39.7% (2,778 patients)
- High Risk: 42.0% (2,946 patients)

### Choosing the Right Threshold

The risk threshold determines how strict your risk classification will be. Here's how to choose:

#### 🎯 **By Use Case:**
- **Clinical Practice**: Threshold 8-12 (balanced sensitivity/specificity)
- **ML Model Training**: Threshold 15 (optimal class balance)
- **Preventive Screening**: Threshold 6-8 (catch more potential cases)
- **Resource Allocation**: Threshold 18-20 (focus on clear high-risk patients)

#### 📊 **Expected Distributions:**
- **Threshold 6**: ~70-80% high risk (very conservative)
- **Threshold 8**: ~50-60% high risk (standard clinical)
- **Threshold 15**: ~35-45% high risk (balanced for ML)
- **Threshold 20**: ~15-25% high risk (strict)

#### 🧪 **Testing Process:**
1. Generate test data: `PatientWithAssessmentsFactory.create_batch(1000)`
2. Test thresholds: `python manage.py export_training_data --dry-run --risk-threshold 15`
3. Look for ideal distribution: 15-25% low, 35-45% medium, 35-45% high
4. Export and train with your chosen threshold

#### 💡 **Quick Recommendation:**
For most users, **threshold 15** provides the best balance for ML training and clinical relevance.

## Output Format

The generated CSV will include:

### Feature Columns (68 total)
1. **Dental Assessment Features (19 fields)**:
   - Demographics: `sa_citizen`, `special_needs`, `caregiver_treatment`
   - Clinical: `appliance`, `plaque`, `dry_mouth`, `enamel_defects`
   - Protective: `fluoride_water`, `fluoride_toothpaste`, `topical_fluoride`, `regular_checkups`
   - Disease indicators: `sealed_pits`, `restorative_procedures`, `enamel_change`, `dentin_discoloration`, `white_spot_lesions`, `cavitated_lesions`, `multiple_restorations`, `missing_teeth`

2. **DMFT Score**: `total_dmft_score` (calculated from teeth data)

3. **Dietary Assessment Features (33 fields)**:
   - Sweet/sugary foods: `sweet_sugary_foods`, `sweet_sugary_foods_daily`, `sweet_sugary_foods_weekly`, `sweet_sugary_foods_timing`, `sweet_sugary_foods_bedtime`
   - Takeaways: `takeaways_processed_foods`, `takeaways_processed_foods_daily`, `takeaways_processed_foods_weekly`
   - Fresh fruit: `fresh_fruit`, `fresh_fruit_daily`, `fresh_fruit_weekly`, `fresh_fruit_timing`, `fresh_fruit_bedtime`
   - Cold drinks: `cold_drinks_juices`, `cold_drinks_juices_daily`, `cold_drinks_juices_weekly`, `cold_drinks_juices_timing`, `cold_drinks_juices_bedtime`
   - Processed fruit: `processed_fruit`, `processed_fruit_daily`, `processed_fruit_weekly`, `processed_fruit_timing`, `processed_fruit_bedtime`
   - Spreads: `spreads`, `spreads_daily`, `spreads_weekly`, `spreads_timing`, `spreads_bedtime`
   - Added sugars: `added_sugars`, `added_sugars_daily`, `added_sugars_weekly`, `added_sugars_timing`, `added_sugars_bedtime`
   - Salty snacks: `salty_snacks`, `salty_snacks_daily`, `salty_snacks_weekly`, `salty_snacks_timing`
   - Dairy: `dairy_products`, `dairy_products_daily`, `dairy_products_weekly`
   - Vegetables: `vegetables`, `vegetables_daily`, `vegetables_weekly`
   - Water: `water`, `water_timing`, `water_glasses`

4. **Data Availability Indicators (2 fields)**:
   - `has_dental_data`: Whether dental assessment data is available
   - `has_dietary_data`: Whether dietary assessment data is available

5. **Target Variable**:
   - `risk_level`: 'high' or 'low' (calculated based on assessment data)

## Risk Level Calculation

The command calculates risk levels using a sophisticated scoring system:

### High Risk Factors (increase score):
- **DMFT Score**: Each point adds 0.5 to risk score. Score ≥8 = immediate high risk
- **Clinical Findings**: plaque, dry mouth, enamel defects, lesions, etc. (+2 each)
- **Dietary Risk**: frequent sugary foods/drinks, bedtime consumption (+1 each)
- **High Frequency**: 3+ times daily/weekly consumption (+1 each)
- **Social Factors**: special needs (+2), no caregiver treatment (+1)

### Protective Factors (decrease score):
- **Fluoride Exposure**: fluoridated water, toothpaste, topical fluoride (-1 each)
- **Professional Care**: regular checkups, sealants (-1 each)

### Risk Thresholds:
- **Complete Data** (both assessments): threshold = 8
- **Partial Data** (one assessment): threshold = 6 (more sensitive)
- **Custom Thresholds**: Use `--risk-threshold` to override

## Data Quality Checks

The command provides statistics including:
- Total patients in database
- Patients with complete vs. partial data
- Risk distribution (high vs. low)
- Warnings for imbalanced datasets

### Sample Output:
```
==================================================
EXPORT STATISTICS
==================================================
Total patients: 7098
With both assessments: 7006
With dental only: 19
With dietary only: 12
With no assessments: 61
Records for training: 7006
High risk: 2946 (42%)
Low risk: 4060 (58%)

Training data exported to: balanced_training_data.csv
Features: 68
Records: 7006
```

### Training Results with 3-Class Exported Data:
```
==================================================
TRAINING RESULTS - 3-CLASS CLASSIFICATION
==================================================
Training Accuracy: 0.9920
Test Accuracy: 0.9301
Training Samples: 5604
Test Samples: 1402
Features Used: 68
Model Type: MLPClassifier
Iterations: 39
Final Loss: 0.002619

Classification Report:
              precision    recall  f1-score   support
           0       0.93      0.91      0.92       257  (Low Risk)
           1       0.92      0.90      0.91       556  (Medium Risk)
           2       0.94      0.96      0.95       589  (High Risk)
    accuracy                           0.93      1402
   macro avg       0.93      0.93      0.93      1402
weighted avg       0.93      0.93      0.93      1402

Confusion Matrix:
     Low  Med  High
Low  [234, 23, 0]    # Low risk correctly identified 91% of time
Med  [17, 502, 37]   # Medium risk correctly identified 90% of time  
High [0, 21, 568]    # High risk correctly identified 96% of time

Risk Distribution in Training Data:
- Low Risk: 1,282 patients (18.3%)
- Medium Risk: 2,778 patients (39.7%) 
- High Risk: 2,946 patients (42.0%)
```

## Using the Exported Data

Once you have the CSV file, you can train the 3-class model:

```bash
# Train the model with your exported 3-class data
from ml_models.ml_predictor import MLPRiskPredictor
predictor = MLPRiskPredictor()
results = predictor.train_from_csv('balanced_3class_data.csv', target_column='risk_level')
```

### Recommended Workflow for 3-Class Training

1. **Export balanced training data**:
```bash
python manage.py export_training_data --risk-threshold 15 --output balanced_3class_data.csv
```

2. **Train the 3-class model**:
```python
from ml_models.ml_predictor import MLPRiskPredictor
predictor = MLPRiskPredictor()
results = predictor.train_from_csv('balanced_3class_data.csv')
print(f"Test Accuracy: {results['test_accuracy']:.4f}")
```

3. **Make predictions with 3 risk levels**:
```python
# The model now returns low/medium/high instead of just low/high
result = predictor.predict_risk(dental_data, dietary_data)
print(f"Risk Level: {result['risk_level']}")  # 'low', 'medium', or 'high'
print(f"Probabilities:")
print(f"  Low: {result['probability_low_risk']:.3f}")
print(f"  Medium: {result['probability_medium_risk']:.3f}")  
print(f"  High: {result['probability_high_risk']:.3f}")
```

### Quick Training Test Script
```python
#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oralsmart.settings')
django.setup()

from ml_models.ml_predictor import MLPRiskPredictor

# Load and train
predictor = MLPRiskPredictor()
results = predictor.train_from_csv('balanced_training_data.csv')

# Show results
print(f"Test Accuracy: {results['test_accuracy']:.4f}")
print(f"Training Samples: {results['train_samples']}")
print(f"Features Used: {results['features_used']}")
print("Classification Report:")
print(results['classification_report'])
```

## Best Practices

1. **Check Data Quality**: Always run `--dry-run` first to check statistics
2. **Balanced Dataset**: Aim for 20-80% high risk ratio. Use `--risk-threshold 15` for good balance
3. **Complete Data**: Use complete records when possible for better model performance
4. **Regular Updates**: Re-export and retrain as you collect more patient data
5. **Backup**: Keep previous training datasets for comparison

### Recommended Commands for Different Scenarios

```bash
# Balanced dataset (recommended for most cases)
python manage.py export_training_data --risk-threshold 15 --output balanced_training_data.csv

# Conservative approach (more high-risk predictions)
python manage.py export_training_data --risk-threshold 12 --output conservative_training_data.csv

# Liberal approach (fewer high-risk predictions)
python manage.py export_training_data --risk-threshold 18 --output liberal_training_data.csv

# Maximum data (includes incomplete records)
python manage.py export_training_data --include-incomplete --risk-threshold 15 --output max_training_data.csv
```

## Troubleshooting

### No Records Found
- Check if patients have assessment data
- Use `--include-incomplete` to include partial records
- Verify database connection

### Imbalanced Dataset
- Adjust `--min-dmft` or `--risk-threshold` parameters
- Collect more diverse patient data
- Consider data augmentation techniques

### Low Data Quality
- Ensure assessment forms are completely filled
- Validate data entry processes
- Check for missing teeth_data in dental assessments
