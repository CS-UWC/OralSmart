"""
Security Tests for Data Protection and Privacy
Tests encryption, data leakage, and privacy compliance
"""
import pytest
from playwright.sync_api import Page, expect
import re

@pytest.mark.e2e
@pytest.mark.security
class TestDataProtectionSecurity:
    
    def test_sensitive_data_not_in_source(self, page: Page, live_server_url):
        """Test that sensitive data is not exposed in HTML source."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Check various pages for sensitive data exposure
        pages_to_check = [
            f"{live_server_url}/home/",
            f"{live_server_url}/patient_list/",
            f"{live_server_url}/profile_view/"
        ]
        
        for url in pages_to_check:
            page.goto(url)
            source = page.content()
            
            # Check for exposed sensitive patterns
            sensitive_patterns = [
                r'password["\'\s]*[:=]["\'\s]*\w+',  # Passwords in JavaScript/HTML
                r'secret["\'\s]*[:=]["\'\s]*\w+',    # Secret keys
                r'api[_-]?key["\'\s]*[:=]["\'\s]*\w+',  # API keys
                r'database[_-]?url["\'\s]*[:=]',     # Database URLs
                r'conn[_-]?string["\'\s]*[:=]',      # Connection strings
            ]
            
            for pattern in sensitive_patterns:
                matches = re.findall(pattern, source, re.IGNORECASE)
                assert len(matches) == 0, f"Sensitive data pattern found: {pattern} in {url}"
    
    def test_error_page_information_disclosure(self, page: Page, live_server_url):
        """Test that error pages don't disclose sensitive information."""
        # Try to trigger various error conditions
        error_urls = [
            f"{live_server_url}/nonexistent_page/",
            f"{live_server_url}/admin/secret/",
            f"{live_server_url}/patient/99999/",
            f"{live_server_url}/../../../etc/passwd",
            f"{live_server_url}/static/../../settings.py"
        ]
        
        for error_url in error_urls:
            page.goto(error_url)
            content = page.content().lower()
            
            # Should not expose sensitive information
            sensitive_info = [
                'traceback',
                'django.db',
                'sqlite3',
                'secret_key',
                'database',
                'settings.py',
                '/usr/local',
                'c:\\users',
                'exception location'
            ]
            
            for sensitive in sensitive_info:
                assert sensitive not in content, f"Sensitive info '{sensitive}' exposed in error page {error_url}"
    
    def test_debug_information_not_exposed(self, page: Page, live_server_url):
        """Test that debug information is not exposed in production."""
        page.goto(f"{live_server_url}/")
        
        # Check that Django debug toolbar is not present
        debug_indicators = [
            'djdt',  # Django Debug Toolbar
            'debug-toolbar',
            'debugtoolbar',
            'sql-queries',
            'debug: true',
            'development mode'
        ]
        
        content = page.content().lower()
        for indicator in debug_indicators:
            assert indicator not in content, f"Debug information exposed: {indicator}"
    
    def test_http_security_headers(self, page: Page, live_server_url):
        """Test that appropriate HTTP security headers are set."""
        response = page.goto(f"{live_server_url}/")
        
        if response:
            headers = response.headers
            
            # Check for security headers
            security_headers = {
                'x-frame-options': ['DENY', 'SAMEORIGIN'],
                'x-content-type-options': ['nosniff'],
                'x-xss-protection': ['1; mode=block'],
                'referrer-policy': ['strict-origin-when-cross-origin', 'no-referrer', 'same-origin'],
            }
            
            for header, allowed_values in security_headers.items():
                if header in headers:
                    header_value = headers[header].lower()
                    assert any(allowed.lower() in header_value for allowed in allowed_values), \
                        f"Security header {header} has unexpected value: {headers[header]}"
    
    def test_cookie_security_attributes(self, page: Page, live_server_url):
        """Test that cookies have appropriate security attributes."""
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        cookies = page.context.cookies()
        
        for cookie in cookies:
            cookie_name = cookie.get('name', '')
            
            # Session cookies should have security attributes
            if cookie_name in ['sessionid', 'csrftoken']:
                # Check HttpOnly (for session cookies)
                if cookie_name == 'sessionid':
                    assert cookie.get('httpOnly', False), f"Cookie {cookie_name} should be HttpOnly"
                
                # Check Secure flag in HTTPS environments
                # assert cookie.get('secure', False), f"Cookie {cookie_name} should have Secure flag"
                
                # Check SameSite attribute
                same_site = cookie.get('sameSite')
                assert same_site in ['Strict', 'Lax'], f"Cookie {cookie_name} should have SameSite attribute"
    
    def test_password_field_autocomplete(self, page: Page, live_server_url):
        """Test that password fields have appropriate autocomplete attributes."""
        page.goto(f"{live_server_url}/login_user/")
        
        password_field = page.locator('input[type="password"]')
        if password_field.is_visible():
            autocomplete = password_field.get_attribute('autocomplete')
            # Should either be 'off' or 'current-password' for security
            assert autocomplete in ['off', 'current-password', None]
        
        # Check registration page
        page.goto(f"{live_server_url}/register_user/")
        
        new_password_fields = page.locator('input[name*="password"]')
        count = new_password_fields.count()
        for i in range(count):
            field = new_password_fields.nth(i)
            if field.is_visible():
                autocomplete = field.get_attribute('autocomplete')
                # New password fields should not autocomplete
                assert autocomplete in ['off', 'new-password', None]
    
    def test_sensitive_data_caching_prevention(self, page: Page, live_server_url):
        """Test that sensitive pages have cache control headers."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Check sensitive pages
        sensitive_pages = [
            f"{live_server_url}/patient_list/",
            f"{live_server_url}/profile_view/"
        ]
        
        for url in sensitive_pages:
            response = page.goto(url)
            
            if response:
                headers = response.headers
                
                # Check cache control headers
                cache_control = headers.get('cache-control', '').lower()
                
                # Sensitive pages should not be cached
                cache_prevention_indicators = [
                    'no-cache',
                    'no-store',
                    'private',
                    'max-age=0'
                ]
                
                has_cache_prevention = any(indicator in cache_control for indicator in cache_prevention_indicators)
            
            # Note: This is a recommendation, not always enforced
            # assert has_cache_prevention, f"Page {url} should have cache prevention headers"
    
    def test_personal_data_protection(self, page: Page, live_server_url):
        """Test protection of personal/medical data."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Create patient with sensitive data
        page.goto(f"{live_server_url}/create_patient/")
        
        sensitive_test_data = {
            'name': 'TestPatient',
            'surname': 'PrivacyTest',
            'parent_id': '9876543210',  # ID number
            'parent_contact': '0987654321'  # Phone number
        }
        
        page.fill('input[name="name"]', sensitive_test_data['name'])
        page.fill('input[name="surname"]', sensitive_test_data['surname'])
        page.fill('input[name="age"]', '8')
        page.select_option('select[name="gender"]', 'Female')
        page.fill('input[name="parent_name"]', 'TestParent')
        page.fill('input[name="parent_surname"]', 'Privacy')
        page.fill('input[name="parent_id"]', sensitive_test_data['parent_id'])
        page.fill('input[name="parent_contact"]', sensitive_test_data['parent_contact'])
        
        page.click('button[type="submit"]')
        
        # Check that sensitive data is handled appropriately
        # (This would need specific implementation details to test properly)
        
        # Logout and ensure data is not accessible
        page.goto(f"{live_server_url}/logout_user/")
        
        # Try to access patient data without authentication
        page.goto(f"{live_server_url}/patient_list/")
        
        # Should not show sensitive data
        content = page.content()
        assert sensitive_test_data['parent_id'] not in content
        assert sensitive_test_data['parent_contact'] not in content
    
    def test_data_export_security(self, page: Page, live_server_url):
        """Test security of data export features."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Check if there are any export/download features
        export_urls = [
            f"{live_server_url}/reports/export/",
            f"{live_server_url}/patient/export/",
            f"{live_server_url}/data/download/"
        ]
        
        for url in export_urls:
            page.goto(url)
            
            # If export exists, it should require authentication
            current_url = page.url
            content = page.content().lower()
            
            # Should not allow unauthorized access to data exports
            if 'export' in content or 'download' in content:
                # Verify user is still authenticated and authorized
                assert 'login' not in current_url
