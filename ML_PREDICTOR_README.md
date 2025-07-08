# ML Risk Predictor Documentation

## Overview

The ML Risk Predictor is a machine learning system designed to predict oral health risk levels for patients based on their dental and dietary assessment data. The system uses a Random Forest classifier to make predictions and supports training with external CSV data.

## Features

- **CSV Training**: Train the model using external data from CSV files
- **Risk Prediction**: Predict high/low risk levels for patients
- **Model Persistence**: Save and load trained models
- **Feature Importance**: Identify key risk factors
- **Django Integration**: Full integration with Django web framework
- **Management Commands**: Easy-to-use Django management commands

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. The ML predictor will be automatically available in your Django project.

## Usage

### 1. Training the Model

#### Using Django Management Command

To train the model with a CSV file:
```bash
python manage.py train_ml_model path/to/your/training_data.csv
```

To create sample training data:
```bash
python manage.py train_ml_model sample_data.csv --create-sample --sample-size 1000
```

#### Using Python Code

```python
from ml_models.ml_predictor import MLPRiskPredictor

# Initialize predictor
predictor = MLPRiskPredictor()

# Train from CSV
results = predictor.train_from_csv('training_data.csv', target_column='risk_level')
print(f"Test accuracy: {results['test_accuracy']:.4f}")
```

### 2. Making Predictions

```python
from ml_models.ml_predictor import MLPRiskPredictor

# Initialize predictor
predictor = MLPRiskPredictor()

# Make prediction (assuming you have Django model instances)
prediction = predictor.predict_risk(dental_assessment, dietary_assessment)

print(f"Risk Level: {prediction['risk_level']}")
print(f"Confidence: {prediction['confidence']:.4f}")
print(f"Top Risk Factors: {prediction['top_risk_factors']}")
```

### 3. Using the Web API

#### Predict Risk Level
```bash
curl -X POST http://your-domain/ml/predict-risk/ \
  -H "Content-Type: application/json" \
  -d '{
    "dental_data": {
      "sa_citizen": "yes",
      "special_needs": "no",
      "sugar_meals": "yes",
      "plaque": "yes",
      "income": "1-2500",
      "teeth_data": {"tooth_1": "1", "tooth_2": "0"}
    },
    "dietary_data": {
      "sweet_sugary_foods": "yes",
      "cold_drinks_juices": "yes"
    }
  }'
```

#### Get Model Status
```bash
curl -X GET http://your-domain/ml/model-status/
```

#### Download Training Template
```bash
curl -X GET http://your-domain/ml/training-template/ > training_template.csv
```

## CSV Data Format

The training CSV file should contain the following columns:

### Binary Features (0 or 1)
- `sa_citizen`: South African citizen
- `special_needs`: Has special needs
- `caregiver_treatment`: Caregiver provides treatment
- `sugar_meals`: Sugar in meals
- `sugar_snacks`: Sugar in snacks
- `sugar_beverages`: Sugar in beverages
- `appliance`: Uses dental appliance
- `plaque`: Has plaque
- `dry_mouth`: Has dry mouth
- `enamel_defects`: Has enamel defects
- `fluoride_water`: Uses fluoride water
- `fluoride_toothpaste`: Uses fluoride toothpaste
- `topical_fluoride`: Uses topical fluoride
- `regular_checkups`: Has regular checkups
- `sealed_pits`: Has sealed pits
- `restorative_procedures`: Had restorative procedures
- `enamel_change`: Has enamel changes
- `dentin_discoloration`: Has dentin discoloration
- `white_spot_lesions`: Has white spot lesions
- `cavitated_lesions`: Has cavitated lesions
- `multiple_restorations`: Has multiple restorations
- `missing_teeth`: Has missing teeth
- `sweet_sugary_foods`: Consumes sweet/sugary foods
- `cold_drinks_juices`: Consumes cold drinks/juices
- `takeaways_processed_foods`: Consumes takeaways/processed foods
- `salty_snacks`: Consumes salty snacks
- `spreads`: Consumes spreads

### Income Categories (One-hot encoded, only one should be 1)
- `income_0`: Income = 0
- `income_1_2500`: Income = 1-2500
- `income_2501_5000`: Income = 2501-5000
- `income_5000_10000`: Income = 5000-10000
- `income_10001_20000`: Income = 10001-20000
- `income_20001_40000`: Income = 20001-40000
- `income_40001_70000`: Income = 40001-70000
- `income_70001_plus`: Income = 70001+

### Numerical Features
- `total_dmft_score`: DMFT (Decayed, Missing, Filled Teeth) score (0-32)

### Target Variable
- `risk_level`: 'high' or 'low'

## Model Architecture

- **Algorithm**: Multi-Layer Perceptron (MLP) Neural Network
- **Hidden Layers**: 3 layers with 64, 32, and 16 neurons respectively
- **Activation**: ReLU activation function
- **Optimizer**: Adam optimizer
- **Regularization**: L2 regularization (alpha=0.001)
- **Features**: 35 features (binary, categorical, numerical)
- **Preprocessing**: StandardScaler for feature normalization (crucial for neural networks)
- **Target**: Binary classification (high/low risk)
- **Early Stopping**: Prevents overfitting with patience of 10 iterations

## Performance Metrics

The model provides the following metrics:
- **Accuracy**: Overall prediction accuracy
- **Precision/Recall**: Per-class performance
- **Confusion Matrix**: Detailed classification results
- **Feature Importance**: Most influential features for predictions

## File Structure

```
ml_models/
├── __init__.py
├── admin.py
├── apps.py
├── ml_predictor.py          # Main ML predictor class
├── models1.py               # Django models (if needed)
├── views.py                 # Django views for API endpoints
├── tests.py                 # Unit tests
├── management/
│   └── commands/
│       └── train_ml_model.py  # Django management command
├── saved_models/            # Directory for saved models
│   ├── risk_predictor.pkl   # Trained model
│   └── scaler.pkl          # Feature scaler
└── migrations/
```

## Error Handling

The system includes comprehensive error handling:
- **Data Validation**: Checks for required features and data types
- **Model Loading**: Graceful handling of missing model files
- **Prediction Errors**: Informative error messages for failed predictions
- **Training Errors**: Detailed error reporting for training issues

## Best Practices

1. **Data Quality**: Ensure your training data is clean and representative
2. **Feature Consistency**: Use the same feature names and formats
3. **Model Validation**: Regularly validate model performance with new data
4. **Retraining**: Retrain the model periodically with new data
5. **Monitoring**: Monitor prediction accuracy and model performance

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **Model Not Found**: Train the model first using the management command
3. **CSV Format Errors**: Check that your CSV has all required columns
4. **Permission Errors**: Ensure Django has write permissions to save models

### Logging

The system uses Python's logging module. Check your Django logs for detailed error messages:
```python
import logging
logger = logging.getLogger(__name__)
```

## Examples

See `ml_usage_example.py` for complete usage examples and `training_data_template.csv` for sample data format.

## Future Enhancements

- Online learning capabilities
- Support for additional ML algorithms
- Advanced feature engineering
- Real-time model monitoring
- A/B testing framework
- Model versioning and rollback
