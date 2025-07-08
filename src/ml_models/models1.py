from django.db import models
from patient.models import Patient

class CariesRiskPrediction(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk')
    ])
    confidence_score = models.FloatField()
    prediction_date = models.DateTimeField(auto_now_add=True)
    features_used = models.JSONField()

    class Meta:
        ordering = ['-prediction_date']
