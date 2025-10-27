# ML Model Training Guide

## Quick Start

### Prerequisites
```bash
cd src  # Navigate to Django project directory
```

### Basic Training Commands

#### Recommended for Production
```bash
python manage.py train_ml_model balanced_3class_training_data.csv
```
- Feature selection (Random Forest importance)
- Hyperparameter tuning (GridSearchCV)
- 5-fold cross-validation
- 10-30 minutes

#### Fast Development Mode
```bash
python manage.py train_ml_model balanced_3class_training_data.csv --fast
```
- Feature selection only
- No hyperparameter tuning
- 2-5 minutes

#### Quick Testing
```bash
python manage.py train_ml_model balanced_3class_training_data.csv --baseline
```
- No enhancements
- 1-2 minutes

## Advanced Options

### Feature Selection Methods
```bash
# Random Forest importance (default)
python manage.py train_ml_model data.csv --feature-selection-method importance --n-features 40

# ANOVA F-statistic
python manage.py train_ml_model data.csv --feature-selection-method kbest --n-features 30

# Recursive Feature Elimination
python manage.py train_ml_model data.csv --feature-selection-method rfe --n-features 35
```

### Disable Specific Features
```bash
# Disable hyperparameter tuning only
python manage.py train_ml_model data.csv --no-hyperparameter-tuning

# Disable feature selection only
python manage.py train_ml_model data.csv --no-feature-selection
```

## Additional Commands

### Export Training Data
```bash
python manage.py export_training_data --output my_data.csv
```

### Test AI Integration
```bash
python manage.py test_ai_integration
```

### Get Help
```bash
python manage.py train_ml_model --help
```

## Performance Expectations

| Mode | Time | Accuracy | Features | Use Case |
|------|------|----------|----------|----------|
| Full | 10-30 min | ~87% | 40/68 | Production |
| Fast | 2-5 min | ~87% | 30/68 | Development |
| Baseline | 1-2 min | ~87% | All | Testing |

## Model Features

- **Neural Network**: MLPClassifier with optimized hyperparameters
- **Feature Selection**: Reduces 68 features to 30-40 most important
- **Cross-Validation**: 5-fold stratified validation
- **Hyperparameter Tuning**: GridSearchCV optimization
- **3-Class Prediction**: Low/Medium/High risk levels
