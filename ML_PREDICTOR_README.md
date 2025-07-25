# ML Risk Predictor Documentation

## Overview

The ML Risk Predictor is a machine learning system designed to predict oral health risk levels for patients based on their dental and dietary assessment data. The system uses a Multi-Layer Perceptron (MLP) Neural Network to make predictions and supports training with external CSV data.

## Features

- **CSV Training**: Train the model using external data from CSV files
- **Risk Prediction**: Predict low/medium/high risk levels for patients
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

**Note**: All API endpoints require user authentication (login).

#### Predict Risk Level
```bash
curl -X POST http://your-domain/ml/predict-risk/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=your-session-id" \
  -d '{
    "dental_data": {
      "sa_citizen": "yes",
      "special_needs": "no",
      "caregiver_treatment": "no",
      "appliance": "yes",
      "plaque": "yes",
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
curl -X GET http://your-domain/ml/model-status/ \
  -H "Cookie: sessionid=your-session-id"
```

#### Download Training Template
```bash
curl -X GET http://your-domain/ml/training-template/ \
  -H "Cookie: sessionid=your-session-id" > training_template.csv
```

## CSV Data Format

The training CSV file should contain the following **68 columns**:

### Dental Assessment Features (20 features)

#### Demographics and General (3 features)
- `sa_citizen`: South African citizen (0/1)
- `special_needs`: Has special needs (0/1)
- `caregiver_treatment`: Caregiver provides treatment (0/1)

#### Oral Health Status (4 features)
- `appliance`: Uses dental appliance (0/1)
- `plaque`: Has plaque (0/1)
- `dry_mouth`: Has dry mouth (0/1)
- `enamel_defects`: Has enamel defects (0/1)

#### Fluoride Exposure (4 features)
- `fluoride_water`: Uses fluoride water (0/1)
- `fluoride_toothpaste`: Uses fluoride toothpaste (0/1)
- `topical_fluoride`: Uses topical fluoride (0/1)
- `regular_checkups`: Has regular checkups (0/1)

#### Clinical Findings (8 features)
- `sealed_pits`: Has sealed pits (0/1)
- `restorative_procedures`: Had restorative procedures (0/1)
- `enamel_change`: Has enamel changes (0/1)
- `dentin_discoloration`: Has dentin discoloration (0/1)
- `white_spot_lesions`: Has white spot lesions (0/1)
- `cavitated_lesions`: Has cavitated lesions (0/1)
- `multiple_restorations`: Has multiple restorations (0/1)
- `missing_teeth`: Has missing teeth (0/1)

#### DMFT Score (1 feature)
- `total_dmft_score`: DMFT (Decayed, Missing, Filled Teeth) score (0-32)

### Dietary Assessment Features (46 features)

#### Sweet/Sugary Foods (5 features)
- `sweet_sugary_foods`: Consumes sweet/sugary foods (0/1)
- `sweet_sugary_foods_daily`: Daily frequency (numerical)
- `sweet_sugary_foods_weekly`: Weekly frequency (numerical)
- `sweet_sugary_foods_timing`: Timing information (numerical)
- `sweet_sugary_foods_bedtime`: Consumes at bedtime (0/1)

#### Takeaways/Processed Foods (3 features)
- `takeaways_processed_foods`: Consumes takeaways/processed foods (0/1)
- `takeaways_processed_foods_daily`: Daily frequency (numerical)
- `takeaways_processed_foods_weekly`: Weekly frequency (numerical)

#### Fresh Fruit (5 features)
- `fresh_fruit`: Consumes fresh fruit (0/1)
- `fresh_fruit_daily`: Daily frequency (numerical)
- `fresh_fruit_weekly`: Weekly frequency (numerical)
- `fresh_fruit_timing`: Timing information (numerical)
- `fresh_fruit_bedtime`: Consumes at bedtime (0/1)

#### Cold Drinks/Juices (5 features)
- `cold_drinks_juices`: Consumes cold drinks/juices (0/1)
- `cold_drinks_juices_daily`: Daily frequency (numerical)
- `cold_drinks_juices_weekly`: Weekly frequency (numerical)
- `cold_drinks_juices_timing`: Timing information (numerical)
- `cold_drinks_juices_bedtime`: Consumes at bedtime (0/1)

#### Processed Fruit (5 features)
- `processed_fruit`: Consumes processed fruit (0/1)
- `processed_fruit_daily`: Daily frequency (numerical)
- `processed_fruit_weekly`: Weekly frequency (numerical)
- `processed_fruit_timing`: Timing information (numerical)
- `processed_fruit_bedtime`: Consumes at bedtime (0/1)

#### Spreads (5 features)
- `spreads`: Consumes spreads (0/1)
- `spreads_daily`: Daily frequency (numerical)
- `spreads_weekly`: Weekly frequency (numerical)
- `spreads_timing`: Timing information (numerical)
- `spreads_bedtime`: Consumes at bedtime (0/1)

#### Added Sugars (5 features)
- `added_sugars`: Consumes added sugars (0/1)
- `added_sugars_daily`: Daily frequency (numerical)
- `added_sugars_weekly`: Weekly frequency (numerical)
- `added_sugars_timing`: Timing information (numerical)
- `added_sugars_bedtime`: Consumes at bedtime (0/1)

#### Salty Snacks (4 features)
- `salty_snacks`: Consumes salty snacks (0/1)
- `salty_snacks_daily`: Daily frequency (numerical)
- `salty_snacks_weekly`: Weekly frequency (numerical)
- `salty_snacks_timing`: Timing information (numerical)

#### Dairy Products (3 features)
- `dairy_products`: Consumes dairy products (0/1)
- `dairy_products_daily`: Daily frequency (numerical)
- `dairy_products_weekly`: Weekly frequency (numerical)

#### Vegetables (3 features)
- `vegetables`: Consumes vegetables (0/1)
- `vegetables_daily`: Daily frequency (numerical)
- `vegetables_weekly`: Weekly frequency (numerical)

#### Water (3 features)
- `water`: Drinks water (0/1)
- `water_timing`: Timing information (numerical)
- `water_glasses`: Number of glasses (numerical)

### Data Availability Indicators (2 features)
- `has_dental_data`: Whether dental data is available (0/1)
- `has_dietary_data`: Whether dietary data is available (0/1)

### Target Variable
- `risk_level`: 'low', 'medium', or 'high' (3-class classification)

## Model Architecture

- **Algorithm**: Multi-Layer Perceptron (MLP) Neural Network
- **Hidden Layers**: 3 layers with 64, 32, and 16 neurons respectively
- **Activation**: ReLU activation function
- **Optimizer**: Adam optimizer
- **Regularization**: L2 regularization (alpha=0.001)
- **Features**: 68 features (20 dental + 46 dietary + 2 availability indicators)
- **Preprocessing**: StandardScaler for feature normalization (crucial for neural networks)
- **Target**: 3-class classification (low/medium/high risk)
- **Early Stopping**: Prevents overfitting with patience of 10 iterations

## Performance Metrics

The model provides the following metrics:
- **Accuracy**: Overall prediction accuracy
- **Precision/Recall**: Per-class performance
- **Confusion Matrix**: Detailed classification results
- **Feature Analysis**: Identify patterns and important features through model interpretation techniques

## File Structure

```
ml_models/
├── __init__.py
├── admin.py
├── apps.py
├── ml_predictor.py          # Main ML predictor class
├── models.py                # Django models
├── views.py                 # Django views for API endpoints
├── urls.py                  # URL routing for API endpoints
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

See `ml_usage_example.py` for complete usage examples. Training templates can be downloaded via the web API.

## Future Enhancements

- Online learning capabilities
- Support for additional ML algorithms
- Advanced feature engineering
- Real-time model monitoring
- A/B testing framework
- Model versioning and rollback
