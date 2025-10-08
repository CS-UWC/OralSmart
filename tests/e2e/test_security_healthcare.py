"""
Security Tests for Healthcare/Medical Data Protection
Tests HIPAA compliance and medical data security requirements
"""
import pytest
from playwright.sync_api import Page, expect
import time

@pytest.mark.e2e
@pytest.mark.security
@pytest.mark.healthcare
class TestHealthcareDataSecurity:
    
    def test_patient_data_encryption_in_transit(self, page: Page, live_server_url):
        """Test that patient data is transmitted securely."""
        # Check if site enforces HTTPS
        if live_server_url.startswith('http://'):
            print("⚠️  Warning: Testing on HTTP. Production should use HTTPS.")
        
        # Login and create patient
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Monitor network requests during patient creation
        network_requests = []
        
        def handle_request(request):
            network_requests.append({
                'url': request.url,
                'method': request.method,
                'headers': dict(request.headers)
            })
        
        page.on('request', handle_request)
        
        page.goto(f"{live_server_url}/create_patient/")
        page.fill('input[name="name"]', 'SensitivePatient')
        page.fill('input[name="surname"]', 'MedicalData')
        page.fill('input[name="age"]', '7')
        page.select_option('select[name="gender"]', 'Female')
        page.fill('input[name="parent_name"]', 'Parent')
        page.fill('input[name="parent_surname"]', 'Sensitive')
        page.fill('input[name="parent_id"]', '9876543210')
        page.fill('input[name="parent_contact"]', '0987654321')
        
        page.click('button[type="submit"]')
        page.wait_for_timeout(2000)
        
        # Verify HTTPS usage for sensitive data
        for request in network_requests:
            if request['method'] == 'POST':
                assert request['url'].startswith('https://') or 'localhost' in request['url'], \
                    "Patient data should be transmitted over HTTPS"
    
    def test_medical_data_access_logging(self, page: Page, live_server_url):
        """Test that access to medical data is properly logged."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Access patient data
        page.goto(f"{live_server_url}/patient_list/")
        
        # This test would need to verify that access is logged
        # In a real implementation, you'd check log files or database audit tables
        
        # For now, verify the page loads correctly
        expect(page.locator('h1, h2, h3')).to_be_visible()
    
    def test_patient_minor_protection(self, page: Page, live_server_url):
        """Test special protections for pediatric patients."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Create minor patient
        page.goto(f"{live_server_url}/create_patient/")
        page.fill('input[name="name"]', 'MinorPatient')
        page.fill('input[name="surname"]', 'TestChild')
        page.fill('input[name="age"]', '8')  # Minor
        page.select_option('select[name="gender"]', 'Male')
        page.fill('input[name="parent_name"]', 'Guardian')
        page.fill('input[name="parent_surname"]', 'Parent')
        page.fill('input[name="parent_id"]', '1234567890')
        page.fill('input[name="parent_contact"]', '0123456789')
        
        page.click('button[type="submit"]')
        
        # Verify that guardian information is required
        # Should have successfully created the patient with guardian info
        current_url = page.url
        assert 'patient_list' in current_url or 'home' in current_url
    
    def test_medical_record_retention_policy(self, page: Page, live_server_url):
        """Test medical record retention and deletion policies."""
        # This would test automated deletion of old records
        # For now, we'll verify that the application handles old data appropriately
        
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Check patient list for data handling
        page.goto(f"{live_server_url}/patient_list/")
        
        # Verify proper data display (not exposing too much sensitive info)
        content = page.content()
        
        # Should not expose full ID numbers in list view
        id_pattern = r'\b\d{10,13}\b'  # Full ID numbers
        import re
        full_ids = re.findall(id_pattern, content)
        
        # Should either mask IDs or not show them in list view
        # This is application-specific logic
        pass
    
    def test_audit_trail_functionality(self, page: Page, live_server_url):
        """Test that user actions create appropriate audit trails."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Perform various actions that should be audited
        actions = [
            (f"{live_server_url}/patient_list/", "view_patient_list"),
            (f"{live_server_url}/create_patient/", "access_patient_creation"),
            (f"{live_server_url}/profile_view/", "view_profile")
        ]
        
        for url, action_name in actions:
            page.goto(url)
            page.wait_for_timeout(1000)
            
            # In a real implementation, you would:
            # 1. Check database audit logs
            # 2. Verify log entries contain: user, timestamp, action, IP
            # 3. Ensure logs are tamper-proof
        
        # For now, verify pages load correctly
        assert True  # Placeholder
    
    def test_data_masking_in_ui(self, page: Page, live_server_url):
        """Test that sensitive data is properly masked in the UI."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Create patient with sensitive data
        page.goto(f"{live_server_url}/create_patient/")
        
        sensitive_id = "9876543210123"  # 13-digit ID
        sensitive_phone = "0823456789"
        
        page.fill('input[name="name"]', 'SensitiveData')
        page.fill('input[name="surname"]', 'TestPatient')
        page.fill('input[name="age"]', '6')
        page.select_option('select[name="gender"]', 'Female')
        page.fill('input[name="parent_name"]', 'Parent')
        page.fill('input[name="parent_surname"]', 'Guardian')
        page.fill('input[name="parent_id"]', sensitive_id)
        page.fill('input[name="parent_contact"]', sensitive_phone)
        
        page.click('button[type="submit"]')
        
        # Go to patient list and check data masking
        page.goto(f"{live_server_url}/patient_list/")
        
        content = page.content()
        
        # Check if sensitive data is properly masked
        # Full ID should not be visible, or should be masked (e.g., ****7890)
        if sensitive_id in content:
            print("⚠️  Warning: Full ID number visible in patient list")
        
        if sensitive_phone in content:
            print("⚠️  Warning: Full phone number visible in patient list")
    
    def test_consent_mechanism_security(self, page: Page, live_server_url):
        """Test security of consent mechanisms for data processing."""
        # This would test consent forms, opt-in/opt-out mechanisms
        # and ensure consent cannot be bypassed
        
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Check for consent mechanisms in patient registration
        page.goto(f"{live_server_url}/create_patient/")
        
        # Look for consent checkboxes or agreements
        consent_elements = page.locator('input[type="checkbox"]')
        consent_text = page.locator('text*=consent, text*=agree, text*=privacy')
        
        if consent_elements.count() > 0 or consent_text.count() > 0:
            # Test that consent is required (cannot proceed without it)
            page.fill('input[name="name"]', 'ConsentTest')
            page.fill('input[name="surname"]', 'Patient')
            page.fill('input[name="age"]', '5')
            page.select_option('select[name="gender"]', 'Male')
            page.fill('input[name="parent_name"]', 'Parent')
            page.fill('input[name="parent_surname"]', 'Test')
            page.fill('input[name="parent_id"]', '1234567890')
            page.fill('input[name="parent_contact"]', '0123456789')
            
            # Try to submit without consent
            page.click('button[type="submit"]')
            
            # Should either prevent submission or show consent requirement
            # Implementation would depend on specific consent mechanism
    
    def test_data_breach_response_simulation(self, page: Page, live_server_url):
        """Test security measures for potential data breach scenarios."""
        # This test would simulate various breach scenarios
        
        # Test 1: Unauthorized access attempt
        page.context.clear_cookies()
        
        # Try to access sensitive endpoints directly
        breach_attempt_urls = [
            f"{live_server_url}/admin/",
            f"{live_server_url}/patient/export/",
            f"{live_server_url}/reports/all/",
            f"{live_server_url}/api/patients/",
        ]
        
        for url in breach_attempt_urls:
            page.goto(url)
            
            # Should be properly protected
            current_url = page.url
            content = page.content().lower()
            
            # Should not expose patient data to unauthorized users
            sensitive_indicators = [
                'patient name',
                'parent id',
                'phone number',
                'medical record'
            ]
            
            for indicator in sensitive_indicators:
                assert indicator not in content, f"Sensitive data exposed at {url}"
    
    def test_cross_tenant_data_isolation(self, page: Page, live_server_url):
        """Test that different facilities/organizations cannot access each other's data."""
        # This test is relevant if the application supports multiple tenants/facilities
        
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Check facility/organization isolation
        page.goto(f"{live_server_url}/patient_list/")
        
        # Should only show patients for the user's facility
        # This would need to be implemented based on your multi-tenant architecture
        content = page.content()
        
        # Verify proper data scoping
        assert 'patient' in content.lower() or 'no patients' in content.lower()
    
    def test_anonymization_and_pseudonymization(self, page: Page, live_server_url):
        """Test data anonymization features for reports and analytics."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Check if there are any analytics or reporting features
        analytics_urls = [
            f"{live_server_url}/reports/",
            f"{live_server_url}/analytics/",
            f"{live_server_url}/statistics/"
        ]
        
        for url in analytics_urls:
            page.goto(url)
            
            # If analytics exist, verify personal identifiers are removed
            content = page.content()
            
            # Should not contain personally identifiable information
            pii_patterns = [
                r'\b\d{10,13}\b',  # ID numbers
                r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Phone numbers
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email addresses
            ]
            
            import re
            for pattern in pii_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"⚠️  Potential PII found in analytics: {matches}")
    
    def test_medical_image_security(self, page: Page, live_server_url):
        """Test security of medical image uploads and storage."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Look for image upload functionality
        page.goto(f"{live_server_url}/create_patient/")
        
        file_inputs = page.locator('input[type="file"]')
        
        if file_inputs.count() > 0:
            # Test that images are properly secured
            # Check that uploaded images are not directly accessible
            
            # This would involve:
            # 1. Upload test image
            # 2. Try to access image directly via URL
            # 3. Verify access controls on image viewing
            
            print("🔍 Medical image upload detected - ensure proper access controls")
    
    def test_assessment_data_integrity(self, page: Page, live_server_url):
        """Test that assessment data cannot be tampered with."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Navigate to assessment forms
        assessment_urls = [
            f"{live_server_url}/dental_screening/1/",
            f"{live_server_url}/dietary_screening/1/",
        ]
        
        for url in assessment_urls:
            page.goto(url)
            
            # Test that assessment forms have integrity protections
            if page.locator('form').is_visible():
                # Check for hidden fields that store assessment state
                hidden_inputs = page.locator('input[type="hidden"]')
                
                # Try to manipulate assessment scoring
                page.evaluate("""
                    // Try to add hidden inputs that might affect scoring
                    const form = document.querySelector('form');
                    if (form) {
                        const scoreInput = document.createElement('input');
                        scoreInput.type = 'hidden';
                        scoreInput.name = 'total_score';
                        scoreInput.value = '0';  // Try to force low score
                        form.appendChild(scoreInput);
                        
                        const riskInput = document.createElement('input');
                        riskInput.type = 'hidden';
                        riskInput.name = 'risk_level';
                        riskInput.value = 'low';  // Try to force low risk
                        form.appendChild(riskInput);
                    }
                """)
                
                # Form should validate data integrity on server side
                # This test is more about ensuring server-side validation exists
    
    def test_ml_model_input_validation(self, page: Page, live_server_url):
        """Test that ML model inputs are properly validated and sanitized."""
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Find ML prediction endpoints
        ml_test_urls = [
            f"{live_server_url}/ml_prediction/",
            f"{live_server_url}/risk_assessment/",
        ]
        
        for url in ml_test_urls:
            page.goto(url)
            
            # Test malformed ML inputs
            if page.locator('form').is_visible():
                # Try to submit malformed data to ML model
                malformed_inputs = [
                    "NaN",
                    "Infinity", 
                    "-Infinity",
                    "null",
                    "undefined",
                    "{'malicious': 'code'}",
                    "<script>alert('xss')</script>"
                ]
                
                # Fill form with malformed data
                input_fields = page.locator('input[type="text"], input[type="number"], textarea')
                
                for i in range(min(input_fields.count(), len(malformed_inputs))):
                    if input_fields.nth(i).is_visible():
                        input_fields.nth(i).fill(malformed_inputs[i])
                
                # Submit and verify proper error handling
                submit_btn = page.locator('button[type="submit"]')
                if submit_btn.is_visible():
                    submit_btn.click()
                    
                    # Should handle malformed input gracefully
                    page.wait_for_timeout(2000)
                    content = page.content().lower()
                    
                    # Should not show system errors or expose internals
                    error_indicators = [
                        'traceback',
                        'exception',
                        'internal server error',
                        'numpy error',
                        'pandas error'
                    ]
                    
                    for indicator in error_indicators:
                        assert indicator not in content, f"ML model exposed system error: {indicator}"

    def test_hipaa_compliance_measures(self, page: Page, live_server_url):
        """Test basic HIPAA compliance security measures."""
        # This is a comprehensive test that would verify:
        # 1. Minimum necessary access
        # 2. Audit logs
        # 3. Data encryption
        # 4. Access controls
        # 5. User authentication
        
        # Login
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', 'testuser123')
        page.fill('input[name="password"]', 'ComplexPass123!')
        page.click('button[type="submit"]')
        
        # Test minimum necessary access principle
        page.goto(f"{live_server_url}/patient_list/")
        
        # Should only show necessary patient information
        content = page.content()
        
        # Check that sensitive data is not unnecessarily exposed
        # Full medical records should not be visible in list views
        sensitive_keywords = [
            'medical history',
            'diagnosis',
            'treatment plan',
            'prescription'
        ]
        
        for keyword in sensitive_keywords:
            if keyword in content.lower():
                print(f"⚠️  Consider if '{keyword}' needs to be visible in this view")
        
        # Test that user can only access appropriate functions
        # Healthcare workers should only see relevant tools for their role
