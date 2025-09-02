# mypy: disable-error-code="attr-defined"
"""
Integration tests for reports app.

Tests cover:
- Report viewing with ML predictions
- PDF generation functionality 
- Professional recommendation service
- Email sending with different PDF versions
- ML risk assessment integration
- Professional body mappings and recommendations
"""
# type: ignore[attr-defined]  # Ignore Django model attribute access issues

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from django.test.utils import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.http import FileResponse, HttpResponseRedirect
from unittest.mock import Mock, patch
import io
import json
from datetime import datetime
from typing import cast

from patient.models import Patient
from userprofile.models import Profile
from assessments.models import DentalScreening, DietaryScreening
from reports.views import (
    ProfessionalRecommendationService, 
    get_ml_risk_prediction, 
    get_risk_color,
    generate_pdf_buffer
)


class ReportsIntegrationTests(TestCase):
    """Integration tests for reports app functionality"""
    
    def get_patient_id(self):
        """Helper method to get patient ID safely for Pylance"""
        return getattr(self.patient, 'id')
    
    def get_redirect_url(self, response):
        """Helper method to get redirect URL safely for Pylance"""
        redirect_response = cast(HttpResponseRedirect, response)
        return redirect_response.url
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test users with different professions
        self.dentist_user = User.objects.create_user(
            username='dentist_test',
            email='dentist@test.com',
            password='TestPass123!',
            first_name='Dr. Jane',
            last_name='Smith'
        )
        
        self.medical_user = User.objects.create_user(
            username='doctor_test', 
            email='doctor@test.com',
            password='TestPass123!',
            first_name='Dr. John',
            last_name='Doe'
        )
        
        # Create profiles with different professions
        self.dentist_profile = Profile.objects.create(
            user=self.dentist_user,
            profession='dentist',
            reg_num='DN12345',
            health_professional_body='HPCSA'
        )
        
        self.medical_profile = Profile.objects.create(
            user=self.medical_user,
            profession='medical_doctor',
            reg_num='MD67890', 
            health_professional_body='HPCSA'
        )
        
        # Create test patient
        self.patient = Patient.objects.create(
            name='Test',
            surname='Patient',
            parent_id='1234567890123',
            parent_contact='0123456789'
        )
        # Type annotation for Pylance - Django models have id field
        self.patient: Patient  # This helps Pylance understand Patient has .id
        
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
    
    def test_professional_recommendation_service_dentist_mappings(self):
        """Test professional recommendation service for dentist users"""
        # Test dentist gets proper recommendations
        recs = ProfessionalRecommendationService.get_recommended_professionals('dentist')
        
        # Should include orthodontist, oral_surgeon, etc.
        self.assertTrue(len(recs) > 0)
        codes = [rec[0] for rec in recs]
        self.assertIn('orthodontist', codes)
        self.assertIn('oral_surgeon', codes)
    
    def test_professional_recommendation_service_medical_mappings(self):
        """Test professional recommendation service for medical doctor users"""
        recs = ProfessionalRecommendationService.get_recommended_professionals('medical_doctor')
        
        codes = [rec[0] for rec in recs]
        self.assertIn('dentist', codes)
        self.assertIn('pediatric_dentist', codes)
        self.assertIn('orthodontist', codes)
        self.assertIn('oral_surgeon', codes)
    
    def test_professional_recommendation_service_display_names(self):
        """Test professional display name conversion"""
        # Test code to display name conversion
        self.assertEqual(
            ProfessionalRecommendationService.get_professional_display_name('medical_doctor'),
            'Medical Doctor'
        )
        self.assertEqual(
            ProfessionalRecommendationService.get_professional_display_name('oral_surgeon'),
            'Oral Surgeon'
        )
        
        # Test unknown codes get title case conversion
        self.assertEqual(
            ProfessionalRecommendationService.get_professional_display_name('unknown_profession'),
            'Unknown Profession'
        )
    
    def test_professional_recommendation_session_handling(self):
        """Test professional recommendation session storage and retrieval"""
        # Mock session with valid recommendation
        mock_session = {'recommended_professional': 'dentist'}
        
        rec = ProfessionalRecommendationService.get_current_recommendation(mock_session)
        self.assertIsNotNone(rec)
        if rec is not None:  # Type guard for Pylance
            self.assertEqual(rec['code'], 'dentist')
            self.assertEqual(rec['name'], 'Dentist')
        
        # Test empty session
        empty_session = {}
        rec = ProfessionalRecommendationService.get_current_recommendation(empty_session)
        self.assertIsNone(rec)
        
        # Test session with empty string
        empty_string_session = {'recommended_professional': ''}
        rec = ProfessionalRecommendationService.get_current_recommendation(empty_string_session)
        self.assertIsNone(rec)
    
    @patch('reports.views.MLPRiskPredictor')
    def test_ml_risk_prediction_integration(self, mock_predictor):
        """Test ML risk prediction integration"""
        # Mock ML predictor 
        mock_instance = Mock()
        mock_instance.is_trained = True
        mock_instance.predict_risk.return_value = {
            'risk_level': 'high',
            'confidence': 85.5,
            'probability_low_risk': 10.0,
            'probability_medium_risk': 5.0,
            'probability_high_risk': 85.0
        }
        mock_predictor.return_value = mock_instance
        
        # Test with both dental and dietary data
        result = get_ml_risk_prediction(self.dental_data, self.dietary_data)
        
        self.assertTrue(result['available'])
        self.assertEqual(result['risk_level'], 'high')
        self.assertEqual(result['confidence'], 85.5)
        self.assertIsNone(result.get('error'))
        self.assertEqual(result['probability_high_risk'], 85.0)
    
    @patch('reports.views.MLPRiskPredictor')
    def test_ml_risk_prediction_error_handling(self, mock_predictor):
        """Test ML risk prediction error handling"""
        # Mock predictor exception
        mock_predictor.side_effect = Exception("ML model unavailable")
        
        result = get_ml_risk_prediction(self.dental_data, self.dietary_data)
        
        self.assertFalse(result['available'])
        self.assertIn('error', result)
        self.assertIn('ML model unavailable', result['error'])
    
    def test_risk_color_mapping(self):
        """Test risk level color mapping"""
        self.assertEqual(get_risk_color('high'), '#dc3545')  # Red
        self.assertEqual(get_risk_color('medium'), '#ffc107')  # Yellow
        self.assertEqual(get_risk_color('low'), '#28a745')  # Green
        self.assertEqual(get_risk_color('unknown'), '#6c757d')  # Gray default
    
    def test_view_report_requires_authentication(self):
        """Test that view_report requires user authentication"""
        url = reverse('report', kwargs={'patient_id': getattr(self.patient, 'id')})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        redirect_response = cast(HttpResponseRedirect, response)
        self.assertIn('login', redirect_response.url)
    
    @patch('reports.views.get_ml_risk_prediction')
    def test_view_report_authenticated_dentist(self, mock_ml_prediction):
        """Test view_report for authenticated dentist user"""
        mock_ml_prediction.return_value = {
            'available': True,
            'risk_level': 'medium',
            'confidence': 75.2
        }
        
        self.client.force_login(self.dentist_user)
        url = reverse('report', kwargs={'patient_id': self.get_patient_id()})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Referral Report')
        self.assertContains(response, 'Recommended Professional for Referral')
        self.assertContains(response, 'recommended_professional')
        
        # Check context data
        self.assertEqual(response.context['patient_id'], self.get_patient_id())
        self.assertIsNotNone(response.context['recommended_professionals'])
        self.assertIn('risk_prediction', response.context)
    
    @patch('reports.views.get_ml_risk_prediction')
    def test_view_report_authenticated_medical_doctor(self, mock_ml_prediction):
        """Test view_report for authenticated medical doctor user"""
        mock_ml_prediction.return_value = {
            'available': True,
            'risk_level': 'high',
            'confidence': 92.1
        }
        
        self.client.force_login(self.medical_user)
        url = reverse('report', kwargs={'patient_id': self.get_patient_id()})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Medical doctors should get different professional recommendations
        recommended_profs = response.context['recommended_professionals']
        codes = [prof[0] for prof in recommended_profs]
        self.assertIn('dentist', codes)  # Medical doctors should be able to refer to dentists
    
    def test_view_report_missing_patient(self):
        """Test view_report with non-existent patient"""
        self.client.force_login(self.dentist_user)
        url = reverse('report', kwargs={'patient_id': 99999})
        
        # View should work but will have no screening data
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that it still shows the basic report structure
        self.assertContains(response, 'Referral Report')
    
    def test_generate_pdf_requires_authentication(self):
        """Test that generate_pdf requires user authentication"""
        url = reverse('generate_pdf', kwargs={'patient_id': self.get_patient_id()})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', self.get_redirect_url(response))
    
    @patch('reports.views.get_ml_risk_prediction')
    def test_generate_pdf_get_request(self, mock_ml_prediction):
        """Test generate_pdf GET request returns PDF"""
        mock_ml_prediction.return_value = {
            'available': True,
            'risk_level': 'low',
            'confidence': 65.0
        }
        
        self.client.force_login(self.dentist_user)
        url = reverse('generate_pdf', kwargs={'patient_id': self.get_patient_id()})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('report_Test_Patient', response['Content-Disposition'])
    
    def test_generate_pdf_post_saves_recommendation(self):
        """Test generate_pdf POST request saves professional recommendation"""
        self.client.force_login(self.dentist_user)
        url = reverse('generate_pdf', kwargs={'patient_id': self.get_patient_id()})
        
        response = self.client.post(url, {
            'recommended_professional': 'orthodontist'
        })
        
        # Should return 204 No Content for AJAX request
        self.assertEqual(response.status_code, 204)
        
        # Check that session was updated
        # Note: Testing session in client is tricky, we'd verify through subsequent requests
    
    def test_generate_pdf_missing_patient_returns_error_pdf(self):
        """Test generate_pdf with missing patient returns error PDF"""
        self.client.force_login(self.dentist_user)
        url = reverse('generate_pdf', kwargs={'patient_id': 99999})
        response = self.client.get(url)
        
        # Should still return PDF (error PDF)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        # Error PDF should have error filename
        self.assertIn('error.pdf', response['Content-Disposition'])
    
    def test_send_report_email_requires_authentication(self):
        """Test that send_report_email requires authentication"""
        url = reverse('send_report_email', kwargs={'patient_id': self.get_patient_id()})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', self.get_redirect_url(response))
    
    def test_send_report_email_get_method_not_allowed(self):
        """Test send_report_email rejects GET requests"""
        self.client.force_login(self.dentist_user)
        url = reverse('send_report_email', kwargs={'patient_id': self.get_patient_id()})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode(), 'Method not allowed')
    
    @patch('reports.views.generate_pdf_buffer')
    @override_settings(DEFAULT_FROM_EMAIL='test@oralsmart.com')
    def test_send_report_email_patient_only(self, mock_generate_pdf):
        """Test sending email to patient only (no CC)"""
        # Mock PDF generation
        mock_pdf_buffer = io.BytesIO(b'fake pdf content')
        mock_generate_pdf.return_value = mock_pdf_buffer
        
        self.client.force_login(self.dentist_user)
        url = reverse('send_report_email', kwargs={'patient_id': self.get_patient_id()})
        
        response = self.client.post(url, {
            'recipient_email': 'patient@test.com',
            'subject': 'Your Dental Report',
            'message': 'Please find your dental report attached.'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Email sent successfully')
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['patient@test.com'])
        self.assertEqual(email.subject, 'Your Dental Report')
        self.assertEqual(len(email.attachments), 1)
        
        # Check attachment
        attachment = email.attachments[0]
        self.assertIn('dental_report_Test_Patient', attachment[0])
        self.assertEqual(attachment[2], 'application/pdf')
    
    @patch('reports.views.generate_pdf_buffer') 
    @override_settings(DEFAULT_FROM_EMAIL='test@oralsmart.com')
    def test_send_report_email_with_cc_professionals(self, mock_generate_pdf):
        """Test sending email with CC to health professionals"""
        # Mock PDF generation (called twice - once for patient, once for professionals)
        mock_pdf_buffer = io.BytesIO(b'fake pdf content')
        mock_generate_pdf.return_value = mock_pdf_buffer
        
        # Set a professional recommendation in session
        session = self.client.session
        session['recommended_professional'] = 'orthodontist'
        session.save()
        
        self.client.force_login(self.dentist_user)
        url = reverse('send_report_email', kwargs={'patient_id': self.get_patient_id()})
        
        response = self.client.post(url, {
            'recipient_email': 'patient@test.com',
            'cc_emails': 'prof1@test.com, prof2@test.com',
            'subject': 'Dental Report',
            'message': 'Report attached.'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Should send 2 emails - one to patient, one to professionals
        self.assertEqual(len(mail.outbox), 2)
        
        # Check patient email
        patient_email = mail.outbox[0]
        self.assertEqual(patient_email.to, ['patient@test.com'])
        
        # Check professional email
        prof_email = mail.outbox[1]
        self.assertEqual(prof_email.to, ['prof1@test.com', 'prof2@test.com'])
        self.assertIn('[PROFESSIONAL]', prof_email.subject)
        self.assertIn('AI risk assessment', prof_email.body)
        
        # Both emails should have attachments
        self.assertEqual(len(patient_email.attachments), 1)
        self.assertEqual(len(prof_email.attachments), 1)
        
        # Professional attachment should have different filename
        prof_attachment = prof_email.attachments[0]
        self.assertIn('dental_report_professional_Test_Patient', prof_attachment[0])
    
    def test_send_report_email_missing_recipient(self):
        """Test send_report_email with missing recipient email"""
        self.client.force_login(self.dentist_user)
        url = reverse('send_report_email', kwargs={'patient_id': self.get_patient_id()})
        
        response = self.client.post(url, {
            'subject': 'Test',
            'message': 'Test message'
            # Missing recipient_email
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'Recipient email is required')
    
    def test_send_report_email_missing_patient(self):
        """Test send_report_email with non-existent patient"""
        self.client.force_login(self.dentist_user)
        url = reverse('send_report_email', kwargs={'patient_id': 99999})
        
        response = self.client.post(url, {
            'recipient_email': 'test@test.com'
        })
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode(), 'Patient not found')
    
    @patch('reports.views.generate_pdf_buffer')
    def test_send_report_email_pdf_generation_error(self, mock_generate_pdf):
        """Test send_report_email handles PDF generation errors"""
        mock_generate_pdf.side_effect = Exception("PDF generation failed")
        
        self.client.force_login(self.dentist_user)
        url = reverse('send_report_email', kwargs={'patient_id': self.get_patient_id()})
        
        response = self.client.post(url, {
            'recipient_email': 'test@test.com'
        })
        
        self.assertEqual(response.status_code, 500)
        self.assertIn('Error sending email', response.content.decode())
    
    def test_send_report_email_clears_session_after_success(self):
        """Test that send_report_email clears recommendation from session after success"""
        # This would require mocking and checking session state
        # Implementation depends on how we want to test session clearing
        pass
    
    @patch('reports.views.get_ml_risk_prediction')
    def test_generate_pdf_buffer_includes_all_sections(self, mock_ml_prediction):
        """Test generate_pdf_buffer includes all available data sections"""
        mock_ml_prediction.return_value = {
            'available': True,
            'risk_level': 'medium',
            'confidence': 78.5,
            'probability_low_risk': 15.0,
            'probability_medium_risk': 70.0,
            'probability_high_risk': 15.0
        }
        
        # Test with AI assessment included
        buffer = generate_pdf_buffer(
            self.patient, 
            include_ai_assessment=True,
            user=self.dentist_user,
            recommended_professional='orthodontist'
        )
        
        self.assertIsInstance(buffer, io.BytesIO)
        self.assertGreater(len(buffer.getvalue()), 1000)  # PDF should have substantial content
        
        # Test without AI assessment
        buffer_no_ai = generate_pdf_buffer(
            self.patient,
            include_ai_assessment=False,
            user=self.dentist_user
        )
        
        self.assertIsInstance(buffer_no_ai, io.BytesIO)
        # Without AI assessment, PDF might be smaller, but should still have content
        self.assertGreater(len(buffer_no_ai.getvalue()), 500)
    
    def test_generate_pdf_buffer_missing_screening_data(self):
        """Test generate_pdf_buffer handles missing screening data gracefully"""
        # Create patient without screening data
        patient_no_data = Patient.objects.create(
            name='No',
            surname='Data',
            parent_id='9876543210987',
            parent_contact='0987654321'
        )
        
        buffer = generate_pdf_buffer(patient_no_data, user=self.dentist_user)
        
        self.assertIsInstance(buffer, io.BytesIO)
        # Should still generate PDF even without screening data
        self.assertGreater(len(buffer.getvalue()), 200)
    
    def test_professional_recommendations_context_integration(self):
        """Test that professional recommendations properly integrate with view context"""
        self.client.force_login(self.dentist_user)
        
        # Set recommendation in session
        session = self.client.session
        session['recommended_professional'] = 'oral_surgeon'
        session.save()
        
        url = reverse('report', kwargs={'patient_id': self.get_patient_id()})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Check that current recommendation appears in context
        self.assertEqual(response.context['current_recommendation_code'], 'oral_surgeon')
        self.assertEqual(response.context['current_recommendation'], 'Oral Surgeon')
    
    def test_dental_screening_data_display_in_pdf(self):
        """Test that dental screening data appears correctly in generated PDF"""
        self.client.force_login(self.dentist_user)
        url = reverse('generate_pdf', kwargs={'patient_id': self.get_patient_id()})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Note: Testing actual PDF content would require PDF parsing libraries
        # For integration tests, we verify that PDF is generated successfully
        # and has reasonable size indicating content inclusion
        # Type assertion to tell Pylance this is a FileResponse
        assert isinstance(response, FileResponse)
        pdf_content = b''.join(response.streaming_content)  # type: ignore
        self.assertGreater(len(pdf_content), 4500)  # Substantial PDF with content
    
    def test_dietary_screening_data_display_in_pdf(self):
        """Test that dietary screening data appears correctly in generated PDF"""
        self.client.force_login(self.medical_user)
        url = reverse('generate_pdf', kwargs={'patient_id': self.get_patient_id()})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Type assertion to tell Pylance this is a FileResponse
        assert isinstance(response, FileResponse)
        pdf_content = b''.join(response.streaming_content)  # type: ignore
        self.assertGreater(len(pdf_content), 4500)
    
    def test_user_without_profile_can_generate_reports(self):
        """Test that users without Profile can still generate reports"""
        # Create user without profile
        user_no_profile = User.objects.create_user(
            username='noprofile',
            email='noprofile@test.com', 
            password='TestPass123!'
        )
        
        self.client.force_login(user_no_profile)
        url = reverse('report', kwargs={'patient_id': self.get_patient_id()})
        response = self.client.get(url)
        
        # Should work, but may have different professional recommendations
        self.assertEqual(response.status_code, 200)
    
    @patch('reports.views.get_ml_risk_prediction')
    def test_complete_workflow_integration(self, mock_ml_prediction):
        """Test complete workflow: view report -> save recommendation -> generate PDF -> send email"""
        mock_ml_prediction.return_value = {
            'available': True,
            'risk_level': 'high',
            'confidence': 89.3
        }
        
        self.client.force_login(self.dentist_user)
        
        # Step 1: View report
        view_url = reverse('report', kwargs={'patient_id': self.get_patient_id()})
        view_response = self.client.get(view_url)
        self.assertEqual(view_response.status_code, 200)
        
        # Step 2: Save recommendation via POST to generate_pdf
        pdf_url = reverse('generate_pdf', kwargs={'patient_id': self.get_patient_id()})
        post_response = self.client.post(pdf_url, {
            'recommended_professional': 'orthodontist'
        })
        self.assertEqual(post_response.status_code, 204)
        
        # Step 3: Generate PDF (GET request)
        pdf_response = self.client.get(pdf_url)
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
        
        # Step 4: Send email (mock PDF generation to avoid complexity)
        with patch('reports.views.generate_pdf_buffer') as mock_pdf_gen:
            mock_pdf_gen.return_value = io.BytesIO(b'test pdf')
            
            email_url = reverse('send_report_email', kwargs={'patient_id': self.get_patient_id()})
            email_response = self.client.post(email_url, {
                'recipient_email': 'patient@test.com',
                'cc_emails': 'prof@test.com',
                'subject': 'Complete Workflow Test',
                'message': 'Test message'
            })
            
            self.assertEqual(email_response.status_code, 200)
            # Should send 2 emails (patient + professional)
            self.assertEqual(len(mail.outbox), 2)
