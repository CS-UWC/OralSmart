#!/usr/bin/env python
"""
Standalone Enhanced ML Model Demo

This script demonstrates the enhanced ML features without Django dependencies.
It uses the existing training data to show:
1. Feature Selection with Random Forest importance
2. Hyperparameter Tuning with GridSearchCV  
3. 5-Fold Cross-Validation
4. Comprehensive validation reporting

Usage:
    python standalone_ml_demo.py
"""

import numpy as np
import pandas as pd
import os
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier

def load_training_data():
    """Load and prepare training data."""
    data_path = os.path.join('src', 'balanced_3class_training_data.csv')
    
    if not os.path.exists(data_path):
        print(f"❌ Training data not found at: {data_path}")
        print("Please make sure the file exists or run:")
        print("python manage.py export_training_data --risk-threshold 15 --output balanced_3class_training_data.csv")
        return None, None, None
    
    print(f"✅ Loading training data from: {data_path}")
    df = pd.read_csv(data_path)
    
    # Prepare features and target
    feature_columns = [col for col in df.columns if col != 'risk_level']
    X = df[feature_columns].fillna(0)
    y = df['risk_level']
    
    # Convert target to numeric if needed
    if y.dtype == 'object':
        y = y.map({'low': 0, 'medium': 1, 'high': 2})
    
    print(f"   Dataset shape: {X.shape}")
    print(f"   Classes: {y.value_counts().to_dict()}")
    
    return X, y, feature_columns

def perform_feature_selection(X, y, feature_names, method='importance', k_features=40):
    """Perform feature selection."""
    print(f"\n🎯 Feature Selection ({method})")
    print("-" * 40)
    
    if method == 'importance':
        # Random Forest importance
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)
        importance_scores = rf.feature_importances_
        
        # Select top k features
        top_indices = np.argsort(importance_scores)[::-1][:k_features]
        selected_features = [feature_names[i] for i in top_indices]
        
        print(f"✅ Selected {k_features} features using Random Forest importance")
        print("Top 10 features:")
        for i, idx in enumerate(top_indices[:10]):
            print(f"  {i+1:2d}. {feature_names[idx]:<30} (Score: {importance_scores[idx]:.4f})")
        
        return X.iloc[:, top_indices], selected_features, importance_scores[top_indices]
    
    elif method == 'kbest':
        # K-best selection
        selector = SelectKBest(score_func=f_classif, k=k_features)
        X_selected = selector.fit_transform(X, y)
        
        selected_mask = selector.get_support()
        selected_features = [feature_names[i] for i, selected in enumerate(selected_mask) if selected]
        scores = selector.scores_
        
        print(f"✅ Selected {k_features} features using K-best ANOVA F-statistic")
        
        # Show top features
        feature_scores = [(feature_names[i], scores[i]) for i, selected in enumerate(selected_mask) if selected]
        feature_scores.sort(key=lambda x: x[1], reverse=True)
        
        print("Top 10 features:")
        for i, (feature, score) in enumerate(feature_scores[:10]):
            print(f"  {i+1:2d}. {feature:<30} (Score: {score:.4f})")
        
        return pd.DataFrame(X_selected), selected_features, scores[selected_mask]
    
    return X, feature_names, None

def perform_hyperparameter_tuning(X, y):
    """Perform hyperparameter tuning."""
    print(f"\n⚙️ Hyperparameter Tuning")
    print("-" * 40)
    
    # Smaller parameter grid for faster execution
    param_grid = {
        'hidden_layer_sizes': [(64, 32), (100, 50), (64, 32, 16)],
        'alpha': [0.001, 0.01],
        'learning_rate_init': [0.001, 0.01],
        'activation': ['relu', 'tanh']
    }
    
    # Base model
    mlp = MLPClassifier(
        solver='adam',
        max_iter=500,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1
    )
    
    # Grid search with 3-fold CV for speed
    print("🔍 Searching for best hyperparameters...")
    grid_search = GridSearchCV(
        estimator=mlp,
        param_grid=param_grid,
        cv=3,  # Reduced for speed
        scoring='accuracy',
        n_jobs=-1,
        verbose=0
    )
    
    grid_search.fit(X, y)
    
    print(f"✅ Best parameters found:")
    for param, value in grid_search.best_params_.items():
        print(f"   {param}: {value}")
    print(f"✅ Best CV score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_, grid_search.best_params_

def perform_cross_validation(model, X, y, cv_folds=5):
    """Perform cross-validation."""
    print(f"\n📊 {cv_folds}-Fold Cross-Validation")
    print("-" * 40)
    
    # Stratified K-fold
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    
    # Perform CV
    cv_scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy')
    
    print(f"✅ Cross-validation results:")
    print(f"   Individual scores: {[f'{score:.4f}' for score in cv_scores]}")
    print(f"   Mean accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    print(f"   Min accuracy: {cv_scores.min():.4f}")
    print(f"   Max accuracy: {cv_scores.max():.4f}")
    
    return {
        'cv_scores': cv_scores.tolist(),
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'cv_min': cv_scores.min(),
        'cv_max': cv_scores.max()
    }

def train_and_evaluate_model(X, y, use_feature_selection=True, use_hyperparameter_tuning=True):
    """Train and evaluate model with enhancements."""
    
    feature_names = X.columns.tolist()
    
    # Feature Selection
    if use_feature_selection:
        X, selected_features, importance_scores = perform_feature_selection(
            X, y, feature_names, method='importance', k_features=40
        )
    else:
        selected_features = feature_names
        importance_scores = None
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Model training
    if use_hyperparameter_tuning:
        model, best_params = perform_hyperparameter_tuning(X_train_scaled, y_train)
    else:
        print(f"\n🤖 Training Default Model")
        print("-" * 40)
        model = MLPClassifier(
            hidden_layer_sizes=(64, 32, 16),
            activation='relu',
            solver='adam',
            alpha=0.001,
            max_iter=500,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        )
        model.fit(X_train_scaled, y_train)
        best_params = None
        print("✅ Model training completed")
    
    # Cross-validation
    cv_results = perform_cross_validation(model, X_train_scaled, y_train)
    
    # Final evaluation
    train_pred = model.predict(X_train_scaled)
    test_pred = model.predict(X_test_scaled)
    
    train_accuracy = accuracy_score(y_train, train_pred)
    test_accuracy = accuracy_score(y_test, test_pred)
    
    # Results summary
    results = {
        'train_accuracy': train_accuracy,
        'test_accuracy': test_accuracy,
        'cv_results': cv_results,
        'best_params': best_params,
        'feature_selection_used': use_feature_selection,
        'hyperparameter_tuning_used': use_hyperparameter_tuning,
        'original_features': len(feature_names),
        'selected_features': len(selected_features) if use_feature_selection else len(feature_names),
        'train_samples': len(X_train),
        'test_samples': len(X_test)
    }
    
    return results, model

def print_validation_summary(results):
    """Print comprehensive validation summary."""
    print(f"\n" + "=" * 60)
    print("MODEL VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"Training Accuracy:     {results['train_accuracy']:.4f}")
    print(f"Test Accuracy:         {results['test_accuracy']:.4f}")
    
    cv = results['cv_results']
    print(f"CV Mean Accuracy:      {cv['cv_mean']:.4f} (+/- {cv['cv_std'] * 2:.4f})")
    print(f"CV Min Accuracy:       {cv['cv_min']:.4f}")
    print(f"CV Max Accuracy:       {cv['cv_max']:.4f}")
    
    print(f"Training Samples:      {results['train_samples']}")
    print(f"Test Samples:          {results['test_samples']}")
    
    if results['feature_selection_used']:
        reduction = (1 - results['selected_features']/results['original_features']) * 100
        print(f"Original Features:     {results['original_features']}")
        print(f"Selected Features:     {results['selected_features']}")
        print(f"Feature Reduction:     {reduction:.1f}%")
    else:
        print(f"Features Used:         {results['selected_features']}")
    
    print(f"Feature Selection:     {'Enabled' if results['feature_selection_used'] else 'Disabled'}")
    print(f"Hyperparameter Tuning: {'Enabled' if results['hyperparameter_tuning_used'] else 'Disabled'}")
    
    if results['best_params']:
        print("Best Parameters:")
        for param, value in results['best_params'].items():
            print(f"  {param}: {value}")
    
    print("=" * 60)

def main():
    """Main function to demonstrate enhanced ML features."""
    print("🚀 Enhanced ML Model Demo")
    print("=" * 60)
    
    # Load data
    X, y, feature_names = load_training_data()
    if X is None:
        return
    
    # Test 1: Full enhancement
    print(f"\n🧪 Test 1: Full Enhancement Training")
    print("=" * 50)
    results1, model1 = train_and_evaluate_model(
        X, y, 
        use_feature_selection=True,
        use_hyperparameter_tuning=True
    )
    print_validation_summary(results1)
    
    # Test 2: Feature selection only
    print(f"\n🧪 Test 2: Feature Selection Only")
    print("=" * 50)
    results2, model2 = train_and_evaluate_model(
        X, y,
        use_feature_selection=True,
        use_hyperparameter_tuning=False
    )
    print_validation_summary(results2)
    
    # Test 3: Traditional training
    print(f"\n🧪 Test 3: Traditional Training (Baseline)")
    print("=" * 50)
    results3, model3 = train_and_evaluate_model(
        X, y,
        use_feature_selection=False,
        use_hyperparameter_tuning=False
    )
    print_validation_summary(results3)
    
    # Comparison
    print(f"\n📈 COMPARISON SUMMARY")
    print("=" * 60)
    print(f"{'Method':<25} {'Test Acc':<10} {'CV Mean':<10} {'Features':<10}")
    print("-" * 60)
    print(f"{'Full Enhancement':<25} {results1['test_accuracy']:<10.4f} {results1['cv_results']['cv_mean']:<10.4f} {results1['selected_features']:<10}")
    print(f"{'Feature Selection':<25} {results2['test_accuracy']:<10.4f} {results2['cv_results']['cv_mean']:<10.4f} {results2['selected_features']:<10}")
    print(f"{'Traditional':<25} {results3['test_accuracy']:<10.4f} {results3['cv_results']['cv_mean']:<10.4f} {results3['selected_features']:<10}")
    
    print(f"\n🎉 Demo Completed Successfully!")
    print("\nEnhanced Features Demonstrated:")
    print("✓ Feature Selection with Random Forest importance")
    print("✓ Hyperparameter Tuning with GridSearchCV")
    print("✓ 5-Fold Cross-Validation")
    print("✓ Comprehensive Validation Reporting")

if __name__ == "__main__":
    main()
