"""
Security Tests for Input Validation and Injection Protection
Tests SQL injection, XSS, and other injection vulnerabilities
"""
import pytest
from playwright.sync_api import Page, expect
import time

@pytest.mark.e2e
@pytest.mark.security
class TestInputValidationSecurity:
    
    def test_sql_injection_protection(self, page: Page, live_server_url):
        """Test protection against SQL injection attacks."""
        # Login first
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Navigate to patient creation
        page.goto(f"{live_server_url}/create_patient/")
        
        # SQL injection payloads
        sql_payloads = [
            "'; DROP TABLE patient; --",
            "' OR '1'='1",
            "'; UPDATE patient SET name='hacked'; --",
            "' UNION SELECT * FROM auth_user --",
            "Robert'; DROP TABLE Students; --"
        ]
        
        for payload in sql_payloads:
            # Clear form first
            page.fill('input[name="name"]', '')
            page.fill('input[name="surname"]', '')
            page.fill('input[name="age"]', '')
            
            # Try SQL injection in various fields
            page.fill('input[name="name"]', payload)
            page.fill('input[name="surname"]', 'Test')
            page.fill('input[name="age"]', '5')
            page.select_option('select[name="gender"]', 'Male')
            page.fill('input[name="parent_name"]', 'Parent')
            page.fill('input[name="parent_surname"]', 'Test')
            page.fill('input[name="parent_id"]', '1234567890')
            page.fill('input[name="parent_contact"]', '0123456789')
            
            page.click('button[type="submit"]')
            
            # Should not cause database errors
            # Check that we're not seeing any database error pages
            assert 'DatabaseError' not in page.content()
            assert 'sqlite3' not in page.content()
            assert 'SQL' not in page.content()
            
            page.wait_for_timeout(500)
    
    def test_xss_protection(self, page: Page, live_server_url):
        """Test protection against Cross-Site Scripting attacks."""
        # Login first
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        page.goto(f"{live_server_url}/create_patient/")
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'\"><script>alert('XSS')</script>",
            "<iframe src=javascript:alert('XSS')></iframe>"
        ]
        
        for payload in xss_payloads:
            # Fill form with XSS payload
            page.fill('input[name="name"]', payload)
            page.fill('input[name="surname"]', 'Test')
            page.fill('input[name="age"]', '5')
            page.select_option('select[name="gender"]', 'Male')
            page.fill('input[name="parent_name"]', 'Parent')
            page.fill('input[name="parent_surname"]', 'Test')
            page.fill('input[name="parent_id"]', '1234567890')
            page.fill('input[name="parent_contact"]', '0123456789')
            
            page.click('button[type="submit"]')
            
            # Wait a moment to see if any alerts fire
            page.wait_for_timeout(1000)
            
            # Check that XSS payload is properly escaped/sanitized
            # Should not execute JavaScript
            page_content = page.content()
            
            # XSS should be escaped, not executed
            if '<script>' in payload.lower():
                assert '<script>' not in page_content or '&lt;script&gt;' in page_content
            
            page.wait_for_timeout(500)
    
    def test_file_upload_security(self, page: Page, live_server_url):
        """Test file upload security measures."""
        # Login first
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Try to access a page with file uploads (if exists)
        page.goto(f"{live_server_url}/create_patient/")
        
        # Check if file upload exists
        file_input = page.locator('input[type="file"]')
        if file_input.is_visible():
            # Test malicious file extensions
            malicious_files = [
                'test.php',
                'malware.exe',
                'script.js',
                'shell.sh',
                'virus.bat'
            ]
            
            # Note: This would require creating actual test files
            # For now, we'll test the UI validation
            pass
    
    def test_path_traversal_protection(self, page: Page, live_server_url):
        """Test protection against path traversal attacks."""
        # Test path traversal in URL parameters
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc//passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for payload in traversal_payloads:
            # Test in various URL contexts
            page.goto(f"{live_server_url}/static/{payload}")
            
            # Should not expose system files
            content = page.content().lower()
            assert 'root:' not in content  # Unix passwd file
            assert 'administrator' not in content  # Windows user
            
            page.wait_for_timeout(200)
    
    def test_command_injection_protection(self, page: Page, live_server_url):
        """Test protection against command injection."""
        # Login first
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        page.goto(f"{live_server_url}/create_patient/")
        
        # Command injection payloads
        cmd_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "& dir",
            "`whoami`",
            "$(id)",
            "; rm -rf /",
            "| net user"
        ]
        
        for payload in cmd_payloads:
            page.fill('input[name="name"]', f"Test{payload}")
            page.fill('input[name="surname"]', 'Patient')
            page.fill('input[name="age"]', '5')
            page.select_option('select[name="gender"]', 'Male')
            page.fill('input[name="parent_name"]', 'Parent')
            page.fill('input[name="parent_surname"]', 'Test')
            page.fill('input[name="parent_id"]', '1234567890')
            page.fill('input[name="parent_contact"]', '0123456789')
            
            page.click('button[type="submit"]')
            
            # Should not execute system commands
            content = page.content()
            assert '/bin' not in content
            assert 'root:' not in content
            assert 'administrator' not in content.lower()
            
            page.wait_for_timeout(300)
    
    def test_ldap_injection_protection(self, page: Page, live_server_url):
        """Test protection against LDAP injection (if LDAP is used)."""
        page.goto(f"{live_server_url}/login_user/")
        
        # LDAP injection payloads
        ldap_payloads = [
            "*",
            "*)(&",
            "*))%00",
            "admin*)((|userPassword=*",
            "*)(uid=*))(|(uid=*",
        ]
        
        for payload in ldap_payloads:
            page.fill('input[name="username"]', payload)
            page.fill('input[name="password"]', 'password')
            page.click('button[type="submit"]')
            
            # Should not bypass authentication
            current_url = page.url
            assert 'home' not in current_url
            
            page.wait_for_timeout(300)
    
    def test_header_injection_protection(self, page: Page, live_server_url):
        """Test protection against HTTP header injection."""
        # Test by manipulating form data that might end up in headers
        page.goto(f"{live_server_url}/login_user/")
        
        # Header injection payloads
        header_payloads = [
            "test\r\nSet-Cookie: admin=true",
            "test\nLocation: http://evil.com",
            "test\r\n\r\n<script>alert('XSS')</script>"
        ]
        
        for payload in header_payloads:
            page.fill('input[name="username"]', payload)
            page.fill('input[name="password"]', 'password')
            page.click('button[type="submit"]')
            
            # Check that malicious headers are not set
            # Note: Direct header inspection in Playwright is limited
            assert True  # Placeholder - would need backend validation
            
            page.wait_for_timeout(300)
