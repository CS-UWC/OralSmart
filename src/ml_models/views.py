from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .ml_predictor import MLPRiskPredictor
import json
import logging

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def predict_risk(request):
    """
    API endpoint to predict risk level for a patient.
    Expects JSON data with patient information.
    """
    try:
        # Parse JSON data
        data = json.loads(request.body)
        
        # Extract dental and dietary data
        dental_data = data.get('dental_data')
        dietary_data = data.get('dietary_data')
        
        if not dental_data:
            return JsonResponse({
                'error': 'Dental data is required',
                'status': 'error'
            }, status=400)
        
        # Create mock objects from the data
        class MockDentalData:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        class MockDietaryData:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        # Initialize predictor
        predictor = MLPRiskPredictor()
        
        # Create data objects
        dental_obj = MockDentalData(dental_data)
        dietary_obj = MockDietaryData(dietary_data) if dietary_data else None
        
        # Make prediction
        prediction = predictor.predict_risk(dental_obj, dietary_obj)
        
        return JsonResponse({
            'prediction': prediction,
            'status': 'success'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data',
            'status': 'error'
        }, status=400)
    
    except ValueError as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=400)
    
    except Exception as e:
        logger.error(f"Error in predict_risk: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error',
            'status': 'error'
        }, status=500)

@login_required
def model_status(request):
    """
    Get the current status of the ML model.
    """
    try:
        predictor = MLPRiskPredictor()
        model_info = predictor.get_model_info()
        
        return JsonResponse({
            'model_info': model_info,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}")
        return JsonResponse({
            'error': 'Failed to get model status',
            'status': 'error'
        }, status=500)

@login_required
def download_training_template(request):
    """
    Download a CSV template for training data.
    """
    try:
        from django.http import HttpResponse
        import csv
        
        # Create response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="training_data_template.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Get feature names
        predictor = MLPRiskPredictor()
        headers = predictor.feature_names + ['risk_level']
        
        # Write headers
        writer.writerow(headers)
        
        # Write sample rows
        sample_rows = [
            # High risk example
            [1,0,1,1,1,1,0,1,0,1,0,1,0,0,0,1,1,0,1,1,0,0,0,1,0,0,0,0,0,0,1,1,1,0,0,18,'high'],
            # Low risk example
            [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,2,'low'],
        ]
        
        for row in sample_rows:
            writer.writerow(row)
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating training template: {str(e)}")
        return JsonResponse({
            'error': 'Failed to create training template',
            'status': 'error'
        }, status=500)
