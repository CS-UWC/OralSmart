#!/usr/bin/env python
"""
Check DMFT score role in the enhanced ML model
"""
import sys
import os
sys.path.append(os.getcwd())

def check_dmft_in_features():
    """Check if DMFT score is in the current model features"""
    try:
        from ml_models.ml_predictor import MLPRiskPredictor
        
        predictor = MLPRiskPredictor()
        
        print("🦷 DMFT Score Analysis in Enhanced ML Model")
        print("=" * 60)
        
        # Check if model is loaded
        try:
            predictor.load_model()
            print("✅ Model loaded successfully")
        except:
            print("⚠️  No trained model found")
            
        # Show all feature names
        print(f"\n📋 Current Feature Set ({len(predictor.feature_names)} features):")
        print("-" * 40)
        
        dmft_found = False
        for i, feature in enumerate(predictor.feature_names, 1):
            if 'dmft' in feature.lower():
                print(f"{i:2d}. {feature} *** DMFT SCORE ***")
                dmft_found = True
            else:
                print(f"{i:2d}. {feature}")
        
        # Analysis
        print("\n🔍 DMFT Analysis:")
        print("-" * 40)
        if dmft_found:
            print("✅ DMFT score IS included in the current model")
            print("   └─ Used as direct feature for ML prediction")
        else:
            print("❌ DMFT score is NOT in the current feature set")
            print("   └─ May have been excluded during feature selection")
            
        # Check for DMFT-related features
        dmft_related = []
        for feature in predictor.feature_names:
            if any(term in feature.lower() for term in ['cavit', 'restor', 'missing', 'filled', 'decay']):
                dmft_related.append(feature)
                
        if dmft_related:
            print(f"\n🦷 DMFT-Related Features Found ({len(dmft_related)}):")
            for feature in dmft_related:
                print(f"   • {feature}")
            print("   └─ AI uses specific dental indicators instead of summary score")
        
        return dmft_found, dmft_related
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None, None

if __name__ == "__main__":
    check_dmft_in_features()
