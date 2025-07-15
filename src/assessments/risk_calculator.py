"""
Risk calculation utilities for factory data generation.
This provides the same risk calculation logic used in the export command
but adapted for use with factory-generated model instances.
"""

def calculate_risk_level_for_patient(patient, dental_screening=None, dietary_screening=None, min_dmft=None, risk_threshold=None):
    """
    Calculate risk level for a patient with their assessment data.
    
    Args:
        patient: Patient model instance
        dental_screening: DentalScreening model instance (optional)
        dietary_screening: DietaryScreening model instance (optional)
        min_dmft: Minimum DMFT for high risk classification (optional)
        risk_threshold: Custom high-risk threshold (optional)
        
    Returns:
        str: 'low', 'medium', or 'high'
    """
    from ml_models.ml_predictor import MLPRiskPredictor
    
    # Initialize predictor to get feature extraction logic
    predictor = MLPRiskPredictor()
    
    try:
        # Convert model instances to feature dictionary
        feature_dict = predictor._prepare_features(dental_screening, dietary_screening) # type: ignore
        
        # Use the same risk calculation logic as the export command
        return _calculate_risk_level_from_features(feature_dict, min_dmft, risk_threshold)
        
    except Exception as e:
        # Fallback to simple calculation if feature extraction fails
        return _simple_risk_calculation(patient, dental_screening, dietary_screening)


def _calculate_risk_level_from_features(feature_dict, min_dmft=None, risk_threshold=None):
    """
    Calculate risk level based on feature values - matches export command logic.
    """
    # DMFT score risk factor
    dmft_score = feature_dict.get('total_dmft_score', 0)
    
    # Use custom DMFT threshold if provided
    if min_dmft is not None and dmft_score >= min_dmft:
        return 'high'
    
    # Calculate composite risk score (same as export command)
    risk_score = 0
    
    # Clinical findings (major risk factors - 2 points each)
    clinical_factors = ['cavitated_lesions', 'multiple_restorations', 'missing_teeth', 
                       'enamel_change', 'dentin_discoloration', 'white_spot_lesions']
    
    for factor in clinical_factors:
        if feature_dict.get(factor, 0) == 1:
            risk_score += 2
    
    # Protective factors (subtract 1 point each)
    protective_factors = ['fluoride_water', 'fluoride_toothpaste', 'topical_fluoride',
                         'regular_checkups', 'sealed_pits']
    
    for factor in protective_factors:
        if feature_dict.get(factor, 0) == 1:
            risk_score -= 1
    
    # Dietary risk factors
    dietary_factors = ['sweet_sugary_foods', 'takeaways_processed_foods', 
                      'cold_drinks_juices', 'processed_fruit', 'added_sugars']
    
    for factor in dietary_factors:
        if feature_dict.get(factor, 0) == 1:
            risk_score += 1
    
    # High frequency dietary factors (3+ times daily)
    frequency_factors = ['sweet_sugary_foods_daily', 'takeaways_processed_foods_daily',
                        'cold_drinks_juices_daily', 'processed_fruit_daily', 'added_sugars_daily']
    
    for factor in frequency_factors:
        freq_value = feature_dict.get(factor, 0)
        if freq_value >= 3:  # High frequency
            risk_score += 1
    
    # Social risk factors
    if feature_dict.get('special_needs', 0) == 1:
        risk_score += 2
    
    if feature_dict.get('caregiver_treatment', 0) == 0:  # No caregiver treatment
        risk_score += 1
    
    # DMFT contribution
    risk_score += dmft_score * 0.5  # Each DMFT point adds 0.5 to risk
    
    # Data availability penalty (uncertainty increases risk threshold)
    has_dental = feature_dict.get('has_dental_data', 0)
    has_dietary = feature_dict.get('has_dietary_data', 0)
    data_completeness = has_dental + has_dietary
    
    # Use custom thresholds if provided, otherwise calculate based on data completeness
    if risk_threshold is not None:
        # For 3-class system, treat risk_threshold as the high threshold
        # Medium threshold is typically 60-70% of high threshold
        high_threshold = risk_threshold
        medium_threshold = risk_threshold * 0.65  # 65% of high threshold
    else:
        # More conservative thresholds when data is incomplete
        base_high_threshold = 8
        if data_completeness == 2:  # Both assessments
            high_threshold = base_high_threshold
            medium_threshold = base_high_threshold * 0.65  # ~5.2
        elif data_completeness == 1:  # Only one assessment
            high_threshold = base_high_threshold - 2  # 6
            medium_threshold = (base_high_threshold - 2) * 0.65  # ~3.9
        else:  # No assessments (shouldn't happen if validation works)
            high_threshold = base_high_threshold - 4  # 4
            medium_threshold = (base_high_threshold - 4) * 0.65  # ~2.6
    
    # Return 3-class risk level
    if risk_score >= high_threshold:
        return 'high'
    elif risk_score >= medium_threshold:
        return 'medium'
    else:
        return 'low'


def _simple_risk_calculation(patient, dental_screening=None, dietary_screening=None):
    """
    Simplified risk calculation as fallback when feature extraction fails.
    """
    risk_score = 0
    
    if dental_screening:
        # Count dental risk factors
        if getattr(dental_screening, 'cavitated_lesions', None) == 'yes':
            risk_score += 2
        if getattr(dental_screening, 'multiple_restorations', None) == 'yes':
            risk_score += 2
        if getattr(dental_screening, 'missing_teeth', None) == 'yes':
            risk_score += 2
        if getattr(dental_screening, 'plaque', None) == 'yes':
            risk_score += 1
        
        # Subtract protective factors
        if getattr(dental_screening, 'fluoride_toothpaste', None) == 'yes':
            risk_score -= 1
        if getattr(dental_screening, 'regular_checkups', None) == 'yes':
            risk_score -= 1
    
    if dietary_screening:
        # Count dietary risk factors
        if getattr(dietary_screening, 'sweet_sugary_foods', None) == 'yes':
            risk_score += 1
        if getattr(dietary_screening, 'cold_drinks_juices', None) == 'yes':
            risk_score += 1
    
    # Simple 3-class thresholds
    if risk_score >= 6:
        return 'high'
    elif risk_score >= 3:
        return 'medium'
    else:
        return 'low'
