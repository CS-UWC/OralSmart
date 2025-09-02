from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.http import JsonResponse
from unittest.mock import patch, Mock
import tempfile
import os
import json
import io

from .models import Profile
from .forms import ProfilePictureForm

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

User = get_user_model()


def create_test_image(name='test.png', size=(10, 10), format='PNG'):
    """Create a valid test image file."""
    if HAS_PIL:
        # Use PIL to create a real image
        from PIL import Image as PILImage
        image = PILImage.new('RGB', size, color='red')
        temp_file = io.BytesIO()
        image.save(temp_file, format=format)
        temp_file.seek(0)
        content = temp_file.read()
    else:
        # Fallback: Use a minimal valid PNG
        content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    
    return SimpleUploadedFile(
        name=name,
        content=content,
        content_type=f'image/{format.lower()}'
    )


class UserProfileIntegrationTestCase(TestCase):
    """Base test case for userprofile integration tests."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        
        # Create test profile
        self.profile = Profile.objects.create(
            user=self.user,
            profession='dentist',
            health_professional_body='HPCSA',
            reg_num='TEST123456',
            email=self.user.email,
            address='123 Test Street, Test City',
            tel='+27123456789'
        )
        
        # Create another user for testing
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='OtherPass123!',
            first_name='Other',
            last_name='User',
            is_active=True
        )


class ProfileViewIntegrationTests(UserProfileIntegrationTestCase):
    """Integration tests for profile view functionality."""
    
    def test_profile_view_requires_authentication(self):
        """Test that profile view requires user to be logged in."""
        response = self.client.get(reverse('profile'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/login_user/'))
    
    def test_profile_view_get_request_authenticated(self):
        """Test GET request to profile view for authenticated user."""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userprofile/profile.html')
        
        # Verify context data
        context = response.context
        self.assertEqual(context['first_name'], 'Test')
        self.assertEqual(context['last_name'], 'User')
        self.assertEqual(context['email'], 'testuser@example.com')
        self.assertEqual(context['phone'], '+27123456789')
        self.assertEqual(context['address'], '123 Test Street, Test City')
        self.assertEqual(context['profession'], 'dentist')
        self.assertFalse(context['show_navbar'])
        self.assertIsInstance(context['form'], ProfilePictureForm)
    
    def test_profile_view_creates_missing_profile(self):
        """Test that profile view creates profile if it doesn't exist."""
        # Login with user who doesn't have a profile
        self.client.login(username='otheruser', password='OtherPass123!')
        
        # Verify no profile exists initially
        self.assertFalse(Profile.objects.filter(user=self.other_user).exists())
        
        response = self.client.get(reverse('profile'))
        
        self.assertEqual(response.status_code, 200)
        
        # Verify profile was created
        self.assertTrue(Profile.objects.filter(user=self.other_user).exists())
        profile = Profile.objects.get(user=self.other_user)
        self.assertEqual(profile.profession, 'dentist')  # Default value
        self.assertEqual(profile.health_professional_body, 'HPCSA')  # Default value
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_profile_picture_upload_successful(self):
        """Test successful profile picture upload."""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Create test image file using helper
        uploaded_file = create_test_image('test_image.png')
        
        form_data = {'profile_pic': uploaded_file}
        
        response = self.client.post(reverse('profile'), form_data)
        
        # Should redirect to profile after successful upload
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        
        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Profile picture updated successfully" in str(m) for m in messages))
        
        # Verify profile picture was saved
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.profile_pic.name.startswith('profile/'))
    
    def test_profile_picture_upload_invalid_file(self):
        """Test profile picture upload with invalid file."""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Create invalid file (text instead of image)
        invalid_file = SimpleUploadedFile(
            name='test.txt',
            content=b'This is not an image',
            content_type='text/plain'
        )
        
        form_data = {'profile_pic': invalid_file}
        
        response = self.client.post(reverse('profile'), form_data)
        
        # Should stay on profile page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userprofile/profile.html')
        
        # Verify error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Error updating profile picture" in str(m) for m in messages))
    
    def test_profile_picture_upload_no_file(self):
        """Test profile picture form submission with no file."""
        self.client.login(username='testuser', password='TestPass123!')
        
        form_data = {}  # No file uploaded
        
        response = self.client.post(reverse('profile'), form_data)
        
        # With no file, form is valid but no actual update happens
        # Should redirect back to profile page (this is the actual behavior)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))


class ProfileModelIntegrationTests(UserProfileIntegrationTestCase):
    """Integration tests for Profile model functionality."""
    
    def test_profile_model_creation(self):
        """Test Profile model creation with all fields."""
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='NewPass123!',
        )
        
        profile = Profile.objects.create(
            user=new_user,
            profession='medical_doctor',
            health_professional_body='HPCSA',
            reg_num='MD123456',
            email='newuser@example.com',
            address='456 New Street',
            tel='+27987654321'
        )
        
        # Verify profile was created correctly
        self.assertEqual(profile.user, new_user)
        self.assertEqual(profile.profession, 'medical_doctor')
        self.assertEqual(profile.health_professional_body, 'HPCSA')
        self.assertEqual(profile.reg_num, 'MD123456')
        self.assertEqual(profile.email, 'newuser@example.com')
        self.assertEqual(profile.address, '456 New Street')
        self.assertEqual(profile.tel, '+27987654321')
    
    def test_profile_model_defaults(self):
        """Test Profile model with default values."""
        new_user = User.objects.create_user(
            username='defaultuser',
            email='default@example.com',
            password='DefaultPass123!',
        )
        
        profile = Profile.objects.create(user=new_user)
        
        # Verify default values
        self.assertEqual(profile.profession, 'dentist')
        self.assertEqual(profile.health_professional_body, 'HPCSA')
        self.assertEqual(profile.reg_num, '0')
    
    def test_profile_model_one_to_one_relationship(self):
        """Test that Profile has one-to-one relationship with User."""
        # Try to create second profile for same user
        with self.assertRaises(Exception):
            Profile.objects.create(
                user=self.user,  # Already has a profile
                profession='medical_doctor'
            )
    
    def test_profile_model_cascade_delete(self):
        """Test that profile is deleted when user is deleted."""
        new_user = User.objects.create_user(
            username='deleteuser',
            email='delete@example.com',
            password='DeletePass123!',
        )
        
        profile = Profile.objects.create(user=new_user)
        profile_pk = profile.pk
        
        # Verify profile exists
        self.assertTrue(Profile.objects.filter(pk=profile_pk).exists())
        
        # Delete user
        new_user.delete()
        
        # Verify profile is also deleted (CASCADE)
        self.assertFalse(Profile.objects.filter(pk=profile_pk).exists())
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp(), MEDIA_URL='/test_media/')
    def test_profile_picture_url_with_existing_file(self):
        """Test profile picture URL when file exists."""
        # Create a temporary image file and save it to profile
        test_image = create_test_image('test_pic.jpg', format='JPEG')
        
        # Save the image to the profile
        from django.core.files.base import ContentFile
        self.profile.profile_pic.save(
            'test_pic.jpg',
            ContentFile(test_image.read()),
            save=True
        )
        
        # The URL should start with the media URL and contain 'profile/'
        url = self.profile.get_profile_picture_url()
        self.assertTrue(url.startswith('/test_media/profile/'))
        self.assertTrue('test_pic' in url)  # Original name should be in there somewhere
        
        # Test property version too
        self.assertEqual(self.profile.profile_picture_url, url)
    
    @override_settings(MEDIA_URL='/test_media/')
    def test_profile_picture_url_without_file(self):
        """Test profile picture URL when no file exists."""
        # Profile has no picture file - delete the file field
        if self.profile.profile_pic:
            self.profile.profile_pic.delete(save=False)
        self.profile.save()
        
        expected_url = '/test_media/images/default/default_profile_pic.jpg'
        self.assertEqual(self.profile.get_profile_picture_url(), expected_url)
        self.assertEqual(self.profile.profile_picture_url, expected_url)
    
    def test_profile_profession_choices(self):
        """Test that all profession choices are valid."""
        valid_professions = [choice[0] for choice in Profile.PROFESSIONS]
        
        # Test HPCSA professions
        hpcsa_professions = [
            'medical_doctor', 'dentist', 'psychologist', 'physiotherapist',
            'radiographer', 'occupational_therapist', 'biokineticist',
            'clinical_technologist', 'dietitian', 'audiologist',
            'optometrist', 'emergency_care_practitioner'
        ]
        
        for profession in hpcsa_professions:
            self.assertIn(profession, valid_professions)
        
        # Test SANC professions
        sanc_professions = [
            'registered_nurse', 'enrolled_nurse', 'nursing_assistant', 'midwife'
        ]
        
        for profession in sanc_professions:
            self.assertIn(profession, valid_professions)
    
    def test_profile_health_body_choices(self):
        """Test that all health body choices are valid."""
        valid_bodies = [choice[0] for choice in Profile.HEALTH_BODIES]
        
        expected_bodies = ['HPCSA', 'SANC']
        
        for body in expected_bodies:
            self.assertIn(body, valid_bodies)


class GetProfessionsViewIntegrationTests(UserProfileIntegrationTestCase):
    """Integration tests for get_professions AJAX view."""
    
    def test_get_professions_hpcsa(self):
        """Test getting professions for HPCSA."""
        response = self.client.get(reverse('get_professions'), {'body': 'HPCSA'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        
        # Parse JSON response
        data = json.loads(response.content.decode('utf-8'))
        professions = data['professions']
        
        # Verify HPCSA professions are returned
        expected_professions = [
            'medical_doctor', 'dentist', 'psychologist', 'physiotherapist',
            'radiographer', 'occupational_therapist', 'biokineticist',
            'clinical_technologist', 'dietitian', 'audiologist',
            'optometrist', 'emergency_care_practitioner'
        ]
        
        returned_values = [prof['value'] for prof in professions]
        for expected in expected_professions:
            self.assertIn(expected, returned_values)
        
        # Verify structure
        self.assertTrue(all('value' in prof and 'text' in prof for prof in professions))
    
    def test_get_professions_sanc(self):
        """Test getting professions for SANC."""
        response = self.client.get(reverse('get_professions'), {'body': 'SANC'})
        
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response
        data = json.loads(response.content.decode('utf-8'))
        professions = data['professions']
        
        # Verify SANC professions are returned
        expected_professions = [
            'registered_nurse', 'enrolled_nurse', 'nursing_assistant', 'midwife'
        ]
        
        returned_values = [prof['value'] for prof in professions]
        for expected in expected_professions:
            self.assertIn(expected, returned_values)
    
    def test_get_professions_unknown_body(self):
        """Test getting professions for unknown health body."""
        response = self.client.get(reverse('get_professions'), {'body': 'UNKNOWN'})
        
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response
        data = json.loads(response.content.decode('utf-8'))
        professions = data['professions']
        
        # Should return empty list
        self.assertEqual(professions, [])
    
    def test_get_professions_no_body_parameter(self):
        """Test getting professions without body parameter."""
        response = self.client.get(reverse('get_professions'))
        
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response
        data = json.loads(response.content.decode('utf-8'))
        professions = data['professions']
        
        # Should return empty list
        self.assertEqual(professions, [])
    
    def test_get_professions_ajax_structure(self):
        """Test that get_professions returns proper AJAX structure."""
        response = self.client.get(reverse('get_professions'), {'body': 'HPCSA'})
        
        # Verify JSON response
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content.decode('utf-8'))
        
        # Verify structure
        self.assertIn('professions', data)
        self.assertIsInstance(data['professions'], list)
        
        if data['professions']:  # If not empty
            profession = data['professions'][0]
            self.assertIn('value', profession)
            self.assertIn('text', profession)
            self.assertIsInstance(profession['value'], str)
            self.assertIsInstance(profession['text'], str)


class ProfilePictureFormIntegrationTests(UserProfileIntegrationTestCase):
    """Integration tests for ProfilePictureForm."""
    
    def test_profile_picture_form_valid_image(self):
        """Test ProfilePictureForm with valid image."""
        # Create test image file using helper
        uploaded_file = create_test_image('test_image.png')
        
        form = ProfilePictureForm(
            data={},
            files={'profile_pic': uploaded_file},
            instance=self.profile
        )
        
        self.assertTrue(form.is_valid())
    
    def test_profile_picture_form_no_file(self):
        """Test ProfilePictureForm with no file."""
        form = ProfilePictureForm(data={}, files={}, instance=self.profile)
        
        # Should be valid (file is optional for update)
        self.assertTrue(form.is_valid())
    
    def test_profile_picture_form_invalid_file_type(self):
        """Test ProfilePictureForm with invalid file type."""
        # Create text file instead of image
        text_file = SimpleUploadedFile(
            name='test.txt',
            content=b'This is not an image',
            content_type='text/plain'
        )
        
        form = ProfilePictureForm(
            data={},
            files={'profile_pic': text_file},
            instance=self.profile
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('profile_pic', form.errors)
    
    def test_profile_picture_form_widget_attributes(self):
        """Test that ProfilePictureForm has correct widget attributes."""
        form = ProfilePictureForm(instance=self.profile)
        
        widget = form.fields['profile_pic'].widget
        attrs = widget.attrs
        
        self.assertEqual(attrs['class'], 'form-control')
        self.assertEqual(attrs['accept'], 'image/*')


class UserProfileWorkflowIntegrationTests(UserProfileIntegrationTestCase):
    """Integration tests for complete userprofile workflows."""
    
    def test_complete_profile_creation_and_update_workflow(self):
        """Test complete workflow of profile creation and updates."""
        # Step 1: Create new user without profile
        new_user = User.objects.create_user(
            username='workflowuser',
            email='workflow@example.com',
            password='WorkflowPass123!',
            first_name='Workflow',
            last_name='User'
        )
        
        # Step 2: Login and access profile (should create profile)
        self.client.login(username='workflowuser', password='WorkflowPass123!')
        response = self.client.get(reverse('profile'))
        
        self.assertEqual(response.status_code, 200)
        
        # Verify profile was auto-created
        profile = Profile.objects.get(user=new_user)
        self.assertEqual(profile.profession, 'dentist')  # Default
        
        # Step 3: Update profile picture
        uploaded_file = create_test_image('workflow_pic.png')
        
        response = self.client.post(reverse('profile'), {'profile_pic': uploaded_file})
        
        self.assertEqual(response.status_code, 302)
        
        # Verify profile was updated
        profile.refresh_from_db()
        self.assertTrue(profile.profile_pic.name.startswith('profile/'))
    
    def test_ajax_professions_integration_workflow(self):
        """Test AJAX professions workflow for different health bodies."""
        # Test getting professions for different bodies
        bodies_to_test = ['HPCSA', 'SANC', 'UNKNOWN']
        
        for body in bodies_to_test:
            response = self.client.get(reverse('get_professions'), {'body': body})
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content.decode('utf-8'))
            
            if body in ['HPCSA', 'SANC']:
                self.assertGreater(len(data['professions']), 0)
            else:
                self.assertEqual(len(data['professions']), 0)
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_profile_picture_replacement_workflow(self):
        """Test workflow of replacing profile pictures."""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Step 1: Upload first picture
        uploaded_file1 = create_test_image('first_pic.png')
        
        response = self.client.post(reverse('profile'), {'profile_pic': uploaded_file1})
        self.assertEqual(response.status_code, 302)
        
        self.profile.refresh_from_db()
        first_pic_name = self.profile.profile_pic.name
        
        # Step 2: Upload second picture (should replace first)
        uploaded_file2 = create_test_image('second_pic.png')
        
        response = self.client.post(reverse('profile'), {'profile_pic': uploaded_file2})
        self.assertEqual(response.status_code, 302)
        
        self.profile.refresh_from_db()
        second_pic_name = self.profile.profile_pic.name
        
        # Verify picture was replaced
        self.assertNotEqual(first_pic_name, second_pic_name)
        self.assertTrue(self.profile.profile_pic.name.startswith('profile/'))
