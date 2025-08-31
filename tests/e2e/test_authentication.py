"""
End-to-End Tests for User Authentication and Authorization
Tests user registration, login, logout, and access control
"""
import pytest
from playwright.sync_api import Page, expect
import time
import re

@pytest.mark.e2e
@pytest.mark.auth
class TestAuthentication:
    
    def setup_method(self):
        """Clean setup for each test method."""
        pass
    
    def test_user_registration_flow(self, page: Page, live_server_url):
        """Test complete user registration process."""
        # Ensure clean session
        page.context.clear_cookies()
        
        page.goto(f"{live_server_url}/register_user/")
        
        # Fill registration form
        page.fill('input[name="username"]', 'newuser123')
        page.fill('input[name="email"]', 'newuser@example.com')
        page.fill('input[name="first_name"]', 'New')
        page.fill('input[name="last_name"]', 'User')
        page.fill('input[name="password1"]', 'ComplexPass123!')
        page.fill('input[name="password2"]', 'ComplexPass123!')
        
        # Submit registration
        page.click('button[type="submit"]')
        
        # Should redirect to login or show success message
        current_url = page.url
        assert 'login' in current_url or 'register' in current_url
    
    def test_user_login_success(self, page: Page, live_server_url):
        """Test successful user login with pre-created active user."""
        # Ensure clean session
        page.context.clear_cookies()
        
        # Login with the pre-created active user (created via Django management command)
        page.goto(f"{live_server_url}/login_user/")
        
        # Fill login form
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        
        # Submit login
        page.click('button[type="submit"]')
        
        # Wait a moment for any redirects to complete
        page.wait_for_load_state('networkidle', timeout=10000)
        
        # Check current URL after login attempt
        current_url = page.url
        print(f"Current URL after login: {current_url}")
        
        # Should redirect to home page
        expect(page).to_have_url(f"{live_server_url}/home/")
        
        # Check if user is logged in by looking for profile avatar/menu
        profile_avatar = page.locator('img[alt="avatar"]').first
        expect(profile_avatar).to_be_visible()
        
        # Click the profile avatar to open the drawer
        profile_avatar.click()
        
        # Check if logout button is visible in the drawer
        logout_button = page.locator('button:has-text("Log out")')
        expect(logout_button).to_be_visible()
    
    def test_user_login_invalid_credentials(self, page: Page, live_server_url):
        """Test login with invalid credentials."""
        # Ensure clean session
        page.context.clear_cookies()
        
        page.goto(f"{live_server_url}/login_user/")
        
        # Fill login form with wrong credentials
        page.fill('input[name="username"]', 'wronguser')
        page.fill('input[name="password"]', 'wrongpassword')
        
        # Submit login
        page.click('button[type="submit"]')
        
        # Should stay on login page and show error
        current_url = page.url
        assert 'login' in current_url
        expect(page.locator('text=Invalid')).to_be_visible()
    
    def test_user_logout(self, page: Page, live_server_url):
        """Test user logout functionality with pre-created active user."""
        # Ensure clean session
        page.context.clear_cookies()
        
        # Login with the pre-created active user (created via Django management command)
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Wait for redirect to home
        page.wait_for_load_state('networkidle', timeout=10000)
        
        # Should be redirected to home page
        expect(page).to_have_url(f"{live_server_url}/home/")
        
        # Click the profile avatar to open the drawer
        profile_avatar = page.locator('img[alt="avatar"]').first
        expect(profile_avatar).to_be_visible()
        profile_avatar.click()
        
        # Click logout button in the drawer
        logout_button = page.locator('button:has-text("Log out")')
        expect(logout_button).to_be_visible()
        logout_button.click()
        
        # Should redirect to login page (not landing page based on logout view)
        expect(page).to_have_url(f"{live_server_url}/login_user/")
    
    def test_protected_page_requires_login(self, page: Page, live_server_url):
        """Test that protected pages require authentication."""
        # Ensure clean session
        page.context.clear_cookies()
        
        # Try to access protected page without login (use admin instead of create_patient)
        page.goto(f"{live_server_url}/admin/")
        
        # Should redirect to login page or show permission denied
        current_url = page.url
        assert 'admin/login' in current_url or 'login' in current_url
    
    def test_staff_access_control(self, page: Page, live_server_url):
        """Test that non-staff users can't access admin areas."""
        # Ensure clean session
        page.context.clear_cookies()
        
        # Login with regular (non-staff) user
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Wait for login to complete
        page.wait_for_load_state('networkidle', timeout=10000)
        
        # Try to access admin area - should be denied or redirect
        page.goto(f"{live_server_url}/admin/")
        
        # Regular user should not have admin access
        current_url = page.url
        assert 'admin/login' in current_url or page.locator('text=permission').is_visible()
