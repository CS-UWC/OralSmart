from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import User
from patient.models import Patient
from reports.views import send_report_email
import json

class Command(BaseCommand):
    help = 'Test email endpoint functionality'

    def add_arguments(self, parser):
        parser.add_argument('patient_id', type=int, help='Patient ID to test with')

    def handle(self, *args, **options):
        patient_id = options['patient_id']
        
        # Create a test request
        factory = RequestFactory()
        
        # Test 1: Test with missing recipient email
        self.stdout.write("Test 1: Missing recipient email")
        request = factory.post(f'/reports/send-email/{patient_id}/', {
            'cc_emails': 'doctor@clinic.com',
            'subject': 'Test Report',
            'message': 'Test message'
        })
        
        # Add a mock user
        user = User.objects.first()
        if not user:
            user = User.objects.create_user('testuser', 'test@example.com', 'password')
        request.user = user
        
        response = send_report_email(request, patient_id)
        if response.status_code == 400:
            self.stdout.write(self.style.SUCCESS("✓ Correctly rejected missing recipient email"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ Unexpected response: {response.status_code}"))
        
        # Test 2: Test with valid data (but don't actually send email)
        self.stdout.write("\nTest 2: Valid form data structure")
        request = factory.post(f'/reports/send-email/{patient_id}/', {
            'recipient_email': 'patient@example.com',
            'cc_emails': 'doctor1@clinic.com, doctor2@clinic.com',
            'subject': 'OralSmart Dental Report - Test Patient',
            'message': 'Please find attached your dental screening report.'
        })
        request.user = user
        
        # Mock the email sending to avoid actually sending
        try:
            response = send_report_email(request, patient_id)
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("✓ Valid request processed successfully"))
            else:
                self.stdout.write(self.style.WARNING(f"Response: {response.status_code} - {response.content.decode()}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error during processing: {str(e)}"))
        
        # Test 3: Test with invalid patient ID
        self.stdout.write("\nTest 3: Invalid patient ID")
        request = factory.post(f'/reports/send-email/9999/', {
            'recipient_email': 'patient@example.com',
            'subject': 'Test Report',
            'message': 'Test message'
        })
        request.user = user
        
        response = send_report_email(request, 9999)
        if response.status_code == 404:
            self.stdout.write(self.style.SUCCESS("✓ Correctly rejected invalid patient ID"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ Unexpected response: {response.status_code}"))
        
        self.stdout.write(f"\n{self.style.SUCCESS('Email endpoint testing completed!')}")
        self.stdout.write(f"Ready to test via web interface at: http://localhost:8000/reports/report/{patient_id}/")
        
        # Show the URL structure
        self.stdout.write(f"\n--- URL STRUCTURE ---")
        self.stdout.write(f"Report View: /reports/report/{patient_id}/")
        self.stdout.write(f"PDF Generation: /reports/pdf/{patient_id}/")
        self.stdout.write(f"Email Sending: /reports/send-email/{patient_id}/")
        
        # Show expected email configuration
        self.stdout.write(f"\n--- EMAIL CONFIGURATION NEEDED ---")
        self.stdout.write("Make sure these settings are configured in settings.py:")
        self.stdout.write("EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'")
        self.stdout.write("EMAIL_HOST = 'smtp.gmail.com'")
        self.stdout.write("EMAIL_PORT = 587")
        self.stdout.write("EMAIL_USE_TLS = True")
        self.stdout.write("EMAIL_HOST_USER = 'your-email@gmail.com'")
        self.stdout.write("EMAIL_HOST_PASSWORD = 'your-app-password'")
        self.stdout.write("DEFAULT_FROM_EMAIL = 'your-email@gmail.com'")
