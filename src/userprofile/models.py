from django.db import models

from django.contrib.auth.models import User

from django.db import models

# Create your models here.

class Profile(models.Model):
    
    HEALTH_BODIES = [
        ('HPCSA', 'Health Professions Council of South Africa'),
        ('SANC', 'South African Nursing Council'),
        ('SAPC', 'South African Pharmacy Council'),
        ('SADTC', 'South African Dental Technicians Council'),
        ('AHPCSA', 'Allied Health Professions Council of South African'),
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
        
        # SAPC - South African Pharmacy Council
        ('pharmacist', 'Pharmacist'),
        ('pharmacy_assistant', 'Pharmacy Assistant'),
        ('pharmacist_intern', 'Pharmacist Intern'),
        
        # SADTC - South African Dental Technicians Council
        ('dental_technician', 'Dental Technician'),
        ('dental_technologist', 'Dental Technologist'),
        
        # AHPCSA - Allied Health Professions Council of South Africa
        ('chiropractor', 'Chiropractor'),
        ('homeopath', 'Homeopath'),
        ('naturopath', 'Naturopath'),
        ('osteopath', 'Osteopath'),
        ('acupuncturist', 'Acupuncturist'),
        ('traditional_health_practitioner', 'Traditional Health Practitioner'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=64)
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
    email = models.CharField(max_length=64, null=True)
    address = models.CharField(max_length=64, null=True)
    tel = models.CharField(max_length=64, null=True)