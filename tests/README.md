# End-to-End Testing for OralSmart

This directory contains comprehensive end-to-end tests for the OralSmart pediatric oral health risk assessment application.

## 🧪 Test Suites

### 1. Authentication Tests (`test_authentication.py`)
- User registration workflow
- Login/logout functionality  
- Access control and authorization
- Staff user permissions

### 2. Patient Management Tests (`test_patient_management.py`)
- Patient creation and registration
- Patient list and search functionality
- Form validation
- Patient profile access

### 3. Assessment Form Tests (`test_assessment_forms.py`)
- Dental screening form completion
- Dietary screening form completion
- Form validation and error handling
- Assessment workflow navigation

### 4. ML Risk Prediction Tests (`test_ml_prediction.py`)
- Complete ML prediction workflow
- High-risk scenario testing
- Low-risk scenario testing
- Partial assessment handling
- API endpoint testing

### 5. Report Generation Tests (`test_report_generation.py`)
- Patient report viewing
- PDF report generation
- Professional vs patient-friendly reports
- Email functionality
- Report data accuracy
- Responsive design testing

### 6. File Upload Tests (`test_file_uploads.py`)
- Image upload functionality
- File type validation
- Size limit validation
- Multiple file uploads
- Image preview
- Upload progress indication
- Image deletion

## 🚀 Quick Start

### Prerequisites
```bash
# Install dependencies (already done in your environment)
pip install pytest pytest-playwright pytest-django pillow

# Install Playwright browsers (already done)
playwright install
```

### Running Tests

#### Use the Test Runner Script (Recommended)
```bash
# Run all E2E tests
python run_e2e_tests.py --all

# Run smoke tests (critical functionality)
python run_e2e_tests.py --smoke

# Run specific test suites
python run_e2e_tests.py --auth          # Authentication tests
python run_e2e_tests.py --patient       # Patient management
python run_e2e_tests.py --assessment    # Assessment forms
python run_e2e_tests.py --ml            # ML prediction workflow
python run_e2e_tests.py --reports       # Report generation
python run_e2e_tests.py --uploads       # File uploads

# Browser options
python run_e2e_tests.py --all --browser firefox
python run_e2e_tests.py --all --browser webkit
python run_e2e_tests.py --all --headless        # Run in headless mode

# List available test suites
python run_e2e_tests.py --list
```

#### Direct Pytest Commands
```bash
# Run all E2E tests
pytest tests/e2e/ -m e2e -v

# Run specific test files
pytest tests/e2e/test_authentication.py -v
pytest tests/e2e/test_patient_management.py -v

# Run with specific browser
pytest tests/e2e/ --browser firefox --headed

# Run specific test methods
pytest tests/e2e/test_authentication.py::TestAuthentication::test_user_login_success -v
```

## 🔧 Configuration

### Test Configuration (`pytest.ini`)
The main pytest configuration includes:
- Django settings module
- Test discovery patterns
- Browser configurations
- Custom markers for test organization

### Test Fixtures (`conftest.py`)
Provides shared fixtures:
- `playwright_context`: Browser context management
- `page`: Page instance for each test
- `test_user`: Test user creation
- `staff_user`: Staff user for permission testing
- `superuser`: Admin user for admin testing
- `django_db_setup`: Database setup for tests

## 📋 Test Markers

Tests are organized with pytest markers:
- `@pytest.mark.e2e`: All end-to-end tests
- `@pytest.mark.auth`: Authentication tests
- `@pytest.mark.patient`: Patient management tests
- `@pytest.mark.assessment`: Assessment form tests
- `@pytest.mark.ml`: ML prediction tests
- `@pytest.mark.reports`: Report generation tests
- `@pytest.mark.uploads`: File upload tests

## 🏗️ Test Structure

Each test class follows this structure:
```python
@pytest.mark.e2e
@pytest.mark.specific_marker
class TestFeatureName:
    def setup_method(self, method):
        """Setup for each test method"""
        
    def test_positive_scenario(self, page, live_server_url, test_user):
        """Test successful workflow"""
        
    def test_negative_scenario(self, page, live_server_url):
        """Test error handling"""
        
    def test_edge_cases(self, page, live_server_url):
        """Test boundary conditions"""
```

## 🎯 Key Testing Scenarios

### Critical User Journeys
1. **Complete Patient Assessment Workflow**
   - User login → Patient creation → Dental screening → Dietary screening → Risk prediction → Report generation

2. **Healthcare Professional Workflow**
   - Login → Patient search → View existing assessment → Generate professional report → Email report

3. **New User Experience**
   - Registration → Profile setup → First patient creation → Assessment completion

### Data Validation Testing
- Form field validation
- File upload validation
- ML model input validation
- Report generation with incomplete data

### Error Handling
- Network connectivity issues
- Server errors
- Invalid user input
- File upload failures

## 🔍 Debugging Tests

### Running Tests in Debug Mode
```bash
# Run with browser visible (non-headless)
python run_e2e_tests.py --all --verbose

# Run single test with debugging
pytest tests/e2e/test_authentication.py::TestAuthentication::test_user_login_success -v -s
```

### Common Issues and Solutions

1. **Test User Creation Fails**
   - Ensure database is properly migrated
   - Check Django settings for test database

2. **Element Not Found Errors**
   - Verify selectors match your actual HTML
   - Add waits for dynamic content loading
   - Check if elements are hidden/visible

3. **File Upload Tests Fail**
   - Ensure PIL (Pillow) is installed
   - Check file permissions for temp directory
   - Verify upload endpoints exist

4. **ML Prediction Tests Fail**
   - Ensure ML models are trained and available
   - Check if prediction endpoints are accessible
   - Verify assessment data creates valid predictions

## 📊 Test Reporting

### HTML Test Reports
```bash
# Generate HTML test report
pytest tests/e2e/ --html=reports/e2e_test_report.html --self-contained-html
```

### Coverage Reports
```bash
# Run tests with coverage
pytest tests/e2e/ --cov=src --cov-report=html
```

## 🚀 Continuous Integration

### GitHub Actions Example
```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-playwright pytest-django pillow
          playwright install
      
      - name: Run E2E tests
        run: python run_e2e_tests.py --all --headless --browser chromium
```

## 📝 Writing New Tests

### Test Naming Convention
- Files: `test_feature_name.py`
- Classes: `TestFeatureName`
- Methods: `test_specific_scenario`

### Best Practices
1. **Use Page Object Pattern** for complex pages
2. **Create reusable helper methods** for common actions
3. **Use proper waits** instead of `time.sleep()`
4. **Clean up test data** after each test
5. **Make tests independent** - don't rely on test order
6. **Use meaningful assertions** with clear error messages

### Example Test Template
```python
@pytest.mark.e2e
@pytest.mark.your_feature
class TestYourFeature:
    def test_your_scenario(self, page: Page, live_server_url, test_user):
        """Test description of what this test validates."""
        # Arrange - Set up test conditions
        self.login_user(page, live_server_url)
        
        # Act - Perform the action being tested
        page.goto(f"{live_server_url}/your-endpoint/")
        page.click('button[type="submit"]')
        
        # Assert - Verify expected outcomes
        expect(page.locator('text=Success')).to_be_visible()
        assert 'success' in page.url.lower()
```

## 🎯 Next Steps

1. **Customize selectors** in tests to match your actual HTML elements
2. **Update patient ID extraction** methods based on your URL patterns  
3. **Configure live server URL** based on your development setup
4. **Add visual regression testing** using Playwright screenshots
5. **Implement API testing** for backend endpoints
6. **Add performance testing** for critical user journeys

## 📞 Support

For questions or issues with the test suite:
1. Check the console output for specific error messages
2. Verify that your Django application is running correctly
3. Ensure all dependencies are properly installed
4. Review the Playwright documentation for selector and assertion help
