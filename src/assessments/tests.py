from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.db.models.signals import post_save
import json

from patient.models import Patient
from userprofile.models import Profile
from .models import DentalScreening, DietaryScreening
from .factory import DentalFactory, DietaryFactory


class AssessmentIntegrationTestCase(TestCase):
    """Base test case for assessment integration tests."""
    
    def setUp(self):
        """Set up test data for all assessment tests."""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create profile for the user
        self.profile = Profile.objects.create(
            user=self.user,
            profession='dentist',
            tel='1234567890'
        )
        
        # Create test patient
        self.patient = Patient.objects.create(
            created_by=self.user,
            name='Test',
            surname='Patient',
            gender='0',
            age='5',
            parent_name='Parent',
            parent_surname='Test',
            parent_id='1234567890123',
            parent_contact='0987654321'
        )
        
        # Sample teeth data for dental screening tests
        self.sample_teeth_data = {
            f"tooth_{tooth}": "A" for tooth in 
            ["55", "54", "53", "52", "51", "61", "62", "63", "64", "65",
             "85", "84", "83", "82", "81", "71", "72", "73", "74", "75"]
        }
        
        # Login user for tests
        self.client.login(username='testuser', password='testpass123')


class DentalScreeningIntegrationTests(AssessmentIntegrationTestCase):
    """Integration tests for dental screening functionality."""
    
    def test_dental_screening_view_get_request(self):
        """Test GET request to dental screening view."""
        url = reverse('dental_screening', kwargs={'patient_id': self.patient.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dental Assessment Form")
        self.assertContains(response, 'sa_citizen')
        self.assertContains(response, 'special_needs')
        
    def test_dental_screening_view_with_from_dietary_parameter(self):
        """Test dental screening view when coming from dietary screening."""
        url = reverse('dental_screening', kwargs={'patient_id': self.patient.pk})
        response = self.client.get(url, {'from_dietary': 'true'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'from_dietary')
        
    def test_dental_screening_successful_submission(self):
        """Test successful dental screening form submission."""
        url = reverse('dental_screening', kwargs={'patient_id': self.patient.pk})
        
        form_data = {
            'sa_citizen': 'yes',
            'special_needs': 'no',
            'caregiver_treatment': 'yes',
            'appliance': 'no',
            'plaque': 'yes',
            'dry_mouth': 'no',
            'enamel_defects': 'yes',
            'fluoride_water': 'yes',
            'fluoride_toothpaste': 'yes',
            'topical_fluoride': 'no',
            'regular_checkups': 'yes',
            'sealed_pits': 'no',
            'restorative_procedures': 'yes',
            'enamel_change': 'no',
            'dentin_discoloration': 'yes',
            'white_spot_lesions': 'no',
            'cavitated_lesions': 'yes',
            'multiple_restorations': 'no',
            'missing_teeth': 'yes',
        }
        form_data.update(self.sample_teeth_data)
        
        response = self.client.post(url, form_data)
        
        # Should redirect to report page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('report', kwargs={'patient_id': self.patient.pk}))
        
        # Verify screening was created
        self.assertTrue(DentalScreening.objects.filter(patient=self.patient).exists())
        screening = DentalScreening.objects.get(patient=self.patient)
        self.assertEqual(screening.sa_citizen, 'yes')
        self.assertEqual(screening.special_needs, 'no')
        self.assertIsNotNone(screening.teeth_data)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("successfully" in str(m) for m in messages))
        
    def test_dental_screening_missing_required_fields(self):
        """Test dental screening form submission with missing required fields."""
        url = reverse('dental_screening', kwargs={'patient_id': self.patient.pk})
        
        # Submit form with missing fields
        form_data = {
            'sa_citizen': 'yes',
            # Missing other required fields
        }
        
        response = self.client.post(url, form_data)
        
        # Should not redirect, should show form with errors
        self.assertEqual(response.status_code, 200)
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Please answer all required questions" in str(m) for m in messages))
        
        # Verify no screening was created
        self.assertFalse(DentalScreening.objects.filter(patient=self.patient).exists())
        
    def test_dental_screening_update_existing(self):
        """Test updating existing dental screening."""
        # Create initial screening
        screening = DentalScreening.objects.create(
            patient=self.patient,
            sa_citizen='no',
            special_needs='no',
            caregiver_treatment='no',
            appliance='no',
            plaque='no',
            dry_mouth='no',
            enamel_defects='no',
            fluoride_water='no',
            fluoride_toothpaste='no',
            topical_fluoride='no',
            regular_checkups='no',
            sealed_pits='no',
            restorative_procedures='no',
            enamel_change='no',
            dentin_discoloration='no',
            white_spot_lesions='no',
            cavitated_lesions='no',
            multiple_restorations='no',
            missing_teeth='no',
            teeth_data={}
        )
        
        url = reverse('dental_screening', kwargs={'patient_id': self.patient.pk})
        
        # Update the screening
        form_data = {
            'sa_citizen': 'yes',  # Changed
            'special_needs': 'yes',  # Changed
            'caregiver_treatment': 'yes',
            'appliance': 'no',
            'plaque': 'yes',
            'dry_mouth': 'no',
            'enamel_defects': 'yes',
            'fluoride_water': 'yes',
            'fluoride_toothpaste': 'yes',
            'topical_fluoride': 'no',
            'regular_checkups': 'yes',
            'sealed_pits': 'no',
            'restorative_procedures': 'yes',
            'enamel_change': 'no',
            'dentin_discoloration': 'yes',
            'white_spot_lesions': 'no',
            'cavitated_lesions': 'yes',
            'multiple_restorations': 'no',
            'missing_teeth': 'yes',
        }
        form_data.update(self.sample_teeth_data)
        
        response = self.client.post(url, form_data)
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify screening was updated
        screening.refresh_from_db()
        self.assertEqual(screening.sa_citizen, 'yes')
        self.assertEqual(screening.special_needs, 'yes')
        
        # Should still be only one screening
        self.assertEqual(DentalScreening.objects.filter(patient=self.patient).count(), 1)
        
    def test_dental_screening_from_dietary_flow(self):
        """Test dental screening when coming from dietary screening."""
        url = reverse('dental_screening', kwargs={'patient_id': self.patient.pk})
        
        form_data = {
            'sa_citizen': 'yes',
            'special_needs': 'no',
            'caregiver_treatment': 'yes',
            'appliance': 'no',
            'plaque': 'yes',
            'dry_mouth': 'no',
            'enamel_defects': 'yes',
            'fluoride_water': 'yes',
            'fluoride_toothpaste': 'yes',
            'topical_fluoride': 'no',
            'regular_checkups': 'yes',
            'sealed_pits': 'no',
            'restorative_procedures': 'yes',
            'enamel_change': 'no',
            'dentin_discoloration': 'yes',
            'white_spot_lesions': 'no',
            'cavitated_lesions': 'yes',
            'multiple_restorations': 'no',
            'missing_teeth': 'yes',
        }
        form_data.update(self.sample_teeth_data)
        
        # Add from_dietary parameter
        response = self.client.post(f"{url}?from_dietary=true", form_data)
        
        self.assertEqual(response.status_code, 302)
        
        # Check success message mentions both screenings
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Both dietary and dental screenings completed" in str(m) for m in messages))
        
    def test_dental_screening_unauthorized_access(self):
        """Test accessing dental screening without login."""
        self.client.logout()
        url = reverse('dental_screening', kwargs={'patient_id': self.patient.pk})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        # Check that we're redirected by checking status code only


class DietaryScreeningIntegrationTests(AssessmentIntegrationTestCase):
    """Integration tests for dietary screening functionality."""
    
    def test_dietary_screening_view_get_request(self):
        """Test GET request to dietary screening view."""
        url = reverse('dietary_screening', kwargs={'patient_id': self.patient.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nutritional Screening Assessment")
        self.assertContains(response, 'sweet_sugary_foods')
        
    def test_dietary_screening_successful_submission(self):
        """Test successful dietary screening form submission."""
        url = reverse('dietary_screening', kwargs={'patient_id': self.patient.pk})
        
        form_data = {
            'sweet_sugary_foods': 'yes',
            'sweet_sugary_foods_daily': '1-3_day',
            'sweet_sugary_foods_weekly': '1-3_week',
            'sweet_sugary_foods_timing': 'with_meals',
            'sweet_sugary_foods_bedtime': 'no',
            'takeaways_processed_foods': 'no',
            'takeaways_processed_foods_daily': '',
            'takeaways_processed_foods_weekly': '',
            'fresh_fruit': 'yes',
            'fresh_fruit_daily': '3-4_day',
            'fresh_fruit_weekly': '3-4_week',
            'fresh_fruit_timing': 'between_meals',
            'fresh_fruit_bedtime': 'no',
            'cold_drinks_juices': 'no',
            'cold_drinks_juices_daily': '',
            'cold_drinks_juices_weekly': '',
            'cold_drinks_juices_timing': '',
            'cold_drinks_juices_bedtime': '',
            'processed_fruit': 'no',
            'processed_fruit_daily': '',
            'processed_fruit_weekly': '',
            'processed_fruit_timing': '',
            'processed_fruit_bedtime': '',
            'spreads': 'yes',
            'spreads_daily': '1-3_day',
            'spreads_weekly': '1-3_week',
            'spreads_timing': 'with_meals',
            'spreads_bedtime': 'no',
            'added_sugars': 'no',
            'added_sugars_daily': '',
            'added_sugars_weekly': '',
            'added_sugars_timing': '',
            'added_sugars_bedtime': '',
            'salty_snacks': 'no',
            'salty_snacks_daily': '',
            'salty_snacks_weekly': '',
            'salty_snacks_timing': '',
            'dairy_products': 'yes',
            'dairy_products_daily': '3-4_day',
            'dairy_products_weekly': '3-4_week',
            'vegetables': 'yes',
            'vegetables_daily': '1-3_day',
            'vegetables_weekly': '1-3_week',
            'water': 'yes',
            'water_timing': 'with_meals',
            'water_glasses': '2-4',
        }
        
        response = self.client.post(url, form_data)
        
        # Should redirect to report page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('report', kwargs={'patient_id': self.patient.pk}))
        
        # Verify screening was created
        self.assertTrue(DietaryScreening.objects.filter(patient=self.patient).exists())
        screening = DietaryScreening.objects.get(patient=self.patient)
        self.assertEqual(screening.sweet_sugary_foods, 'yes')
        self.assertEqual(screening.takeaways_processed_foods, 'no')
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("successfully" in str(m) for m in messages))
        
    def test_dietary_screening_missing_main_questions(self):
        """Test dietary screening with missing main questions."""
        url = reverse('dietary_screening', kwargs={'patient_id': self.patient.pk})
        
        form_data = {
            # Missing sweet_sugary_foods
            'takeaways_processed_foods': 'no',
            # Missing other main questions
        }
        
        response = self.client.post(url, form_data)
        
        # Should not redirect, should show form with errors
        self.assertEqual(response.status_code, 200)
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Please answer all required questions" in str(m) for m in messages))
        
    def test_dietary_screening_missing_frequency_questions(self):
        """Test dietary screening with missing frequency questions when main is 'yes'."""
        url = reverse('dietary_screening', kwargs={'patient_id': self.patient.pk})
        
        form_data = {
            'sweet_sugary_foods': 'yes',
            # Missing frequency questions for sweet_sugary_foods
            'takeaways_processed_foods': 'no',
            'fresh_fruit': 'no',
            'cold_drinks_juices': 'no',
            'processed_fruit': 'no',
            'spreads': 'no',
            'added_sugars': 'no',
            'salty_snacks': 'no',
            'dairy_products': 'no',
            'vegetables': 'no',
            'water': 'no',
        }
        
        response = self.client.post(url, form_data)
        
        # Should not redirect due to missing frequency questions
        self.assertEqual(response.status_code, 200)
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Please answer all required questions" in str(m) for m in messages))
        
    def test_dietary_screening_proceed_to_dental(self):
        """Test proceeding from dietary to dental screening."""
        url = reverse('dietary_screening', kwargs={'patient_id': self.patient.pk})
        
        form_data = {
            'sweet_sugary_foods': 'no',
            'takeaways_processed_foods': 'no',
            'fresh_fruit': 'no',
            'cold_drinks_juices': 'no',
            'processed_fruit': 'no',
            'spreads': 'no',
            'added_sugars': 'no',
            'salty_snacks': 'no',
            'dairy_products': 'no',
            'vegetables': 'no',
            'water': 'no',
            'proceed_to_dental': 'true'
        }
        
        response = self.client.post(url, form_data)
        
        # Should redirect to dental screening
        expected_url = reverse('dental_screening', kwargs={'patient_id': self.patient.pk}) + '?from_dietary=true'
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url)
        
    def test_dietary_screening_perform_both_parameter(self):
        """Test dietary screening with perform_both parameter."""
        url = reverse('dietary_screening', kwargs={'patient_id': self.patient.pk})
        response = self.client.get(url, {'perform_both': 'true'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'perform_both')
        
    def test_dietary_screening_update_existing(self):
        """Test updating existing dietary screening."""
        # Create initial screening
        screening = DietaryScreening.objects.create(
            patient=self.patient,
            sweet_sugary_foods='no',
            takeaways_processed_foods='no',
            fresh_fruit='no',
            cold_drinks_juices='no',
            processed_fruit='no',
            spreads='no',
            added_sugars='no',
            salty_snacks='no',
            dairy_products='no',
            vegetables='no',
            water='no'
        )
        
        url = reverse('dietary_screening', kwargs={'patient_id': self.patient.pk})
        
        form_data = {
            'sweet_sugary_foods': 'yes',  # Changed
            'sweet_sugary_foods_daily': '1-3_day',
            'sweet_sugary_foods_weekly': '1-3_week',
            'sweet_sugary_foods_timing': 'with_meals',
            'sweet_sugary_foods_bedtime': 'no',
            'takeaways_processed_foods': 'no',
            'takeaways_processed_foods_daily': '',
            'takeaways_processed_foods_weekly': '',
            'fresh_fruit': 'no',
            'fresh_fruit_daily': '',
            'fresh_fruit_weekly': '',
            'fresh_fruit_timing': '',
            'fresh_fruit_bedtime': '',
            'cold_drinks_juices': 'no',
            'cold_drinks_juices_daily': '',
            'cold_drinks_juices_weekly': '',
            'cold_drinks_juices_timing': '',
            'cold_drinks_juices_bedtime': '',
            'processed_fruit': 'no',
            'processed_fruit_daily': '',
            'processed_fruit_weekly': '',
            'processed_fruit_timing': '',
            'processed_fruit_bedtime': '',
            'spreads': 'no',
            'spreads_daily': '',
            'spreads_weekly': '',
            'spreads_timing': '',
            'spreads_bedtime': '',
            'added_sugars': 'no',
            'added_sugars_daily': '',
            'added_sugars_weekly': '',
            'added_sugars_timing': '',
            'added_sugars_bedtime': '',
            'salty_snacks': 'no',
            'salty_snacks_daily': '',
            'salty_snacks_weekly': '',
            'salty_snacks_timing': '',
            'dairy_products': 'no',
            'dairy_products_daily': '',
            'dairy_products_weekly': '',
            'vegetables': 'no',
            'vegetables_daily': '',
            'vegetables_weekly': '',
            'water': 'no',
            'water_timing': '',
            'water_glasses': '',
        }
        
        response = self.client.post(url, form_data)
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify screening was updated
        screening.refresh_from_db()
        self.assertEqual(screening.sweet_sugary_foods, 'yes')
        
        # Should still be only one screening
        self.assertEqual(DietaryScreening.objects.filter(patient=self.patient).count(), 1)


class DietaryScreeningModelValidationTests(TestCase):
    """Tests for DietaryScreening model validation logic."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            created_by=self.user,
            name='Test',
            surname='Patient',
            gender='0',
            age='3',
            parent_name='Parent',
            parent_surname='Test',
            parent_id='1234567890123',
            parent_contact='0987654321'
        )
        
    def test_dietary_screening_clean_method_clears_subfields(self):
        """Test that clean method clears sub-fields when main field is 'no'."""
        screening = DietaryScreening(
            patient=self.patient,
            sweet_sugary_foods='no',
            sweet_sugary_foods_daily='1-3_day',  # Should be cleared
            sweet_sugary_foods_timing='with_meals',  # Should be cleared
            takeaways_processed_foods='yes',
            takeaways_processed_foods_daily='1-3_day',  # Should remain
            fresh_fruit='no',
            cold_drinks_juices='no',
            processed_fruit='no',
            spreads='no',
            added_sugars='no',
            salty_snacks='no',
            dairy_products='no',
            vegetables='no',
            water='no'
        )
        
        screening.clean()
        
        # Fields for 'no' answers should be cleared
        self.assertIsNone(screening.sweet_sugary_foods_daily)
        self.assertIsNone(screening.sweet_sugary_foods_timing)
        
        # Fields for 'yes' answers should remain
        self.assertEqual(screening.takeaways_processed_foods_daily, '1-3_day')
        
    def test_dietary_screening_save_calls_clean(self):
        """Test that save method calls clean to validate data."""
        screening = DietaryScreening.objects.create(
            patient=self.patient,
            sweet_sugary_foods='no',
            sweet_sugary_foods_daily='1-3_day',  # Should be cleared on save
            takeaways_processed_foods='no',
            fresh_fruit='no',
            cold_drinks_juices='no',
            processed_fruit='no',
            spreads='no',
            added_sugars='no',
            salty_snacks='no',
            dairy_products='no',
            vegetables='no',
            water='no'
        )
        
        # Refresh from database to see if clean was applied
        screening.refresh_from_db()
        self.assertIsNone(screening.sweet_sugary_foods_daily)


class AssessmentFactoryIntegrationTests(TestCase):
    """Tests for assessment factories and their integration with models."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_dental_factory_creates_valid_instance(self):
        """Test that DentalFactory creates valid DentalScreening instances."""
        screening = DentalFactory()
        
        # Should have all required fields
        self.assertIsNotNone(screening.patient)
        self.assertIn(screening.sa_citizen, ['yes', 'no'])
        self.assertIn(screening.special_needs, ['yes', 'no'])
        self.assertIsInstance(screening.teeth_data, dict)
        
        # Should save successfully
        screening.save()
        self.assertIsNotNone(screening.pk)
        
    def test_dental_factory_with_existing_patient(self):
        """Test DentalFactory with an existing patient."""
        patient = Patient.objects.create(
            created_by=self.user,
            name='Test',
            surname='Patient',
            gender='0',
            age='4',
            parent_name='Parent',
            parent_surname='Test',
            parent_id='1234567890123',
            parent_contact='0987654321'
        )
        
        screening = DentalFactory(patient=patient)
        
        self.assertEqual(screening.patient, patient)
        screening.save()
        
        # Verify relationship
        dental_screenings = DentalScreening.objects.filter(patient=patient)
        self.assertTrue(dental_screenings.filter(pk=screening.pk).exists())
        
    def test_dietary_factory_creates_valid_instance(self):
        """Test that DietaryFactory creates valid DietaryScreening instances."""
        screening = DietaryFactory()
        
        # Should have all required fields
        self.assertIsNotNone(screening.patient)
        self.assertIn(screening.sweet_sugary_foods, ['yes', 'no'])
        self.assertIn(screening.water, ['yes', 'no'])
        
        # Should save successfully
        screening.save()
        self.assertIsNotNone(screening.pk)
        
    def test_dietary_factory_with_existing_patient(self):
        """Test DietaryFactory with an existing patient."""
        patient = Patient.objects.create(
            created_by=self.user,
            name='Test',
            surname='Patient',
            gender='0',
            age='4',
            parent_name='Parent',
            parent_surname='Test',
            parent_id='1234567890123',
            parent_contact='0987654321'
        )
        
        screening = DietaryFactory(patient=patient)
        
        self.assertEqual(screening.patient, patient)
        screening.save()
        
        # Verify relationship
        dietary_screenings = DietaryScreening.objects.filter(patient=patient)
        self.assertTrue(dietary_screenings.filter(pk=screening.pk).exists())


class AssessmentErrorHandlingTests(AssessmentIntegrationTestCase):
    """Tests for error handling in assessment views."""
    
    def test_dental_screening_nonexistent_patient(self):
        """Test dental screening with non-existent patient ID."""
        url = reverse('dental_screening', kwargs={'patient_id': 999999})
        
        # The view raises DoesNotExist exception for non-existent patients
        with self.assertRaises(Patient.DoesNotExist):
            response = self.client.get(url)
        
    def test_dietary_screening_nonexistent_patient(self):
        """Test dietary screening with non-existent patient ID."""
        url = reverse('dietary_screening', kwargs={'patient_id': 999999})
        
        # The view raises DoesNotExist exception for non-existent patients
        with self.assertRaises(Patient.DoesNotExist):
            response = self.client.get(url)
        
    def test_dental_screening_form_exception_handling(self):
        """Test dental screening form submission with invalid data causing exception."""
        url = reverse('dental_screening', kwargs={'patient_id': self.patient.pk})
        
        # Create form data with all required fields but potentially problematic teeth data
        form_data = {
            'sa_citizen': 'yes',
            'special_needs': 'no',
            'caregiver_treatment': 'yes',
            'appliance': 'no',
            'plaque': 'yes',
            'dry_mouth': 'no',
            'enamel_defects': 'yes',
            'fluoride_water': 'yes',
            'fluoride_toothpaste': 'yes',
            'topical_fluoride': 'no',
            'regular_checkups': 'yes',
            'sealed_pits': 'no',
            'restorative_procedures': 'yes',
            'enamel_change': 'no',
            'dentin_discoloration': 'yes',
            'white_spot_lesions': 'no',
            'cavitated_lesions': 'yes',
            'multiple_restorations': 'no',
            'missing_teeth': 'yes',
        }
        form_data.update(self.sample_teeth_data)
        
        # Should handle any exceptions gracefully
        response = self.client.post(url, form_data)
        
        # Should either succeed or show error message, not crash
        self.assertIn(response.status_code, [200, 302])


class AssessmentWorkflowIntegrationTests(AssessmentIntegrationTestCase):
    """Tests for complete assessment workflows."""
    
    def test_complete_dietary_to_dental_workflow(self):
        """Test complete workflow from dietary screening to dental screening to report."""
        # Step 1: Complete dietary screening
        dietary_url = reverse('dietary_screening', kwargs={'patient_id': self.patient.pk})
        dietary_data = {
            'sweet_sugary_foods': 'yes',
            'sweet_sugary_foods_daily': '1-3_day',
            'sweet_sugary_foods_weekly': '1-3_week',
            'sweet_sugary_foods_timing': 'with_meals',
            'sweet_sugary_foods_bedtime': 'no',
            'takeaways_processed_foods': 'no',
            'takeaways_processed_foods_daily': '',
            'takeaways_processed_foods_weekly': '',
            'fresh_fruit': 'no',
            'fresh_fruit_daily': '',
            'fresh_fruit_weekly': '',
            'fresh_fruit_timing': '',
            'fresh_fruit_bedtime': '',
            'cold_drinks_juices': 'no',
            'cold_drinks_juices_daily': '',
            'cold_drinks_juices_weekly': '',
            'cold_drinks_juices_timing': '',
            'cold_drinks_juices_bedtime': '',
            'processed_fruit': 'no',
            'processed_fruit_daily': '',
            'processed_fruit_weekly': '',
            'processed_fruit_timing': '',
            'processed_fruit_bedtime': '',
            'spreads': 'no',
            'spreads_daily': '',
            'spreads_weekly': '',
            'spreads_timing': '',
            'spreads_bedtime': '',
            'added_sugars': 'no',
            'added_sugars_daily': '',
            'added_sugars_weekly': '',
            'added_sugars_timing': '',
            'added_sugars_bedtime': '',
            'salty_snacks': 'no',
            'salty_snacks_daily': '',
            'salty_snacks_weekly': '',
            'salty_snacks_timing': '',
            'dairy_products': 'no',
            'dairy_products_daily': '',
            'dairy_products_weekly': '',
            'vegetables': 'no',
            'vegetables_daily': '',
            'vegetables_weekly': '',
            'water': 'no',
            'water_timing': '',
            'water_glasses': '',
            'proceed_to_dental': 'true'
        }
        
        response = self.client.post(dietary_url, dietary_data)
        
        # Should redirect to dental screening
        self.assertEqual(response.status_code, 302)
        
        # Follow redirect to dental screening - get the redirect location
        redirect_location = response.get('Location')
        if redirect_location:
            dental_url = redirect_location
            response = self.client.get(redirect_location)
            self.assertEqual(response.status_code, 200)
        else:
            # Fallback - construct the dental URL manually
            dental_url = reverse('dental_screening', kwargs={'patient_id': self.patient.pk}) + '?from_dietary=true'
            response = self.client.get(dental_url)
            self.assertEqual(response.status_code, 200)
        
        # Step 2: Complete dental screening
        dental_data = {
            'sa_citizen': 'yes',
            'special_needs': 'no',
            'caregiver_treatment': 'yes',
            'appliance': 'no',
            'plaque': 'yes',
            'dry_mouth': 'no',
            'enamel_defects': 'yes',
            'fluoride_water': 'yes',
            'fluoride_toothpaste': 'yes',
            'topical_fluoride': 'no',
            'regular_checkups': 'yes',
            'sealed_pits': 'no',
            'restorative_procedures': 'yes',
            'enamel_change': 'no',
            'dentin_discoloration': 'yes',
            'white_spot_lesions': 'no',
            'cavitated_lesions': 'yes',
            'multiple_restorations': 'no',
            'missing_teeth': 'yes',
        }
        dental_data.update(self.sample_teeth_data)
        
        response = self.client.post(dental_url, dental_data)
        
        # Should redirect to report
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('report', kwargs={'patient_id': self.patient.pk}))
        
        # Verify both screenings exist
        self.assertTrue(DietaryScreening.objects.filter(patient=self.patient).exists())
        self.assertTrue(DentalScreening.objects.filter(patient=self.patient).exists())
        
        # Check final success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Both dietary and dental screenings completed" in str(m) for m in messages))
        
    def test_standalone_dental_screening_workflow(self):
        """Test standalone dental screening workflow."""
        url = reverse('dental_screening', kwargs={'patient_id': self.patient.pk})
        
        dental_data = {
            'sa_citizen': 'yes',
            'special_needs': 'no',
            'caregiver_treatment': 'yes',
            'appliance': 'no',
            'plaque': 'yes',
            'dry_mouth': 'no',
            'enamel_defects': 'yes',
            'fluoride_water': 'yes',
            'fluoride_toothpaste': 'yes',
            'topical_fluoride': 'no',
            'regular_checkups': 'yes',
            'sealed_pits': 'no',
            'restorative_procedures': 'yes',
            'enamel_change': 'no',
            'dentin_discoloration': 'yes',
            'white_spot_lesions': 'no',
            'cavitated_lesions': 'yes',
            'multiple_restorations': 'no',
            'missing_teeth': 'yes',
        }
        dental_data.update(self.sample_teeth_data)
        
        response = self.client.post(url, dental_data)
        
        # Should redirect to report
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('report', kwargs={'patient_id': self.patient.pk}))
        
        # Verify screening exists
        self.assertTrue(DentalScreening.objects.filter(patient=self.patient).exists())
        
        # Check success message for single screening
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Dental screening completed successfully" in str(m) for m in messages))
        
    def test_standalone_dietary_screening_workflow(self):
        """Test standalone dietary screening workflow."""
        url = reverse('dietary_screening', kwargs={'patient_id': self.patient.pk})
        
        dietary_data = {
            'sweet_sugary_foods': 'no',
            'sweet_sugary_foods_daily': '',
            'sweet_sugary_foods_weekly': '',
            'sweet_sugary_foods_timing': '',
            'sweet_sugary_foods_bedtime': '',
            'takeaways_processed_foods': 'no',
            'takeaways_processed_foods_daily': '',
            'takeaways_processed_foods_weekly': '',
            'fresh_fruit': 'yes',
            'fresh_fruit_daily': '1-3_day',
            'fresh_fruit_weekly': '1-3_week',
            'fresh_fruit_timing': 'with_meals',
            'fresh_fruit_bedtime': 'no',
            'cold_drinks_juices': 'no',
            'cold_drinks_juices_daily': '',
            'cold_drinks_juices_weekly': '',
            'cold_drinks_juices_timing': '',
            'cold_drinks_juices_bedtime': '',
            'processed_fruit': 'no',
            'processed_fruit_daily': '',
            'processed_fruit_weekly': '',
            'processed_fruit_timing': '',
            'processed_fruit_bedtime': '',
            'spreads': 'no',
            'spreads_daily': '',
            'spreads_weekly': '',
            'spreads_timing': '',
            'spreads_bedtime': '',
            'added_sugars': 'no',
            'added_sugars_daily': '',
            'added_sugars_weekly': '',
            'added_sugars_timing': '',
            'added_sugars_bedtime': '',
            'salty_snacks': 'no',
            'salty_snacks_daily': '',
            'salty_snacks_weekly': '',
            'salty_snacks_timing': '',
            'dairy_products': 'yes',
            'dairy_products_daily': '3-4_day',
            'dairy_products_weekly': '3-4_week',
            'vegetables': 'yes',
            'vegetables_daily': '1-3_day',
            'vegetables_weekly': '1-3_week',
            'water': 'yes',
            'water_timing': 'with_meals',
            'water_glasses': '2-4',
        }
        
        response = self.client.post(url, dietary_data)
        
        # Should redirect to report
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('report', kwargs={'patient_id': self.patient.pk}))
        
        # Verify screening exists
        self.assertTrue(DietaryScreening.objects.filter(patient=self.patient).exists())
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Dietary screening completed successfully" in str(m) for m in messages))


class AssessmentModelIntegrationTests(TestCase):
    """Tests for model-level integration functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            created_by=self.user,
            name='Test',
            surname='Patient',
            gender='0',
            age='3',
            parent_name='Parent',
            parent_surname='Test',
            parent_id='1234567890123',
            parent_contact='0987654321'
        )
        
    def test_dental_screening_model_relationships(self):
        """Test DentalScreening model relationships work correctly."""
        screening = DentalScreening.objects.create(
            patient=self.patient,
            sa_citizen='yes',
            special_needs='no',
            caregiver_treatment='yes',
            appliance='no',
            plaque='yes',
            dry_mouth='no',
            enamel_defects='yes',
            fluoride_water='yes',
            fluoride_toothpaste='yes',
            topical_fluoride='no',
            regular_checkups='yes',
            sealed_pits='no',
            restorative_procedures='yes',
            enamel_change='no',
            dentin_discoloration='yes',
            white_spot_lesions='no',
            cavitated_lesions='yes',
            multiple_restorations='no',
            missing_teeth='yes',
            teeth_data={}
        )
        
        # Test forward relationship
        self.assertEqual(screening.patient, self.patient)
        
        # Test reverse relationship
        dental_screenings = DentalScreening.objects.filter(patient=self.patient)
        self.assertTrue(dental_screenings.filter(pk=screening.pk).exists())
        self.assertEqual(dental_screenings.first(), screening)
        
    def test_dietary_screening_model_relationships(self):
        """Test DietaryScreening model relationships work correctly."""
        screening = DietaryScreening.objects.create(
            patient=self.patient,
            sweet_sugary_foods='yes',
            takeaways_processed_foods='no',
            fresh_fruit='yes',
            cold_drinks_juices='no',
            processed_fruit='no',
            spreads='yes',
            added_sugars='no',
            salty_snacks='no',
            dairy_products='yes',
            vegetables='yes',
            water='yes'
        )
        
        # Test forward relationship
        self.assertEqual(screening.patient, self.patient)
        
        # Test reverse relationship
        dietary_screenings = DietaryScreening.objects.filter(patient=self.patient)
        self.assertTrue(dietary_screenings.filter(pk=screening.pk).exists())
        self.assertEqual(dietary_screenings.first(), screening)
        
    def test_multiple_screenings_for_patient(self):
        """Test that a patient can have multiple screenings (though not typical workflow)."""
        # Create dental screening
        dental = DentalScreening.objects.create(
            patient=self.patient,
            sa_citizen='yes',
            special_needs='no',
            caregiver_treatment='yes',
            appliance='no',
            plaque='yes',
            dry_mouth='no',
            enamel_defects='yes',
            fluoride_water='yes',
            fluoride_toothpaste='yes',
            topical_fluoride='no',
            regular_checkups='yes',
            sealed_pits='no',
            restorative_procedures='yes',
            enamel_change='no',
            dentin_discoloration='yes',
            white_spot_lesions='no',
            cavitated_lesions='yes',
            multiple_restorations='no',
            missing_teeth='yes',
            teeth_data={}
        )
        
        # Create dietary screening
        dietary = DietaryScreening.objects.create(
            patient=self.patient,
            sweet_sugary_foods='yes',
            takeaways_processed_foods='no',
            fresh_fruit='yes',
            cold_drinks_juices='no',
            processed_fruit='no',
            spreads='yes',
            added_sugars='no',
            salty_snacks='no',
            dairy_products='yes',
            vegetables='yes',
            water='yes'
        )
        
        # Verify both screenings are associated with patient
        dental_screenings = DentalScreening.objects.filter(patient=self.patient)
        dietary_screenings = DietaryScreening.objects.filter(patient=self.patient)
        
        self.assertEqual(dental_screenings.count(), 1)
        self.assertEqual(dietary_screenings.count(), 1)
        self.assertEqual(dental_screenings.first(), dental)
        self.assertEqual(dietary_screenings.first(), dietary)
