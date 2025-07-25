from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db import models
import os

# Create your models here.

class Profile(models.Model):
    
    HEALTH_BODIES = [
        ('HPCSA', 'Health Professions Council of South Africa'),
        ('SANC', 'South African Nursing Council'),
    ]

    PROFESSIONS = [
        # HPCSA - Health Professions Council of South Africa
        ('medical_doctor', 'Medical Doctor'),
        ('dentist', 'Dentist'),
        ('psychologist', 'Psychologist'),
        ('physiotherapist', 'Physiotherapist'),
        ('radiographer', 'Radiographer'),
        ('occupational_therapist', 'Occupational Therapist'),
        ('biokineticist', 'Biokineticist'),
        ('clinical_technologist', 'Clinical Technologist'),
        ('dietitian', 'Dietitian'),
        ('audiologist', 'Audiologist'),
        ('optometrist', 'Optometrist'),
        ('emergency_care_practitioner', 'Emergency Care Practitioner'),
        
        # SANC - South African Nursing Council
        ('registered_nurse', 'Registered Nurse'),
        ('enrolled_nurse', 'Enrolled Nurse'),
        ('nursing_assistant', 'Nursing Assistant'),
        ('midwife', 'Midwife'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    profession = models.CharField(
        max_length=64,
        choices=PROFESSIONS,
        default='dentist'
    )

    health_professional_body = models.CharField(
        max_length=64,
        choices=HEALTH_BODIES,
        default='HPCSA'
    )

    reg_num = models.CharField(
        max_length=64,
        default="0",
    )

    email = models.CharField(max_length=64, null=True)

    address = models.CharField(max_length=64, null=True)
    
    tel = models.CharField(max_length=64, null=True)

    profile_pic = models.ImageField(upload_to='profile/', default='images/default/default_profile_pic.jpg',null=True, blank=True)

    def get_profile_picture_url(self):
        """
        Returns profile picture URL or default if none exists
        """
        if self.profile_pic and os.path.exists(self.profile_pic.path):
            return self.profile_pic.url
        return f"{settings.MEDIA_URL}images/default/default_profile_pic.jpg"
    
    @property
    def profile_picture_url(self):
        """Property version of get_profile_picture_url"""
        return self.get_profile_picture_url()