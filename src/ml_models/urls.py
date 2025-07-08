from django.urls import path
from . import views

app_name = 'ml_models'

urlpatterns = [
    path('predict-risk/', views.predict_risk, name='predict_risk'),
    path('model-status/', views.model_status, name='model_status'),
    path('training-template/', views.download_training_template, name='training_template'),
]
