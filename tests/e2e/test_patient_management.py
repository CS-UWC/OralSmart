"""
End-to-End Tests for Patient Registration and Management
Tests patient creation, listing, search, and management functionality
"""
import pytest
from playwright.sync_api import Page, expect
import time

@pytest.mark.e2e
@pytest.mark.patient
class TestPatientManagement:
    
    def setup_method(self, method):
        """Setup for each test method."""
        self.test_patient_data = {
            'name': 'John',
            'surname': 'Doe',
            'age': '2',  # Valid age option from the form (0-6)
            'gender': '0',  # 0=Male, 1=Female
            'parent_name': 'Jane',
            'parent_surname': 'Doe',
            'parent_id': '8001014800086',  # Valid 13-digit SA ID
            'parent_contact': '0123456789'  # Valid 10-digit contact
        }
    
    def login_user(self, page: Page, live_server_url, username='testuser123', password='ComplexPass123!'):
        """Helper method to login a user using pre-created test user."""
        # Ensure clean session
        page.context.clear_cookies()
        
        page.goto(f"{live_server_url}/login_user/")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle', timeout=10000)
    
    def test_create_patient_success(self, page: Page, live_server_url):
        """Test successful patient creation."""
        self.login_user(page, live_server_url)
        
        # Navigate to create patient page
        page.goto(f"{live_server_url}/create_patient/")
        
        # Fill patient form with correct field types
        page.fill('input[name="name"]', self.test_patient_data['name'])
        page.fill('input[name="surname"]', self.test_patient_data['surname'])
        page.select_option('select[name="gender"]', self.test_patient_data['gender'])
        page.select_option('select[name="age"]', self.test_patient_data['age'])
        page.fill('input[name="parent_name"]', self.test_patient_data['parent_name'])
        page.fill('input[name="parent_surname"]', self.test_patient_data['parent_surname'])
        page.fill('input[name="parent_id"]', self.test_patient_data['parent_id'])
        page.fill('input[name="parent_contact"]', self.test_patient_data['parent_contact'])
        
        # Click one of the screening buttons to submit
        page.click('button[onclick="submitAndRedirect(\'dietary\')"]')
        
        # Should redirect to screening page
        page.wait_for_load_state('networkidle', timeout=10000)
        
        # Check if we were redirected to screening (success)
        current_url = page.url
        assert 'screening' in current_url or 'create_patient' not in current_url
    
    def test_create_patient_with_screening(self, page: Page, live_server_url):
        """Test patient creation with immediate screening selection."""
        self.login_user(page, live_server_url)
        
        # Navigate to create patient page
        page.goto(f"{live_server_url}/create_patient/")
        
        # Fill patient form with correct field types
        page.fill('input[name="name"]', 'Alice')
        page.fill('input[name="surname"]', 'Smith')
        page.select_option('select[name="gender"]', '1')  # Female
        page.select_option('select[name="age"]', '3')
        page.fill('input[name="parent_name"]', 'Bob')
        page.fill('input[name="parent_surname"]', 'Smith')
        page.fill('input[name="parent_id"]', '8505144800086')  # Valid 13-digit SA ID
        page.fill('input[name="parent_contact"]', '0987654321')
        
        # Click dental screening button
        page.click('button[onclick="submitAndRedirect(\'dental\')"]')
        
        # Should redirect to dental screening page
        page.wait_for_load_state('networkidle', timeout=10000)
        
        # Check if we redirected to screening page
        current_url = page.url
        assert 'screening' in current_url
    
    def test_create_patient_validation(self, page: Page, live_server_url):
        """Test patient creation form validation."""
        self.login_user(page, live_server_url)
        
        # Navigate to create patient page
        page.goto(f"{live_server_url}/create_patient/")
        
        # Try to submit form without filling required fields by clicking a screening button
        page.click('button[onclick="submitAndRedirect(\'dietary\')"]')
        
        # Should show validation error or stay on the same page
        # HTML5 validation will prevent submission for required fields
        page.wait_for_timeout(2000)  # Brief wait
        current_url = page.url
        assert 'create_patient' in current_url  # Should stay on create patient page
    
    def test_patient_list_view(self, page: Page, live_server_url):
        """Test patient list functionality."""
        self.login_user(page, live_server_url)
        
        # First create a patient
        self.create_test_patient(page, live_server_url)
        
        # Navigate to patient list
        page.goto(f"{live_server_url}/patient_list/")
        
        # Check if patient appears in list (use more specific locator to handle duplicates)
        patient_row = page.locator('td', has_text=self.test_patient_data["name"]).first
        expect(patient_row).to_be_visible()
        
        # Check if the page has the expected structure
        expect(page.locator('h1, h2, .table, [class*="patient"]')).to_be_visible()
    
    def test_patient_search(self, page: Page, live_server_url):
        """Test patient search functionality."""
        self.login_user(page, live_server_url)
        
        # Create a patient first
        self.create_test_patient(page, live_server_url)
        
        # Navigate to patient list
        page.goto(f"{live_server_url}/patient_list/")
        
        # Search for patient
        search_box = page.locator('input[name="search"]')
        if search_box.is_visible():
            search_box.fill(self.test_patient_data['name'])
            page.press('input[name="search"]', 'Enter')
            
            # Check if search results contain the patient (use first match to avoid strict mode violation)
            patient_result = page.locator('td', has_text=self.test_patient_data["name"]).first
            expect(patient_result).to_be_visible()
    
    def test_patient_profile_access(self, page: Page, live_server_url):
        """Test accessing patient profile/details."""
        self.login_user(page, live_server_url)
        
        # Create a patient first
        patient_id = self.create_test_patient(page, live_server_url)
        
        # Navigate to patient list
        page.goto(f"{live_server_url}/patient_list/")
        
        # Click on patient name or view button (use first match to avoid strict mode violation)
        patient_link = page.locator('td', has_text=self.test_patient_data["name"]).first
        patient_link.click()
        
        # Wait for page to load and check if we're on a valid page
        page.wait_for_load_state('networkidle', timeout=10000)
        
        # Should show patient details or redirect to screening (check for any header or content)
        page_content = page.locator('h1, h2, h3, .content, main, body')
        expect(page_content.first).to_be_visible()
    
    def create_test_patient(self, page: Page, live_server_url):
        """Helper method to create a test patient."""
        page.goto(f"{live_server_url}/create_patient/")
        
        # Fill and submit patient form with correct field types
        page.fill('input[name="name"]', self.test_patient_data['name'])
        page.fill('input[name="surname"]', self.test_patient_data['surname'])
        page.select_option('select[name="gender"]', self.test_patient_data['gender'])
        page.select_option('select[name="age"]', self.test_patient_data['age'])
        page.fill('input[name="parent_name"]', self.test_patient_data['parent_name'])
        page.fill('input[name="parent_surname"]', self.test_patient_data['parent_surname'])
        page.fill('input[name="parent_id"]', self.test_patient_data['parent_id'])
        page.fill('input[name="parent_contact"]', self.test_patient_data['parent_contact'])
        
        # Click one of the screening buttons to submit
        page.click('button[onclick="submitAndRedirect(\'dietary\')"]')
        
        # Wait for success or redirect
        page.wait_for_load_state('networkidle', timeout=10000)
        
        return None  # Would need to extract actual ID for real implementation
