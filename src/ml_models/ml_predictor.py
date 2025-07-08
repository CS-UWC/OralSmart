import numpy as np
import pandas as pd
import pickle
import os
import logging
from typing import Optional, Dict, Any, Tuple
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from django.db import models
from django.conf import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLPRiskPredictor:
    """
    Multi-Layer Perceptron (MLP) Neural Network for oral health risk prediction.
    
    This class implements a neural network model that predicts risk levels (high/low) 
    based on dental assessment data, dietary information, and patient demographics.
    """
    def __init__(self) -> None:
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'saved_models', 'risk_predictor.pkl')
        self.scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'saved_models', 'scaler.pkl')
        self.feature_names = [
            'sa_citizen', 'special_needs', 'caregiver_treatment',
            'sugar_meals', 'sugar_snacks', 'sugar_beverages',
            'appliance', 'plaque', 'dry_mouth', 'enamel_defects',
            'fluoride_water', 'fluoride_toothpaste', 'topical_fluoride',
            'regular_checkups', 'sealed_pits', 'restorative_procedures',
            'enamel_change', 'dentin_discoloration', 'white_spot_lesions',
            'cavitated_lesions', 'multiple_restorations', 'missing_teeth',
            'income_0', 'income_1_2500', 'income_2501_5000',
            'income_5000_10000', 'income_10001_20000', 'income_20001_40000',
            'income_40001_70000', 'income_70001_plus',
            'sweet_sugary_foods', 'cold_drinks_juices',
            'takeaways_processed_foods', 'salty_snacks', 'spreads',
            'total_dmft_score'
        ]
        
        # Try to load existing model
        self.load_model()

    def prepare_features(self, dental_data, dietary_data=None):
        """
        Prepare features from dental and dietary data for ML prediction.
        
        Args:
            dental_data: Object containing dental assessment data
            dietary_data: Optional object containing dietary assessment data
            
        Returns:
            numpy array: Feature vector ready for model prediction
        """
        try:
            features = {}

            # Yes/No → binary
            binary_fields = [
                'sa_citizen', 'special_needs', 'caregiver_treatment',
                'sugar_meals', 'sugar_snacks', 'sugar_beverages',
                'appliance', 'plaque', 'dry_mouth', 'enamel_defects',
                'fluoride_water', 'fluoride_toothpaste', 'topical_fluoride',
                'regular_checkups', 'sealed_pits', 'restorative_procedures',
                'enamel_change', 'dentin_discoloration', 'white_spot_lesions',
                'cavitated_lesions', 'multiple_restorations', 'missing_teeth'
            ]

            for field in binary_fields:
                value = getattr(dental_data, field, 'no')
                features[field] = 1 if value == 'yes' else 0

            # Income one-hot encoding
            income_categories = ['0', '1-2500', '2501-5000', '5000-10000',
                               '10001-20000', '20001-40000', '40001-70000', '70001+']
            for cat in income_categories:
                key = f"income_{cat.replace('-', '_').replace('+', '_plus')}"
                features[key] = 1 if dental_data.income == cat else 0

            # DMFT score
            features['total_dmft_score'] = self.calculate_dmft_score(dental_data.teeth_data)

            # Dietary fields (optional)
            if dietary_data:
                for field in ['sweet_sugary_foods', 'cold_drinks_juices',
                            'takeaways_processed_foods', 'salty_snacks', 'spreads']:
                    value = getattr(dietary_data, field, 'no')
                    features[field] = 1 if value == 'yes' else 0
            else:
                for field in ['sweet_sugary_foods', 'cold_drinks_juices',
                            'takeaways_processed_foods', 'salty_snacks', 'spreads']:
                    features[field] = 0

            # Convert to vector
            return np.array([features.get(f, 0) for f in self.feature_names]).reshape(1, -1)
        
        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            raise ValueError(f"Failed to prepare features: {str(e)}")

    def calculate_dmft_score(self, teeth_data):
        """
        Calculate DMFT (Decayed, Missing, Filled Teeth) score.
        
        Args:
            teeth_data: Dictionary containing teeth status data
            
        Returns:
            int: DMFT score
        """
        try:
            score = 0
            if not teeth_data:
                return 0

            for tooth, status in teeth_data.items():
                if status in ['1', 'B']:  # Decayed
                    score += 1
                elif status in ['2', 'C']:  # Filled
                    score += 1
                elif status in ['3', '4', 'D', 'E']:  # Missing
                    score += 1

            return score
        
        except Exception as e:
            logger.error(f"Error calculating DMFT score: {str(e)}")
            return 0

    def train_from_csv(self, csv_file_path: str, target_column: str = 'risk_level') -> Dict[str, Any]:
        """
        Train the model using data from a CSV file.
        
        Args:
            csv_file_path: Path to the CSV file containing training data
            target_column: Name of the column containing the target variable (risk levels)
            
        Returns:
            Dict containing training metrics and model information
        """
        try:
            logger.info(f"Loading training data from {csv_file_path}")
            
            # Load data
            df = pd.read_csv(csv_file_path)
            
            # Validate required columns
            missing_features = set(self.feature_names) - set(df.columns)
            if missing_features:
                logger.warning(f"Missing features in CSV: {missing_features}")
            
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found in CSV")
            
            # Prepare features and target
            X = df[self.feature_names].fillna(0)  # Fill missing values with 0
            y = df[target_column]
            
            # Convert target to binary if needed (high risk = 1, low risk = 0)
            if y.dtype == 'object':
                y = y.map({'high': 1, 'low': 0, 'High': 1, 'Low': 0})
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features (crucial for neural networks)
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train MLP model
            self.model = MLPClassifier(
                hidden_layer_sizes=(64, 32, 16),  # 3 hidden layers
                activation='relu',                 # ReLU activation
                solver='adam',                     # Adam optimizer
                alpha=0.001,                      # L2 regularization
                batch_size='auto',                # Automatic batch size
                learning_rate='adaptive',         # Adaptive learning rate
                max_iter=1000,                    # Maximum iterations
                random_state=42,                  # Reproducibility
                early_stopping=True,              # Early stopping
                validation_fraction=0.1,          # Validation set size
                n_iter_no_change=10              # Patience for early stopping
            )
            
            logger.info("Training MLP model...")
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_pred = self.model.predict(X_train_scaled)
            test_pred = self.model.predict(X_test_scaled)
            
            train_accuracy = accuracy_score(y_train, train_pred)
            test_accuracy = accuracy_score(y_test, test_pred)
            
            # Save model
            self.save_model()
            self.is_trained = True
            
            results = {
                'train_accuracy': train_accuracy,
                'test_accuracy': test_accuracy,
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'features_used': len(self.feature_names),
                'classification_report': classification_report(y_test, test_pred),
                'confusion_matrix': confusion_matrix(y_test, test_pred).tolist(),
                'model_type': 'MLPClassifier',
                'iterations': self.model.n_iter_,
                'loss': self.model.loss_
            }
            
            logger.info(f"MLP model trained successfully. Test accuracy: {test_accuracy:.4f}")
            logger.info(f"Training completed in {self.model.n_iter_} iterations")
            return results
            
        except Exception as e:
            logger.error(f"Error training model from CSV: {str(e)}")
            raise ValueError(f"Failed to train model: {str(e)}")
    
    def predict_risk(self, dental_data, dietary_data=None) -> Dict[str, Any]:
        """
        Predict risk level for given patient data.
        
        Args:
            dental_data: Object containing dental assessment data
            dietary_data: Optional object containing dietary assessment data
            
        Returns:
            Dict containing prediction results
        """
        try:
            if not self.is_trained or self.model is None:
                raise ValueError("Model is not trained. Please train the model first.")
            
            # Prepare features
            features = self.prepare_features(dental_data, dietary_data)
            
            # Scale features
            if self.scaler is None:
                raise ValueError("Scaler not available. Please retrain the model.")
            
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            prediction_proba = self.model.predict_proba(features_scaled)[0]
            
            # Get feature importance (different approaches for different models)
            feature_importance = {}
            top_features = []
            
            # Check model type and use appropriate method
            model_type = self.model.__class__.__name__
            
            if model_type == 'MLPClassifier':
                # MLP: Use first layer weights as proxy for feature importance
                try:
                    # Use getattr to safely access coefs_ attribute
                    coefs = getattr(self.model, 'coefs_', None)
                    if coefs is not None and len(coefs) > 0:
                        # Get weights from input layer to first hidden layer
                        first_layer_weights = coefs[0]
                        # Calculate mean absolute weight for each feature
                        feature_importance_scores = np.mean(np.abs(first_layer_weights), axis=1)
                        feature_importance = dict(zip(self.feature_names, feature_importance_scores))
                        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
                        logger.info("Using first layer weights as feature importance proxy")
                    else:
                        top_features = [("Feature importance not available", 0.0)]
                except Exception as e:
                    logger.warning(f"Could not calculate feature importance proxy: {str(e)}")
                    top_features = [("Feature importance calculation failed", 0.0)]
            
            else:
                # Other models
                logger.info("Model type doesn't provide feature importance scores")
                top_features = [("Feature importance not available for this model type", 0.0)]
            
            result = {
                'risk_level': 'high' if prediction == 1 else 'low',
                'confidence': float(max(prediction_proba)),
                'probability_high_risk': float(prediction_proba[1] if len(prediction_proba) > 1 else 0),
                'probability_low_risk': float(prediction_proba[0]),
                'top_risk_factors': top_features
            }
            
            logger.info(f"Prediction made: {result['risk_level']} risk with {result['confidence']:.4f} confidence")
            return result
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise ValueError(f"Failed to make prediction: {str(e)}")
    
    def save_model(self):
        """Save the trained model and scaler to disk."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            # Save model
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            # Save scaler
            with open(self.scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            logger.info(f"Model saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise ValueError(f"Failed to save model: {str(e)}")
    
    def load_model(self):
        """Load the trained model and scaler from disk."""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                # Load model
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                
                # Load scaler
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                
                self.is_trained = True
                logger.info("Model loaded successfully from disk")
                
            else:
                logger.info("No saved model found. Model needs to be trained.")
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model = None
            self.scaler = None
            self.is_trained = False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        if not self.is_trained:
            return {'status': 'not_trained', 'message': 'Model has not been trained yet.'}
        
        model_type = type(self.model).__name__ if self.model else 'Unknown'
        
        return {
            'status': 'trained',
            'model_type': model_type,
            'feature_count': len(self.feature_names),
            'features': self.feature_names,
            'model_path': self.model_path,
            'scaler_path': self.scaler_path
        }
    
    def retrain_with_new_data(self, new_csv_path: str, target_column: str = 'risk_level') -> Dict[str, Any]:
        """
        Retrain the model with new data while preserving existing knowledge.
        
        Args:
            new_csv_path: Path to CSV file with new training data
            target_column: Name of the target column
            
        Returns:
            Dict containing retraining results
        """
        try:
            logger.info("Retraining model with new data...")
            
            # Load new data
            new_df = pd.read_csv(new_csv_path)
            
            # Validate columns
            if target_column not in new_df.columns:
                raise ValueError(f"Target column '{target_column}' not found in new data")
            
            # Prepare features
            X_new = new_df[self.feature_names].fillna(0)
            y_new = new_df[target_column]
            
            # Convert target to binary if needed
            if y_new.dtype == 'object':
                y_new = y_new.map({'high': 1, 'low': 0, 'High': 1, 'Low': 0})
            
            # If we have an existing model, we can either:
            # 1. Retrain from scratch with combined data
            # 2. Use online learning (if supported by the algorithm)
            
            # For now, we'll retrain from scratch
            return self.train_from_csv(new_csv_path, target_column)
            
        except Exception as e:
            logger.error(f"Error retraining model: {str(e)}")
            raise ValueError(f"Failed to retrain model: {str(e)}")
    
    def create_sample_training_data(self, output_path: str, num_samples: int = 1000):
        """
        Create a sample CSV file with the expected format for training.
        
        Args:
            output_path: Path where to save the sample CSV
            num_samples: Number of sample records to generate
        """
        try:
            import random
            
            # Generate sample data
            data = []
            for _ in range(num_samples):
                record = {}
                
                # Binary features (0 or 1)
                for feature in self.feature_names:
                    if 'income_' in feature:
                        continue  # Handle income separately
                    elif feature == 'total_dmft_score':
                        record[feature] = random.randint(0, 32)  # Max 32 teeth
                    else:
                        record[feature] = random.choice([0, 1])
                
                # Income (one-hot encoded, but only one should be 1)
                income_features = [f for f in self.feature_names if f.startswith('income_')]
                for feature in income_features:
                    record[feature] = 0
                
                # Set one income category to 1
                chosen_income = random.choice(income_features)
                record[chosen_income] = 1
                
                # Add target variable (risk level)
                # Simple rule: high risk if DMFT > 15 or multiple risk factors
                risk_factors = sum([record[f] for f in self.feature_names if f not in income_features and f != 'total_dmft_score'])
                if record['total_dmft_score'] > 15 or risk_factors > 10:
                    record['risk_level'] = 'high'
                else:
                    record['risk_level'] = 'low'
                
                data.append(record)
            
            # Create DataFrame and save
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            
            logger.info(f"Sample training data created at {output_path}")
            logger.info(f"Generated {num_samples} samples with {len(df.columns)} columns")
            
        except Exception as e:
            logger.error(f"Error creating sample data: {str(e)}")
            raise ValueError(f"Failed to create sample data: {str(e)}")
