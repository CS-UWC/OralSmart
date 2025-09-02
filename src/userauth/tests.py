from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core import mail
from django.db import transaction
from unittest.mock import patch, Mock

from userprofile.models import Profile
from .forms import CustomUserCreationForm, CustomSetPasswordForm, CustomPasswordResetForm
from .tokens import account_activation_token
from .decorators import user_not_authenticated

User = get_user_model()


class UserAuthIntegrationTestCase(TestCase):
    """Base test case for userauth integration tests."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.test_user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'profession': 'dentist',
            'health_professional_body': 'HPCSA',
            'reg_num': 'TEST123456'
        }
        
        self.active_user = User.objects.create_user(
            username='activeuser',
            email='activeuser@example.com',
            password='ActivePass123!',
            first_name='Active',
            last_name='User',
            is_active=True
        )
        
        # Create corresponding profile
        Profile.objects.create(
            user=self.active_user,
            profession='dentist',
            health_professional_body='HPCSA',
            reg_num='ACTIVE123',
            email=self.active_user.email
        )


class LandingPageIntegrationTests(UserAuthIntegrationTestCase):
    """Integration tests for landing page functionality."""
    
    def test_landing_page_get_request(self):
        """Test GET request to landing page."""
        response = self.client.get(reverse('landing'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')
    
    def test_landing_page_redirects_authenticated_user(self):
        """Test that authenticated users are redirected from landing page."""
        self.client.login(username='activeuser', password='ActivePass123!')
        response = self.client.get(reverse('landing'))
        
        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
    
    def test_user_not_authenticated_decorator_functionality(self):
        """Test the user_not_authenticated decorator works correctly."""
        # Test with unauthenticated user - should allow access
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        
        # Test with authenticated user - should redirect
        self.client.login(username='activeuser', password='ActivePass123!')
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 302)


class LoginIntegrationTests(UserAuthIntegrationTestCase):
    """Integration tests for login functionality."""
    
    def test_login_view_get_request(self):
        """Test GET request to login view."""
        response = self.client.get(reverse('login'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')
        self.assertContains(response, 'Sign in to')
        self.assertContains(response, 'OralSmart')
    
    def test_successful_login(self):
        """Test successful login with valid credentials."""
        login_data = {
            'username': 'activeuser',
            'password': 'ActivePass123!'
        }
        
        response = self.client.post(reverse('login'), login_data)
        
        # Should redirect to home after successful login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Verify user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
        
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        
        response = self.client.post(reverse('login'), login_data)
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid username or password" in str(m) for m in messages))
    
    def test_login_with_next_parameter(self):
        """Test login redirect with next parameter."""
        login_data = {
            'username': 'activeuser',
            'password': 'ActivePass123!',
            'next': '/patient_list/'
        }
        
        response = self.client.post(reverse('login'), login_data)
        
        # Should redirect to next URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/patient_list/')
    
    def test_login_redirects_authenticated_user(self):
        """Test that authenticated users are redirected from login page."""
        self.client.login(username='activeuser', password='ActivePass123!')
        response = self.client.get(reverse('login'))
        
        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
    
    def test_login_inactive_user(self):
        """Test login with inactive user account."""
        # Create inactive user
        inactive_user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='InactivePass123!',
            is_active=False
        )
        
        login_data = {
            'username': 'inactiveuser',
            'password': 'InactivePass123!'
        }
        
        response = self.client.post(reverse('login'), login_data)
        
        # Should fail to login (Django's authenticate returns None for inactive users)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid username or password" in str(m) for m in messages))


class LogoutIntegrationTests(UserAuthIntegrationTestCase):
    """Integration tests for logout functionality."""
    
    def test_successful_logout(self):
        """Test successful logout."""
        # First login
        self.client.login(username='activeuser', password='ActivePass123!')
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Then logout
        response = self.client.post(reverse('logout'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Verify user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("successfully logged out" in str(m) for m in messages))
    
    def test_logout_requires_post(self):
        """Test that logout requires POST request."""
        self.client.login(username='activeuser', password='ActivePass123!')
        
        # Try GET request
        response = self.client.get(reverse('logout'))
        
        # Should redirect with unsuccessful message
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("unsuccessful" in str(m) for m in messages))
    
    def test_logout_requires_authentication(self):
        """Test that logout requires user to be logged in."""
        # Try to access logout without being logged in
        response = self.client.post(reverse('logout'))
        
        # Should redirect to login (due to @login_required decorator)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/login_user/'))


class RegistrationIntegrationTests(UserAuthIntegrationTestCase):
    """Integration tests for user registration functionality."""
    
    def test_registration_view_get_request(self):
        """Test GET request to registration view."""
        response = self.client.get(reverse('register_user'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/register_user.html')
        self.assertContains(response, 'Register to use')
        self.assertContains(response, 'OralSmart')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)
    
    @patch('userauth.views.activateEmail')
    def test_successful_registration(self, mock_activate_email):
        """Test successful user registration."""
        mock_activate_email.return_value = None  # Mock email sending
        
        response = self.client.post(reverse('register_user'), self.test_user_data)
        
        # Should redirect to login after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Verify user was created
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertFalse(user.is_active)  # Should be inactive pending email verification
        
        # Verify profile was created
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.profession, 'dentist')
        self.assertEqual(profile.health_professional_body, 'HPCSA')
        self.assertEqual(profile.reg_num, 'TEST123456')
        
        # Verify email activation was called
        mock_activate_email.assert_called_once()
    
    def test_registration_with_duplicate_username(self):
        """Test registration with duplicate username."""
        duplicate_data = self.test_user_data.copy()
        duplicate_data['username'] = 'activeuser'  # Already exists
        
        response = self.client.post(reverse('register_user'), duplicate_data)
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/register_user.html')
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("already exists" in str(m) for m in messages))
    
    def test_registration_with_duplicate_email(self):
        """Test registration with duplicate email."""
        duplicate_data = self.test_user_data.copy()
        duplicate_data['email'] = 'activeuser@example.com'  # Already exists
        
        response = self.client.post(reverse('register_user'), duplicate_data)
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("already exists" in str(m) for m in messages))
    
    def test_registration_with_mismatched_passwords(self):
        """Test registration with mismatched passwords."""
        invalid_data = self.test_user_data.copy()
        invalid_data['password2'] = 'different_password'
        
        response = self.client.post(reverse('register_user'), invalid_data)
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/register_user.html')
    
    def test_registration_with_missing_required_fields(self):
        """Test registration with missing required fields."""
        incomplete_data = {
            'username': 'newuser',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
            # Missing email, names, profile fields
        }
        
        response = self.client.post(reverse('register_user'), incomplete_data)
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/register_user.html')
    
    def test_registration_redirects_authenticated_user(self):
        """Test that authenticated users are redirected from registration page."""
        self.client.login(username='activeuser', password='ActivePass123!')
        response = self.client.get(reverse('register_user'))
        
        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
    
    @patch('userauth.views.activateEmail')
    def test_registration_transaction_rollback_on_profile_error(self, mock_activate_email):
        """Test that registration is rolled back if profile creation fails."""
        mock_activate_email.return_value = None
        
        # Mock Profile.objects.create to raise an exception
        with patch('userprofile.models.Profile.objects.create') as mock_profile_create:
            mock_profile_create.side_effect = Exception("Profile creation failed")
            
            response = self.client.post(reverse('register_user'), self.test_user_data)
            
            # Should stay on registration page
            self.assertEqual(response.status_code, 200)
            
            # User should not be created due to transaction rollback
            self.assertFalse(User.objects.filter(username='testuser').exists())
            
            # Check error message
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("error occurred during registration" in str(m) for m in messages))


class AccountActivationIntegrationTests(UserAuthIntegrationTestCase):
    """Integration tests for account activation functionality."""
    
    def setUp(self):
        super().setUp()
        # Create inactive user for activation testing
        self.inactive_user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='InactivePass123!',
            is_active=False
        )
    
    def test_successful_account_activation(self):
        """Test successful account activation."""
        # Generate activation token and uid
        token = account_activation_token.make_token(self.inactive_user)
        uid = urlsafe_base64_encode(force_bytes(self.inactive_user.pk))
        
        response = self.client.get(reverse('activate', kwargs={'uidb64': uid, 'token': token}))
        
        # Should redirect to create_patient after activation
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('create_patient'))
        
        # Verify user is now active
        self.inactive_user.refresh_from_db()
        self.assertTrue(self.inactive_user.is_active)
        
        # Verify user is logged in after activation
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("successfully been activated" in str(m) for m in messages))
    
    def test_activation_with_invalid_token(self):
        """Test activation with invalid token."""
        uid = urlsafe_base64_encode(force_bytes(self.inactive_user.pk))
        invalid_token = 'invalid-token'
        
        response = self.client.get(reverse('activate', kwargs={'uidb64': uid, 'token': invalid_token}))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Verify user is still inactive
        self.inactive_user.refresh_from_db()
        self.assertFalse(self.inactive_user.is_active)
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("invalid" in str(m) for m in messages))
    
    def test_activation_with_invalid_uid(self):
        """Test activation with invalid uid."""
        token = account_activation_token.make_token(self.inactive_user)
        invalid_uid = 'invalid-uid'
        
        response = self.client.get(reverse('activate', kwargs={'uidb64': invalid_uid, 'token': token}))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("invalid" in str(m) for m in messages))
    
    def test_activation_with_nonexistent_user(self):
        """Test activation with non-existent user ID."""
        # Generate uid for non-existent user
        fake_uid = urlsafe_base64_encode(force_bytes(99999))
        token = 'any-token'
        
        response = self.client.get(reverse('activate', kwargs={'uidb64': fake_uid, 'token': token}))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
    
    def test_activation_redirects_authenticated_user(self):
        """Test that authenticated users are redirected from activation page."""
        self.client.login(username='activeuser', password='ActivePass123!')
        
        token = account_activation_token.make_token(self.inactive_user)
        uid = urlsafe_base64_encode(force_bytes(self.inactive_user.pk))
        
        response = self.client.get(reverse('activate', kwargs={'uidb64': uid, 'token': token}))
        
        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailActivationIntegrationTests(UserAuthIntegrationTestCase):
    """Integration tests for email activation functionality."""
    
    def test_activation_email_sent(self):
        """Test that activation email is sent during registration."""
        response = self.client.post(reverse('register_user'), self.test_user_data)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        # Verify email content
        self.assertEqual(email.subject, 'Activate Your OralSmart Account')
        self.assertIn('testuser@example.com', email.to)
        self.assertIn('activate', email.body)
        
        # Check success message about email
        messages = list(get_messages(response.wsgi_request))
        email_message_found = any("please go to your email" in str(m) for m in messages)
        self.assertTrue(email_message_found)
    
    @patch('userauth.views.EmailMessage.send')
    def test_activation_email_send_failure(self, mock_email_send):
        """Test handling of email send failure."""
        mock_email_send.return_value = False  # Simulate email send failure
        
        response = self.client.post(reverse('register_user'), self.test_user_data)
        
        # Should still redirect to login
        self.assertEqual(response.status_code, 302)
        
        # Check error message about email failure
        messages = list(get_messages(response.wsgi_request))
        email_error_found = any("problem sending the email" in str(m) for m in messages)
        self.assertTrue(email_error_found)


class PasswordResetIntegrationTests(UserAuthIntegrationTestCase):
    """Integration tests for password reset functionality."""
    
    def test_password_reset_request_get(self):
        """Test GET request to password reset request page."""
        response = self.client.get(reverse('reset_password'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/reset_password.html')
        self.assertIsInstance(response.context['form'], CustomPasswordResetForm)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_request_post_valid_email(self):
        """Test password reset request with valid email."""
        reset_data = {'email': 'activeuser@example.com'}
        
        response = self.client.post(reverse('reset_password'), reset_data)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Password reset email sent" in str(m) for m in messages))
    
    def test_password_reset_request_post_invalid_email(self):
        """Test password reset request with invalid email."""
        reset_data = {'email': 'nonexistent@example.com'}
        
        response = self.client.post(reverse('reset_password'), reset_data)
        
        # Should stay on reset password page with form errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/reset_password.html')
    
    def test_password_reset_request_redirects_authenticated_user(self):
        """Test that authenticated users are redirected from password reset page."""
        self.client.login(username='activeuser', password='ActivePass123!')
        response = self.client.get(reverse('reset_password'))
        
        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
    
    def test_password_reset_confirm_get_valid_token(self):
        """Test password reset confirmation with valid token."""
        # Generate reset token
        token = default_token_generator.make_token(self.active_user)
        uid = urlsafe_base64_encode(force_bytes(self.active_user.pk))
        
        response = self.client.get(reverse('confirm_password_reset', kwargs={'uidb64': uid, 'token': token}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/reset_password_confirm.html')
        self.assertIsInstance(response.context['form'], CustomSetPasswordForm)
    
    def test_password_reset_confirm_post_valid_data(self):
        """Test password reset confirmation with valid new password."""
        # Generate reset token
        token = default_token_generator.make_token(self.active_user)
        uid = urlsafe_base64_encode(force_bytes(self.active_user.pk))
        
        new_password_data = {
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        
        response = self.client.post(
            reverse('confirm_password_reset', kwargs={'uidb64': uid, 'token': token}),
            new_password_data
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Verify password was changed
        self.active_user.refresh_from_db()
        self.assertTrue(self.active_user.check_password('NewPassword123!'))
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("password has been set" in str(m) for m in messages))
    
    def test_password_reset_confirm_invalid_token(self):
        """Test password reset confirmation with invalid token."""
        uid = urlsafe_base64_encode(force_bytes(self.active_user.pk))
        invalid_token = 'invalid-token'
        
        response = self.client.get(reverse('confirm_password_reset', kwargs={'uidb64': uid, 'token': invalid_token}))
        
        # Should redirect to password reset request page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reset_password'))
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("invalid" in str(m) for m in messages))


class ChangePasswordIntegrationTests(UserAuthIntegrationTestCase):
    """Integration tests for change password functionality."""
    
    def test_change_password_get_requires_authentication(self):
        """Test that change password requires authentication."""
        response = self.client.get(reverse('change_password'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/login_user/'))
    
    def test_change_password_get_authenticated_user(self):
        """Test GET request to change password for authenticated user."""
        self.client.login(username='activeuser', password='ActivePass123!')
        
        response = self.client.get(reverse('change_password'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/reset_password_confirm.html')
        self.assertIsInstance(response.context['form'], CustomSetPasswordForm)
        self.assertTrue(response.context['show_navbar'])
    
    def test_change_password_post_valid_data(self):
        """Test changing password with valid data."""
        self.client.login(username='activeuser', password='ActivePass123!')
        
        new_password_data = {
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        
        response = self.client.post(reverse('change_password'), new_password_data)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Verify password was changed
        self.active_user.refresh_from_db()
        self.assertTrue(self.active_user.check_password('NewPassword123!'))
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("successfully updated" in str(m) for m in messages))
    
    def test_change_password_post_invalid_data(self):
        """Test changing password with invalid data."""
        self.client.login(username='activeuser', password='ActivePass123!')
        
        invalid_password_data = {
            'new_password1': 'newpass',  # Too short
            'new_password2': 'different'  # Doesn't match
        }
        
        response = self.client.post(reverse('change_password'), invalid_password_data)
        
        # Should stay on change password page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/reset_password_confirm.html')
        
        # Check error messages
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)  # Should have validation error messages


class HomePageIntegrationTests(UserAuthIntegrationTestCase):
    """Integration tests for home page functionality."""
    
    def test_home_page_requires_authentication(self):
        """Test that home page requires authentication."""
        response = self.client.get(reverse('home'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/login_user/'))
    
    def test_home_page_authenticated_user(self):
        """Test home page access for authenticated user."""
        self.client.login(username='activeuser', password='ActivePass123!')
        
        response = self.client.get(reverse('home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')


class UserAuthFormIntegrationTests(UserAuthIntegrationTestCase):
    """Integration tests for userauth forms."""
    
    def test_custom_user_creation_form_validation(self):
        """Test CustomUserCreationForm validation."""
        # Test valid form
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Test form save
        user = form.save(commit=False)
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertFalse(user.is_active)  # Should be inactive by default
    
    def test_custom_user_creation_form_duplicate_validation(self):
        """Test CustomUserCreationForm duplicate validation."""
        form_data = {
            'username': 'activeuser',  # Already exists
            'email': 'activeuser@example.com',  # Already exists
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('already exists', str(form.errors['username']))
        self.assertIn('already exists', str(form.errors['email']))
    
    def test_custom_password_reset_form_validation(self):
        """Test CustomPasswordResetForm validation."""
        # Test with valid active user email
        form = CustomPasswordResetForm(data={'email': 'activeuser@example.com'})
        self.assertTrue(form.is_valid())
        
        # Test with non-existent email
        form = CustomPasswordResetForm(data={'email': 'nonexistent@example.com'})
        self.assertFalse(form.is_valid())
        self.assertIn('No User is associated', str(form.errors['email']))
    
    def test_custom_set_password_form_functionality(self):
        """Test CustomSetPasswordForm functionality."""
        form_data = {
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        
        form = CustomSetPasswordForm(user=self.active_user, data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")


class UserAuthWorkflowIntegrationTests(UserAuthIntegrationTestCase):
    """Integration tests for complete userauth workflows."""
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_complete_registration_to_activation_workflow(self):
        """Test complete workflow from registration to activation."""
        # Step 1: Register new user
        response = self.client.post(reverse('register_user'), self.test_user_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify user created but inactive
        user = User.objects.get(username='testuser')
        self.assertFalse(user.is_active)
        
        # Verify email sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Step 2: Extract activation link from email
        email_body = mail.outbox[0].body
        # Parse activation URL from email
        import re
        activation_match = re.search(r'/activate/([^/]+)/([^/]+)/', email_body)
        self.assertIsNotNone(activation_match, "Activation URL not found in email")
        
        if activation_match:
            uid, token = activation_match.groups()
        else:
            self.fail("Could not extract activation parameters from email")
        
        # Step 3: Activate account
        response = self.client.get(reverse('activate', kwargs={'uidb64': uid, 'token': token}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('create_patient'))
        
        # Verify user is now active and logged in
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue('_auth_user_id' in self.client.session)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_complete_password_reset_workflow(self):
        """Test complete password reset workflow."""
        # Step 1: Request password reset
        response = self.client.post(reverse('reset_password'), {'email': 'activeuser@example.com'})
        self.assertEqual(response.status_code, 302)
        
        # Verify email sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Step 2: Extract reset link from email
        email_body = mail.outbox[0].body
        import re
        reset_match = re.search(r'/reset/([^/]+)/([^/]+)/', email_body)
        self.assertIsNotNone(reset_match, "Reset URL not found in email")
        
        if reset_match:
            uid, token = reset_match.groups()
        else:
            self.fail("Could not extract reset parameters from email")
        
        # Step 3: Access reset confirmation page
        response = self.client.get(reverse('confirm_password_reset', kwargs={'uidb64': uid, 'token': token}))
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Set new password
        new_password_data = {
            'new_password1': 'BrandNewPass123!',
            'new_password2': 'BrandNewPass123!'
        }
        
        response = self.client.post(
            reverse('confirm_password_reset', kwargs={'uidb64': uid, 'token': token}),
            new_password_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Step 5: Login with new password
        login_response = self.client.post(reverse('login'), {
            'username': 'activeuser',
            'password': 'BrandNewPass123!'
        })
        self.assertEqual(login_response.status_code, 302)
        self.assertRedirects(login_response, reverse('home'))
    
    def test_login_to_logout_workflow(self):
        """Test complete login to logout workflow."""
        # Step 1: Login
        login_response = self.client.post(reverse('login'), {
            'username': 'activeuser',
            'password': 'ActivePass123!'
        })
        self.assertEqual(login_response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Step 2: Access authenticated page
        home_response = self.client.get(reverse('home'))
        self.assertEqual(home_response.status_code, 200)
        
        # Step 3: Change password
        change_password_response = self.client.post(reverse('change_password'), {
            'new_password1': 'ChangedPass123!',
            'new_password2': 'ChangedPass123!'
        })
        self.assertEqual(change_password_response.status_code, 302)
        
        # Step 4: Login with new password
        new_login_response = self.client.post(reverse('login'), {
            'username': 'activeuser',
            'password': 'ChangedPass123!'
        })
        self.assertEqual(new_login_response.status_code, 302)
        
        # Step 5: Logout
        logout_response = self.client.post(reverse('logout'))
        self.assertEqual(logout_response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)
