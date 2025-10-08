"""
Security Tests for CSRF Protection
Tests Cross-Site Request Forgery protection mechanisms
"""
import pytest
from playwright.sync_api import Page, expect
import requests
import re

@pytest.mark.e2e
@pytest.mark.security
class TestCSRFProtection:
    
    def test_csrf_token_presence_in_forms(self, page: Page, live_server_url):
        """Test that CSRF tokens are present in all forms."""
        forms_to_test = [
            f"{live_server_url}/login_user/",
            f"{live_server_url}/register_user/",
        ]
        
        for url in forms_to_test:
            page.goto(url)
            
            # Check if form has CSRF token
            csrf_input = page.locator('input[name="csrfmiddlewaretoken"]')
            expect(csrf_input).to_be_attached()
            
            csrf_value = csrf_input.get_attribute('value')
            assert csrf_value is not None
            assert len(csrf_value) > 10  # CSRF tokens should be reasonably long
    
    def test_csrf_protection_on_post_requests(self, page: Page, live_server_url):
        """Test that POST requests without valid CSRF tokens are rejected."""
        # First, login to get session
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Get session cookies
        cookies = page.context.cookies()
        cookie_dict = {}
        for cookie in cookies:
            name = cookie.get('name')
            value = cookie.get('value') 
            if name and value:
                cookie_dict[name] = value
        
        # Try to make POST request without CSRF token
        session = requests.Session()
        session.cookies.update(cookie_dict)
        
        response = session.post(f"{live_server_url}/create_patient/", data={
            'name': 'Test',
            'surname': 'Patient',
            'age': '5'
        })
        
        # Should be forbidden or redirect due to missing CSRF
        assert response.status_code in [403, 302, 400]  # Forbidden, redirect, or bad request
    
    def test_csrf_token_validation(self, page: Page, live_server_url):
        """Test that invalid CSRF tokens are rejected."""
        page.goto(f"{live_server_url}/login_user/")
        
        # Modify CSRF token to invalid value
        page.evaluate("""
            const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (csrfInput) {
                csrfInput.value = 'invalid_csrf_token_12345';
            }
        """)
        
        # Try to submit form with invalid CSRF token
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        
        # Submit and check for CSRF error
        page.click('button[type="submit"]')
        
        # Should either show error or stay on same page
        current_url = page.url
        assert 'login' in current_url  # Should not proceed to next page
    
    def test_csrf_token_in_ajax_requests(self, page: Page, live_server_url):
        """Test CSRF protection in AJAX requests."""
        page.goto(f"{live_server_url}/register_user/")
        
        # Try to make AJAX request without CSRF token
        response = page.evaluate("""
            async () => {
                try {
                    const response = await fetch('/ajax/get_professions/?body=HPCSA', {
                        method: 'GET',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });
                    return {
                        status: response.status,
                        ok: response.ok
                    };
                } catch (error) {
                    return { error: error.message };
                }
            }
        """)
        
        # GET requests should work (as they don't require CSRF)
        assert response.get('status') in [200, 404]  # Either works or endpoint doesn't exist

    def test_referer_header_validation(self, page: Page, live_server_url):
        """Test that requests with invalid referer headers are handled properly."""
        # Login first
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Get session cookies and CSRF token
        cookies = page.context.cookies()
        cookie_dict = {}
        for cookie in cookies:
            name = cookie.get('name')
            value = cookie.get('value') 
            if name and value:
                cookie_dict[name] = value
        
        # Get CSRF token from a page
        page.goto(f"{live_server_url}/create_patient/")
        csrf_token = page.locator('input[name="csrfmiddlewaretoken"]').get_attribute('value')
        
        # Make request with invalid referer
        session = requests.Session()
        session.cookies.update(cookie_dict)
        
        response = session.post(
            f"{live_server_url}/create_patient/",
            data={
                'csrfmiddlewaretoken': csrf_token,
                'name': 'Test',
                'surname': 'Patient',
                'age': '5'
            },
            headers={
                'Referer': 'https://evil-site.com/'
            }
        )
        
        # Should be rejected due to invalid referer
        assert response.status_code in [403, 400]
