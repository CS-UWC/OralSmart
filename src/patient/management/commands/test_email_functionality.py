from django.core.management.base import BaseCommand
from patient.models import Patient
from assessments.models import DentalScreening
from reports.views import generate_pdf_buffer
from django.template.loader import render_to_string

class Command(BaseCommand):
    help = 'Test email functionality without actually sending emails'

    def add_arguments(self, parser):
        parser.add_argument('patient_id', type=int, help='Patient ID to test with')

    def handle(self, *args, **options):
        patient_id = options['patient_id']
        
        try:
            patient = Patient.objects.get(pk=patient_id)
        except Patient.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Patient with ID {patient_id} not found'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Testing email functionality for patient: {patient.name} {patient.surname}'))
        
        # Test 1: Check if patient has screening data
        dental_count = DentalScreening.objects.filter(patient_id=patient_id).count()
        self.stdout.write(f"Dental screenings: {dental_count}")
        
        if dental_count == 0:
            self.stdout.write(self.style.ERROR('Patient has no screening data - email will contain error PDF'))
            return
        
        # Test 2: Generate PDF buffer
        try:
            self.stdout.write("Generating PDF buffer...")
            selected_sections = ['section1', 'section2', 'section3', 'section4', 'section5']
            pdf_buffer = generate_pdf_buffer(patient, selected_sections)
            pdf_size = len(pdf_buffer.getvalue())
            self.stdout.write(self.style.SUCCESS(f"✓ PDF generated successfully ({pdf_size} bytes)"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ PDF generation failed: {str(e)}"))
            return
        
        # Test 3: Render email template
        try:
            self.stdout.write("Rendering email template...")
            email_context = {
                'patient_name': f'{patient.name} {patient.surname}',
                'patient_id': patient_id,
                'message': 'This is a test message from the health professional.',
                'sections_included': 'Section 1, Section 2, Section 3, Section 4, Section 5',
                'sender_name': 'Test Health Professional'
            }
            
            html_content = render_to_string('reports/email_template.html', email_context)
            self.stdout.write(self.style.SUCCESS(f"✓ Email template rendered successfully ({len(html_content)} characters)"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Email template rendering failed: {str(e)}"))
            return
        
        # Test 4: Email content preview
        self.stdout.write("\n--- EMAIL CONTENT PREVIEW ---")
        self.stdout.write(f"To: test@example.com")
        self.stdout.write(f"CC: doctor@clinic.com")
        self.stdout.write(f"Subject: OralSmart Dental Report - {patient.name} {patient.surname}")
        self.stdout.write(f"Attachment: dental_report_{patient.name}_{patient.surname}_{patient_id}.pdf ({pdf_size} bytes)")
        self.stdout.write("Message: This is a test message from the health professional.")
        
        self.stdout.write(f"\n{self.style.SUCCESS('✓ Email functionality test completed successfully!')}")
        self.stdout.write(f"Patient {patient_id} is ready for email testing via the web interface")
        self.stdout.write(f"URL: http://localhost:8000/reports/report/{patient_id}/")
        
        # Test 5: Show form data format
        self.stdout.write("\n--- SAMPLE FORM DATA ---")
        self.stdout.write("recipient_email: patient@example.com")
        self.stdout.write("cc_emails: doctor1@clinic.com, doctor2@clinic.com")
        self.stdout.write("subject: OralSmart Dental Report - Test Patient")
        self.stdout.write("message: Please find attached your dental screening report.")
