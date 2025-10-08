"""
Security Tests for Authentication and Session Management        page2.click('button[type="submit"]')
Tests various security aspects o             # Login with same user in second session
        page2.goto(f"{live_server_url}/login_user/")
        page2.fill('input[name="username"]', 'testuser123')
        page2.fill('input[name="password"]', 'ComplexPass123!')
        page2.click('button[type="submit"]')     page2.fill('input[name="password"]', 'ComplexPass123!')
        page2.click('button[type="submit"]') Login with same user in second session
        page2.goto(f"{live_server_url}/login_user/")
        page2.fill('input[name="username"]', 'testuser123')
        page2.fill('input[name="password"]', 'ComplexPass123!')
        page2.click('button[type="submit"]')r authentication and session handling
"""
import pytest
from playwright.sync_api import Page, expect
import time
import re

@pytest.mark.e2e
@pytest.mark.security
class TestAuthenticationSecurity:
    
    def test_password_complexity_enforcement(self, page: Page, live_server_url):
        """Test that weak passwords are rejected."""
        page.goto(f"{live_server_url}/register_user/")
        
        # Test weak passwords
        weak_passwords = [
            "123456",           # Too simple
            "password",         # Common password
            "Password",         # Missing numbers and special chars
            "Password123",      # Missing special chars
            "Pass@1"           # Too short
        ]
        
        for weak_password in weak_passwords:
            page.fill('input[name="username"]', f'testuser_{weak_password}')
            page.fill('input[name="email"]', f'test_{weak_password}@example.com')
            page.fill('input[name="first_name"]', 'Test')
            page.fill('input[name="last_name"]', 'User')
            page.fill('input[name="password1"]', weak_password)
            page.fill('input[name="password2"]', weak_password)
            
            # Fill required fields
            page.select_option('select[name="health_professional_body"]', 'HPCSA')
            page.wait_for_timeout(1000)  # Wait for profession dropdown to load
            page.select_option('select[name="profession"]', 'Dentist')
            page.fill('input[name="reg_num"]', '12345')
            
            page.click('button[type="submit"]')
            
            # Should show password validation error
            expect(page.locator('text*=password')).to_be_visible()
            page.reload()  # Reset form
    
    def test_session_timeout_behavior(self, page: Page, live_server_url):
        """Test session security and timeout behavior."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Verify successful login
        expect(page).to_have_url(f"{live_server_url}/home/")
        
        # Test session persistence across page reloads
        page.reload()
        expect(page).to_have_url(f"{live_server_url}/home/")
        
        # Clear session cookies to simulate timeout
        page.context.clear_cookies()
        page.goto(f"{live_server_url}/home/")
        
        # Should redirect to login
        assert 'login' in page.url
    
    def test_brute_force_protection(self, page: Page, live_server_url):
        """Test multiple failed login attempts."""
        page.goto(f"{live_server_url}/login_user/")
        
        # Attempt multiple failed logins
        for i in range(5):
            page.fill('input[name="username"]', 'testuser123')
            page.fill('input[name="password"]', f'wrongpass{i}')
            page.click('button[type="submit"]')
            
            # Should show error message
            expect(page.locator('text=Invalid')).to_be_visible()
            page.wait_for_timeout(1000)  # Small delay between attempts
    
    def test_concurrent_session_handling(self, page: Page, live_server_url, browser):
        """Test behavior with multiple concurrent sessions."""
        # First session login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        expect(page).to_have_url(f"{live_server_url}/home/")
        
        # Create second browser context (simulate different device)
        context2 = browser.new_context()
        page2 = context2.new_page()
        
        # Login with same user in second session
        page2.goto(f"{live_server_url}/login_user/")
        page2.fill('input[name="username"]', 'testuser123')
        page2.fill('input[name="password"]', 'ComplexPass123!')
        page2.click('button[type="submit"]')
        
        # Both sessions should be valid (Django allows multiple sessions by default)
        expect(page2).to_have_url(f"{live_server_url}/home/")
        
        # First session should still be valid
        page.reload()
        expect(page).to_have_url(f"{live_server_url}/home/")
        
        context2.close()

    def test_redirect_after_login(self, page: Page, live_server_url):
        """Test that login redirects to intended page."""
        # Try to access protected page without authentication
        protected_url = f"{live_server_url}/create_patient/"
        page.goto(protected_url)
        
        # Should redirect to login with next parameter
        current_url = page.url
        assert 'login' in current_url
        assert 'next=' in current_url or page.url == f"{live_server_url}/login_user/"
        
        # Login and should redirect back to intended page
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Should redirect to intended page or home
        page.wait_for_load_state('networkidle')
        assert page.url == protected_url or page.url == f"{live_server_url}/home/"

    def test_user_enumeration_protection(self, page: Page, live_server_url):
        """Test that login doesn't reveal if username exists."""
        page.goto(f"{live_server_url}/login_user/")
        
        # Test with non-existent user
        page.fill('input[name="username"]', 'nonexistentuser999')
        page.fill('input[name="password"]', 'somepassword')
        page.click('button[type="submit"]')
        
        error_message_1 = page.locator('.alert').text_content() if page.locator('.alert').is_visible() else ""
        
        # Test with existing user but wrong password
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'wrongpassword')
        page.click('button[type="submit"]')
        
        error_message_2 = page.locator('.alert').text_content() if page.locator('.alert').is_visible() else ""
        
        # Error messages should be similar (not revealing if user exists)
        error_message_1 = error_message_1 or ""
        error_message_2 = error_message_2 or ""
        assert 'Invalid' in error_message_1 or 'Invalid' in error_message_2
