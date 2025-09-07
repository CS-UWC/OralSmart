# 🔐 Security Testing Guide for OralSmart

This document outlines comprehensive security tests that can be implemented for your Django OralSmart application. The tests are organized by security domain and include both automated E2E tests and manual testing procedures.

## 📋 **Security Test Categories**

### **1. Authentication & Session Security**
**File**: `test_security_auth.py`

| Test | Description | Security Risk |
|------|-------------|---------------|
| `test_password_complexity_enforcement` | Validates password strength requirements | Weak authentication |
| `test_session_timeout_behavior` | Tests session management and timeout | Session hijacking |
| `test_brute_force_protection` | Tests multiple failed login attempts | Brute force attacks |
| `test_concurrent_session_handling` | Tests multiple concurrent user sessions | Session management |
| `test_redirect_after_login` | Validates post-login redirect security | Open redirect |
| `test_user_enumeration_protection` | Ensures login errors don't reveal user existence | Information disclosure |

### **2. CSRF Protection**
**File**: `test_security_csrf.py`

| Test | Description | Security Risk |
|------|-------------|---------------|
| `test_csrf_token_presence_in_forms` | Verifies CSRF tokens in all forms | CSRF attacks |
| `test_csrf_protection_on_post_requests` | Tests POST request CSRF validation | CSRF attacks |
| `test_csrf_token_validation` | Tests invalid CSRF token rejection | CSRF attacks |
| `test_csrf_token_in_ajax_requests` | Tests CSRF in AJAX requests | CSRF attacks |
| `test_referer_header_validation` | Tests referer header validation | CSRF attacks |

### **3. Input Validation & Injection Protection**
**File**: `test_security_injection.py`

| Test | Description | Security Risk |
|------|-------------|---------------|
| `test_sql_injection_protection` | Tests SQL injection attack prevention | Data breach |
| `test_xss_protection` | Tests Cross-Site Scripting protection | XSS attacks |
| `test_file_upload_security` | Tests malicious file upload protection | Code execution |
| `test_path_traversal_protection` | Tests directory traversal attack prevention | File system access |
| `test_command_injection_protection` | Tests OS command injection prevention | System compromise |
| `test_ldap_injection_protection` | Tests LDAP injection prevention | Authentication bypass |
| `test_header_injection_protection` | Tests HTTP header injection prevention | Header manipulation |

### **4. Authorization & Access Control**
**File**: `test_security_access_control.py`

| Test | Description | Security Risk |
|------|-------------|---------------|
| `test_unauthorized_access_protection` | Tests unauthenticated user restrictions | Unauthorized access |
| `test_user_data_isolation` | Tests user data separation | Data leakage |
| `test_admin_area_protection` | Tests admin area access restrictions | Privilege escalation |
| `test_direct_object_reference_protection` | Tests IDOR prevention | Unauthorized data access |
| `test_privilege_escalation_protection` | Tests role-based access controls | Privilege escalation |
| `test_session_fixation_protection` | Tests session ID changes after login | Session fixation |
| `test_password_change_security` | Tests password change security measures | Account compromise |
| `test_account_lockout_protection` | Tests account lockout mechanisms | Brute force attacks |

### **5. Data Protection & Privacy**
**File**: `test_security_data_protection.py`

| Test | Description | Security Risk |
|------|-------------|---------------|
| `test_sensitive_data_not_in_source` | Tests for exposed secrets in HTML | Information disclosure |
| `test_error_page_information_disclosure` | Tests error page information leakage | Information disclosure |
| `test_debug_information_not_exposed` | Tests debug mode security | Information disclosure |
| `test_http_security_headers` | Tests security HTTP headers | Various attacks |
| `test_cookie_security_attributes` | Tests cookie security flags | Session hijacking |
| `test_password_field_autocomplete` | Tests password autocomplete settings | Credential theft |
| `test_sensitive_data_caching_prevention` | Tests cache control headers | Data exposure |
| `test_personal_data_protection` | Tests medical data protection | Privacy breach |
| `test_data_export_security` | Tests data export authorization | Data breach |

---

## 🚀 **Running the Security Tests**

### **Prerequisites**
```bash
# Install testing dependencies
pip install pytest playwright pytest-django

# Install Playwright browsers
python -m playwright install
```

### **Run All Security Tests**
```bash
# Run all security tests
pytest tests/e2e/test_security_*.py -v -m security

# Run specific security category
pytest tests/e2e/test_security_auth.py -v
pytest tests/e2e/test_security_csrf.py -v
pytest tests/e2e/test_security_injection.py -v
pytest tests/e2e/test_security_access_control.py -v
pytest tests/e2e/test_security_data_protection.py -v
```

### **Generate Security Test Report**
```bash
# Generate HTML report
pytest tests/e2e/test_security_*.py --html=security_report.html --self-contained-html

# Generate coverage report
pytest tests/e2e/test_security_*.py --cov=src --cov-report=html
```

---

## ⚠️ **Additional Security Tests to Consider**

### **6. Infrastructure Security Tests**

**Manual/Unit Tests for**:
- SSL/TLS configuration validation
- Database connection security
- Environment variable protection
- Docker container security
- Network security configurations

### **7. API Security Tests** 

**If you have APIs**:
- Authentication token validation
- Rate limiting tests
- API versioning security
- JSON/XML injection tests
- API endpoint enumeration protection

### **8. File Upload Security Tests**

**Enhanced file upload security**:
```python
def test_malicious_file_upload_prevention():
    # Test malicious file extensions
    malicious_extensions = ['.php', '.exe', '.sh', '.bat', '.jsp']
    
    # Test MIME type validation
    # Test file size limits
    # Test virus/malware detection
    # Test file content validation
```

### **9. Business Logic Security Tests**

**Application-specific tests**:
- Patient data access controls
- Medical report authorization
- ML model input validation
- Assessment form tampering protection
- Age-based restriction validation

---

## 🛡️ **Security Configuration Recommendations**

### **Django Settings Security Checklist**

```python
# SECURITY SETTINGS TO VERIFY

# 1. Debug and Secret Key
DEBUG = False  # Never True in production
SECRET_KEY = os.environ.get('SECRET_KEY')  # From environment

# 2. HTTPS and Security Headers
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# 3. Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 4. CSRF Protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# 5. Allowed Hosts
ALLOWED_HOSTS = ['your-domain.com']  # Specific domains only

# 6. Database Security
# Use strong database passwords
# Enable database SSL connections
```

### **Additional Security Middleware**

```python
# Consider adding to MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Add rate limiting middleware
    'django_ratelimit.middleware.RatelimitMiddleware',
    # Add security headers middleware
    'django_csp.middleware.CSPMiddleware',
    # Existing middleware...
]
```

---

## 📊 **Security Test Metrics**

### **Coverage Goals**
- **Authentication**: 95%+ coverage of auth flows
- **Authorization**: 100% coverage of access controls
- **Input Validation**: 90%+ coverage of user inputs
- **Data Protection**: 100% coverage of sensitive data handling

### **Performance Benchmarks**
- Login attempts: < 3 failed attempts should not cause delays
- Session timeout: Should be configurable (15-30 minutes)
- CSRF validation: Should not impact performance significantly

---

## 🔍 **Manual Security Testing**

### **Penetration Testing Tools**
- **OWASP ZAP**: Automated security scanner
- **Burp Suite**: Manual penetration testing
- **Nmap**: Network security scanning
- **SQLmap**: SQL injection testing

### **Security Code Review**
- Review all `@login_required` decorators
- Check SQL query construction
- Validate all user input handling
- Review file upload implementations
- Check error handling and logging

---

## 📝 **Security Test Maintenance**

### **Regular Updates**
1. **Monthly**: Review and update test data
2. **Quarterly**: Add tests for new features
3. **Annually**: Comprehensive security audit
4. **As needed**: Update tests for new vulnerabilities

### **Security Monitoring**
- Set up automated security testing in CI/CD
- Monitor security headers with tools like securityheaders.com
- Regular dependency vulnerability scanning
- Log analysis for security incidents

---

This comprehensive security testing framework will help ensure your OralSmart application maintains strong security posture while protecting sensitive medical data and user information.
