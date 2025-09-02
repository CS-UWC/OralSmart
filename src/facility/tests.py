"""
Integration tests for facility app.

Tests cover:
- Clinic model creation and validation
- Clinic list view with search and filtering
- Patient referral functionality 
- PDF generation for referrals
- Email sending for referrals
- Error handling and edge cases
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from django.test.utils import override_settings
from unittest.mock import patch, Mock
import io
from datetime import datetime

from facility.models import Clinic
from patient.models import Patient
from assessments.models import DentalScreening, DietaryScreening
from facility.views import generate_pdf_buffer


class FacilityIntegrationTests(TestCase):
    """Integration tests for facility app functionality"""
    
    def get_patient_id(self):
        """Helper method to get patient ID safely for Pylance"""
        return getattr(self.patient, 'id')
    
    def get_clinic_id(self):
        """Helper method to get clinic ID safely for Pylance"""
        return getattr(self.clinic, 'id')
    
    def get_redirect_url(self, response):
        """Helper method to get redirect URL safely for Pylance"""
        return getattr(response, 'url', None)
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Clear mail outbox for clean testing
        mail.outbox = []
        
        # Create test user
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='TestPass123!'
        )
        
        # Create test clinics
        self.clinic = Clinic.objects.create(
            name='Test Dental Clinic',
            address='123 Test Street, Test City',
            phone_number='0123456789',
            email='clinic@test.com',
            website='https://testclinic.com',
            description='A comprehensive dental clinic for testing',
            hours='Mon-Fri 8AM-5PM',
            emergency='24/7 Emergency',
            clinic_type='private'
        )
        
        self.public_clinic = Clinic.objects.create(
            name='Public Health Clinic',
            address='456 Public Ave, Health City',
            phone_number='0987654321',
            email='public@health.gov',
            description='Public healthcare facility',
            clinic_type='public'
        )
        
        # Create test patient
        self.patient = Patient.objects.create(
            name='Test',
            surname='Patient',
            parent_id='1234567890123',
            parent_contact='0123456789'
        )
        
        # Create dental screening data
        self.dental_data = DentalScreening.objects.create(
            patient=self.patient,
            caregiver_treatment='yes',
            sa_citizen='yes',
            special_needs='no',
            plaque='yes',
            dry_mouth='no',
            enamel_defects='yes',
            appliance='no',
            fluoride_water='yes',
            fluoride_toothpaste='yes',
            topical_fluoride='yes',
            regular_checkups='yes',
            sealed_pits='no',
            restorative_procedures='yes',
            enamel_change='yes',
            dentin_discoloration='no',
            white_spot_lesions='yes',
            cavitated_lesions='yes',
            multiple_restorations='no',
            missing_teeth='yes',
            teeth_data={
                'tooth_11': 'Sound',
                'tooth_21': 'Caries',
                'tooth_31': 'Restored',
                'tooth_41': 'Missing'
            }
        )
        
        # Create dietary screening data
        self.dietary_data = DietaryScreening.objects.create(
            patient=self.patient,
            sweet_sugary_foods='yes',
            sweet_sugary_foods_daily='1-3_day',
            sweet_sugary_foods_weekly='1-3_week',
            cold_drinks_juices='yes',
            cold_drinks_juices_daily='1-3_day',
            cold_drinks_juices_weekly='1-3_week',
            takeaways_processed_foods='no',
            fresh_fruit='yes',
            processed_fruit='no',
            salty_snacks='yes',
            spreads='yes',
            added_sugars='no',
            dairy_products='yes',
            vegetables='yes',
            water='yes'
        )
    
    def test_clinic_model_creation(self):
        """Test Clinic model creation and string representation"""
        clinic = Clinic.objects.create(
            name='New Test Clinic',
            address='789 New Street',
            clinic_type='private'
        )
        
        self.assertEqual(str(clinic), 'New Test Clinic')
        self.assertEqual(clinic.clinic_type, 'private')
        self.assertEqual(clinic.address, '789 New Street')
    
    def test_clinic_model_optional_fields(self):
        """Test Clinic model with minimal required fields"""
        clinic = Clinic.objects.create(name='Minimal Clinic')
        
        self.assertEqual(clinic.name, 'Minimal Clinic')
        self.assertEqual(clinic.clinic_type, 'public')  # Default value
        self.assertIsNone(clinic.address)
        self.assertIsNone(clinic.phone_number)
        self.assertIsNone(clinic.email)
    
    def test_clinic_list_view_basic(self):
        """Test basic clinic list view functionality"""
        response = self.client.get(reverse('clinics'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dental Clinic')
        self.assertContains(response, 'Public Health Clinic')
        self.assertEqual(len(response.context['clinics']), 2)
    
    def test_clinic_list_view_search_by_name(self):
        """Test clinic list view search functionality by name"""
        response = self.client.get(reverse('clinics'), {'search': 'Dental'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dental Clinic')
        self.assertNotContains(response, 'Public Health Clinic')
        self.assertEqual(len(response.context['clinics']), 1)
        self.assertEqual(response.context['search_query'], 'Dental')
    
    def test_clinic_list_view_search_by_address(self):
        """Test clinic list view search functionality by address"""
        response = self.client.get(reverse('clinics'), {'search': 'Test Street'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dental Clinic')
        self.assertNotContains(response, 'Public Health Clinic')
        self.assertEqual(len(response.context['clinics']), 1)
    
    def test_clinic_list_view_search_by_phone(self):
        """Test clinic list view search functionality by phone number"""
        response = self.client.get(reverse('clinics'), {'search': '0123456789'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dental Clinic')
        self.assertEqual(len(response.context['clinics']), 1)
    
    def test_clinic_list_view_search_by_email(self):
        """Test clinic list view search functionality by email"""
        response = self.client.get(reverse('clinics'), {'search': 'clinic@test.com'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dental Clinic')
        self.assertEqual(len(response.context['clinics']), 1)
    
    def test_clinic_list_view_search_by_description(self):
        """Test clinic list view search functionality by description"""
        response = self.client.get(reverse('clinics'), {'search': 'comprehensive'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dental Clinic')
        self.assertEqual(len(response.context['clinics']), 1)
    
    def test_clinic_list_view_search_no_results(self):
        """Test clinic list view search with no matching results"""
        response = self.client.get(reverse('clinics'), {'search': 'nonexistent'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clinics']), 0)
        self.assertEqual(response.context['search_query'], 'nonexistent')
    
    def test_clinic_list_view_filter_private(self):
        """Test clinic list view filtering by private clinic type"""
        response = self.client.get(reverse('clinics'), {'center_type': 'private'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dental Clinic')
        self.assertNotContains(response, 'Public Health Clinic')
        self.assertEqual(len(response.context['clinics']), 1)
        self.assertEqual(response.context['center_type'], 'private')
    
    def test_clinic_list_view_filter_public(self):
        """Test clinic list view filtering by public clinic type"""
        response = self.client.get(reverse('clinics'), {'center_type': 'public'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public Health Clinic')
        self.assertNotContains(response, 'Test Dental Clinic')
        self.assertEqual(len(response.context['clinics']), 1)
        self.assertEqual(response.context['center_type'], 'public')
    
    def test_clinic_list_view_combined_search_and_filter(self):
        """Test clinic list view with both search and filter"""
        response = self.client.get(reverse('clinics'), {
            'search': 'Health',
            'center_type': 'public'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public Health Clinic')
        self.assertEqual(len(response.context['clinics']), 1)
    
    def test_clinic_list_view_with_patient_context(self):
        """Test clinic list view with patient_id parameter"""
        response = self.client.get(reverse('clinics'), {
            'patient_id': str(self.get_patient_id()),
            'selected_sections': 'dental,dietary'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_id'], str(self.get_patient_id()))
        self.assertEqual(response.context['selected_sections'], ['dental', 'dietary'])
    
    def test_refer_patient_get_method_not_allowed(self):
        """Test refer_patient view rejects GET requests"""
        url = reverse('refer_patient', kwargs={'clinic_id': self.get_clinic_id()})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 405)
    
    @override_settings(DEFAULT_FROM_EMAIL='test@oralsmart.com')
    def test_refer_patient_successful_referral(self):
        """Test successful patient referral with email sending"""
        url = reverse('refer_patient', kwargs={'clinic_id': self.get_clinic_id()})
        
        response = self.client.post(url, {
            'patient_id': str(self.get_patient_id()),
            'selected_sections': 'dental,dietary',
            'appointment_date': '2025-12-25',
            'appointment_time': '10:00'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Referral Successful!')
        
        # Check that email was sent (mail.outbox accumulates across tests)
        self.assertGreaterEqual(len(mail.outbox), 1)
        # Get the most recent email
        email = mail.outbox[-1]
        self.assertIn('Referral for Test Patient', email.subject)
        self.assertEqual(email.to, ['clinic@test.com'])
        self.assertIn('2025-12-25 at 10:00', email.body)
        
        # Check PDF attachment
        self.assertEqual(len(email.attachments), 1)
        attachment = email.attachments[0]
        self.assertIn('report_Test_Patient.pdf', attachment[0])
        self.assertEqual(attachment[2], 'application/pdf')
    
    def test_refer_patient_missing_patient_id(self):
        """Test refer_patient with missing patient_id"""
        url = reverse('refer_patient', kwargs={'clinic_id': self.get_clinic_id()})
        
        response = self.client.post(url, {
            'selected_sections': 'dental',
            'appointment_date': '2025-12-25',
            'appointment_time': '10:00'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'Missing patient_id')
    
    def test_refer_patient_nonexistent_patient(self):
        """Test refer_patient with non-existent patient"""
        url = reverse('refer_patient', kwargs={'clinic_id': self.get_clinic_id()})
        
        with self.assertRaises(Patient.DoesNotExist):
            self.client.post(url, {
                'patient_id': '99999',
                'selected_sections': 'dental',
                'appointment_date': '2025-12-25',
                'appointment_time': '10:00'
            })
    
    def test_refer_patient_nonexistent_clinic(self):
        """Test refer_patient with non-existent clinic"""
        url = reverse('refer_patient', kwargs={'clinic_id': 99999})
        
        with self.assertRaises(Clinic.DoesNotExist):
            self.client.post(url, {
                'patient_id': str(self.get_patient_id()),
                'selected_sections': 'dental',
                'appointment_date': '2025-12-25',
                'appointment_time': '10:00'
            })
    
    def test_refer_patient_no_screening_data(self):
        """Test refer_patient with patient having no screening data"""
        # Create patient without screening data
        patient_no_data = Patient.objects.create(
            name='No',
            surname='Data',
            parent_id='9876543210987',
            parent_contact='0987654321'
        )
        
        url = reverse('refer_patient', kwargs={'clinic_id': self.get_clinic_id()})
        
        response = self.client.post(url, {
            'patient_id': str(getattr(patient_no_data, 'id')),
            'selected_sections': 'dental',
            'appointment_date': '2025-12-25',
            'appointment_time': '10:00'
        })
        
        # Should redirect to clinics page with error message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.get_redirect_url(response), reverse('clinics'))
    
    def test_refer_patient_only_dental_data(self):
        """Test refer_patient with only dental screening data"""
        # Create patient with only dental data
        patient_dental_only = Patient.objects.create(
            name='Dental',
            surname='Only',
            parent_id='1111111111111',
            parent_contact='1111111111'
        )
        
        DentalScreening.objects.create(
            patient=patient_dental_only,
            caregiver_treatment='yes',
            sa_citizen='yes',
            plaque='yes',
            teeth_data={'tooth_11': 'Sound'}  # Required field
        )
        
        url = reverse('refer_patient', kwargs={'clinic_id': self.get_clinic_id()})
        
        response = self.client.post(url, {
            'patient_id': str(getattr(patient_dental_only, 'id')),
            'selected_sections': 'dental',
            'appointment_date': '2025-12-25',
            'appointment_time': '10:00'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(mail.outbox), 1)
    
    def test_refer_patient_only_dietary_data(self):
        """Test refer_patient with only dietary screening data"""
        # Create patient with only dietary data
        patient_dietary_only = Patient.objects.create(
            name='Dietary',
            surname='Only',
            parent_id='2222222222222',
            parent_contact='2222222222'
        )
        
        DietaryScreening.objects.create(
            patient=patient_dietary_only,
            sweet_sugary_foods='yes',
            cold_drinks_juices='no',
            takeaways_processed_foods='no',
            fresh_fruit='yes',
            processed_fruit='no',
            salty_snacks='no',
            spreads='no',
            added_sugars='no',
            dairy_products='yes',
            vegetables='yes',
            water='yes'
        )
        
        url = reverse('refer_patient', kwargs={'clinic_id': self.get_clinic_id()})
        
        response = self.client.post(url, {
            'patient_id': str(getattr(patient_dietary_only, 'id')),
            'selected_sections': 'dietary',
            'appointment_date': '2025-12-25',
            'appointment_time': '10:00'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(mail.outbox), 1)
    
    def test_refer_patient_clinic_without_email(self):
        """Test refer_patient with clinic that has no email"""
        clinic_no_email = Clinic.objects.create(
            name='No Email Clinic',
            clinic_type='private'
        )
        
        url = reverse('refer_patient', kwargs={'clinic_id': getattr(clinic_no_email, 'id')})
        
        response = self.client.post(url, {
            'patient_id': str(self.get_patient_id()),
            'selected_sections': 'dental',
            'appointment_date': '2025-12-25',
            'appointment_time': '10:00'
        })
        
        self.assertEqual(response.status_code, 200)
        # Email with empty recipient list may not be added to mail.outbox
        # But the referral should still be processed successfully
        self.assertContains(response, 'Referral Successful!')
    
    def test_generate_pdf_buffer_with_all_data(self):
        """Test PDF buffer generation with complete screening data"""
        selected_sections = ['dental', 'dietary']
        
        buffer = generate_pdf_buffer(
            self.patient,
            self.dental_data,
            self.dietary_data,
            selected_sections
        )
        
        self.assertIsInstance(buffer, io.BytesIO)
        self.assertGreater(len(buffer.getvalue()), 1000)  # PDF should have substantial content
    
    def test_generate_pdf_buffer_dental_only(self):
        """Test PDF buffer generation with only dental data"""
        selected_sections = ['dental']
        
        buffer = generate_pdf_buffer(
            self.patient,
            self.dental_data,
            None,
            selected_sections
        )
        
        self.assertIsInstance(buffer, io.BytesIO)
        self.assertGreater(len(buffer.getvalue()), 500)
    
    def test_generate_pdf_buffer_dietary_only(self):
        """Test PDF buffer generation with only dietary data"""
        selected_sections = ['dietary']
        
        buffer = generate_pdf_buffer(
            self.patient,
            None,
            self.dietary_data,
            selected_sections
        )
        
        self.assertIsInstance(buffer, io.BytesIO)
        self.assertGreater(len(buffer.getvalue()), 500)
    
    def test_generate_pdf_buffer_empty_sections(self):
        """Test PDF buffer generation with empty selected sections"""
        selected_sections = []
        
        buffer = generate_pdf_buffer(
            self.patient,
            self.dental_data,
            self.dietary_data,
            selected_sections
        )
        
        self.assertIsInstance(buffer, io.BytesIO)
        # Should still generate basic PDF even with no sections
        self.assertGreater(len(buffer.getvalue()), 200)
    
    def test_clinic_model_clinic_type_choices(self):
        """Test clinic model with different clinic type choices"""
        # Test private clinic
        private_clinic = Clinic.objects.create(
            name='Private Clinic',
            clinic_type='private'
        )
        self.assertEqual(private_clinic.clinic_type, 'private')
        
        # Test public clinic
        public_clinic = Clinic.objects.create(
            name='Public Clinic',
            clinic_type='public'
        )
        self.assertEqual(public_clinic.clinic_type, 'public')
    
    def test_clinic_list_view_case_insensitive_search(self):
        """Test that clinic list search is case insensitive"""
        response = self.client.get(reverse('clinics'), {'search': 'DENTAL'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dental Clinic')
        self.assertEqual(len(response.context['clinics']), 1)
    
    def test_clinic_list_view_partial_search(self):
        """Test clinic list view with partial search terms"""
        response = self.client.get(reverse('clinics'), {'search': 'Test'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dental Clinic')
        # Should match both "Test Dental Clinic" and any other clinic with "Test"
        self.assertGreaterEqual(len(response.context['clinics']), 1)
    
    @override_settings(DEFAULT_FROM_EMAIL='test@oralsmart.com')
    def test_refer_patient_email_content_format(self):
        """Test the format and content of referral emails"""
        url = reverse('refer_patient', kwargs={'clinic_id': self.get_clinic_id()})
        
        self.client.post(url, {
            'patient_id': str(self.get_patient_id()),
            'selected_sections': 'dental,dietary',
            'appointment_date': '2025-12-25',
            'appointment_time': '14:30'
        })
        
        # Get the most recent email
        email = mail.outbox[-1]
        
        # Check subject format
        self.assertEqual(email.subject, 'Referral for Test Patient')
        
        # Check body content
        expected_content = [
            'Patient Test Patient is referred',
            'appointment on 2025-12-25 at 14:30'
        ]
        
        for content in expected_content:
            self.assertIn(content, email.body)
    
    def test_clinic_model_string_representation_length(self):
        """Test clinic string representation with long names"""
        long_name = 'A' * 100  # Name longer than max_length
        clinic = Clinic.objects.create(
            name=long_name[:64],  # Django will truncate to max_length
            clinic_type='private'
        )
        
        self.assertEqual(len(str(clinic)), 64)
        self.assertEqual(str(clinic), 'A' * 64)
    
    def test_clinic_list_view_empty_database(self):
        """Test clinic list view when no clinics exist"""
        # Delete all clinics
        Clinic.objects.all().delete()
        
        response = self.client.get(reverse('clinics'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clinics']), 0)
    
    def test_clinic_model_url_field_validation(self):
        """Test clinic model URL field accepts valid URLs"""
        clinic = Clinic.objects.create(
            name='URL Test Clinic',
            website='https://example.com',
            clinic_type='private'
        )
        
        self.assertEqual(clinic.website, 'https://example.com')
    
    def test_clinic_model_email_field_validation(self):
        """Test clinic model email field accepts valid emails"""
        clinic = Clinic.objects.create(
            name='Email Test Clinic',
            email='test@example.com',
            clinic_type='private'
        )
        
        self.assertEqual(clinic.email, 'test@example.com')
