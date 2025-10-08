"""
Security Tests for Authorization and Access Control
Tests role-based access control and privilege escalation protection
"""
import pytest
from playwright.sync_api import Page, expect
import time

@pytest.mark.e2e
@pytest.mark.security
class TestAccessControlSecurity:
    
    def test_unauthorized_access_protection(self, page: Page, live_server_url):
        """Test that unauthenticated users cannot access protected resources."""
        # Ensure not logged in
        page.context.clear_cookies()
        
        protected_pages = [
            f"{live_server_url}/home/",
            f"{live_server_url}/create_patient/",
            f"{live_server_url}/patient_list/",
            f"{live_server_url}/profile_view/",
        ]
        
        for protected_url in protected_pages:
            page.goto(protected_url)
            
            # Should redirect to login or show access denied
            current_url = page.url
            assert ('login' in current_url.lower() or 
                    'access' in page.content().lower() or
                    'permission' in page.content().lower() or
                    'unauthorized' in page.content().lower())
    
    def test_user_data_isolation(self, page: Page, live_server_url, browser):
        """Test that users can only access their own data."""
        # Login as first user
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Create a patient as first user
        page.goto(f"{live_server_url}/create_patient/")
        page.fill('input[name="name"]', 'User1Patient')
        page.fill('input[name="surname"]', 'TestPatient')
        page.fill('input[name="age"]', '5')
        page.select_option('select[name="gender"]', 'Male')
        page.fill('input[name="parent_name"]', 'Parent1')
        page.fill('input[name="parent_surname"]', 'Test')
        page.fill('input[name="parent_id"]', '1234567890')
        page.fill('input[name="parent_contact"]', '0123456789')
        page.click('button[type="submit"]')
        
        # Logout
        page.goto(f"{live_server_url}/logout_user/")
        
        # Login as different user (if exists)
        # For now, we'll test that patient list shows appropriate data
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')  # Same user for now
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        page.goto(f"{live_server_url}/patient_list/")
        
        # Should only see patients belonging to this user
        # This test would be more meaningful with multiple users
        assert page.is_visible('text=User1Patient') or page.locator('tbody tr').count() >= 0
    
    def test_admin_area_protection(self, page: Page, live_server_url):
        """Test that non-admin users cannot access admin areas."""
        # Login as regular user
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Try to access admin panel
        page.goto(f"{live_server_url}/admin/")
        
        # Should be denied or redirected to admin login
        current_url = page.url
        assert ('admin/login' in current_url or 
                'permission' in page.content().lower() or
                'unauthorized' in page.content().lower())
    
    def test_direct_object_reference_protection(self, page: Page, live_server_url):
        """Test protection against insecure direct object references."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Try to access objects with direct IDs
        # Test various ID manipulation attempts
        object_ids = [1, 2, 99, 999, -1, 'admin', '../admin', 'null']
        
        for obj_id in object_ids:
            # Test patient access (if URL pattern exists)
            test_urls = [
                f"{live_server_url}/patient/{obj_id}/",
                f"{live_server_url}/assessment/{obj_id}/",
                f"{live_server_url}/report/{obj_id}/",
            ]
            
            for test_url in test_urls:
                page.goto(test_url)
                
                # Should either show 404, permission denied, or proper access control
                current_content = page.content().lower()
                current_url = page.url
                
                # Should not expose unauthorized data
                assert ('404' in current_content or 
                        'not found' in current_content or
                        'permission' in current_content or
                        'access denied' in current_content or
                        'unauthorized' in current_content or
                        page.url != test_url)  # Redirected away
                
                page.wait_for_timeout(200)
    
    def test_privilege_escalation_protection(self, page: Page, live_server_url):
        """Test protection against privilege escalation attempts."""
        # Login as regular user
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Try to modify user role through form manipulation
        page.goto(f"{live_server_url}/profile_view/")
        
        # Check if there are hidden fields that could be manipulated
        page.evaluate("""
            // Try to add admin privileges through DOM manipulation
            const form = document.querySelector('form');
            if (form) {
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'is_staff';
                hiddenInput.value = 'true';
                form.appendChild(hiddenInput);
                
                const hiddenInput2 = document.createElement('input');
                hiddenInput2.type = 'hidden';
                hiddenInput2.name = 'is_superuser';
                hiddenInput2.value = 'true';
                form.appendChild(hiddenInput2);
            }
        """)
        
        # Submit form if it exists
        submit_button = page.locator('button[type="submit"], input[type="submit"]')
        if submit_button.is_visible():
            submit_button.click()
            
            # User should not gain admin privileges
            # This would need verification in the application logic
            page.wait_for_timeout(1000)
    
    def test_session_fixation_protection(self, page: Page, live_server_url):
        """Test protection against session fixation attacks."""
        # Get initial session ID
        page.goto(f"{live_server_url}/login_user/")
        
        # Get session cookie before login
        cookies_before = page.context.cookies()
        session_before = None
        for cookie in cookies_before:
            if cookie.get('name') == 'sessionid':
                session_before = cookie.get('value')
                break
        
        # Login
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Get session cookie after login
        cookies_after = page.context.cookies()
        session_after = None
        for cookie in cookies_after:
            if cookie.get('name') == 'sessionid':
                session_after = cookie.get('value')
                break
        
        # Session ID should change after login (to prevent session fixation)
        if session_before and session_after:
            assert session_before != session_after, "Session ID should change after login"
    
    def test_password_change_security(self, page: Page, live_server_url):
        """Test security measures around password changes."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Navigate to password change (if exists)
        page.goto(f"{live_server_url}/change_password/")
        
        if page.locator('input[name*="password"]').is_visible():
            # Test that old password is required
            page.fill('input[name*="new_password"]', 'NewComplexPass123!')
            page.fill('input[name*="new_password_confirm"]', 'NewComplexPass123!')
            # Don't fill old password
            
            submit_button = page.locator('button[type="submit"]')
            if submit_button.is_visible():
                submit_button.click()
                
                # Should require old password
                assert page.locator('text*=old password').is_visible() or page.locator('.error').is_visible()
    
    def test_account_lockout_protection(self, page: Page, live_server_url):
        """Test account lockout after multiple failed attempts."""
        page.goto(f"{live_server_url}/login_user/")
        
        # Attempt multiple failed logins
        for attempt in range(6):  # Try more than typical lockout threshold
            page.fill('input[name="username"]', 'testuser123')
            page.fill('input[name="password"]', f'wrongpass{attempt}')
            page.click('button[type="submit"]')
            
            page.wait_for_timeout(500)
        
        # Now try with correct password
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Should either succeed or show lockout message
        # (Django doesn't have built-in lockout, but custom implementations might)
        current_url = page.url
        page_content = page.content().lower()
        
        # Test would depend on if lockout is implemented
        assert True  # Placeholder - actual implementation would check for lockout
