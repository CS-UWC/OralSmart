import pytest
import os
import sys
import django
from pathlib import Path

# Add the src directory to Python path so we can import Django modules
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / 'src'
sys.path.insert(0, str(SRC_DIR))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oralsmart.test_settings')

try:
    django.setup()
except Exception as e:
    print(f"Warning: Could not setup Django: {e}")

from django.conf import settings
from playwright.sync_api import sync_playwright

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except Exception:
    User = None

@pytest.fixture(scope="session")
def django_db_setup():
    """Set up the database for testing - use existing database."""
    # We'll use the existing database that was already migrated
    # This avoids the async/sync issues with test database creation
    pass

@pytest.fixture(scope="session")
def playwright_context():
    """Create a Playwright browser context for the session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True for headless
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True
        )
        yield context
        context.close()
        browser.close()

@pytest.fixture(scope="function")
def page(playwright_context):
    """Create a new page for each test."""
    page = playwright_context.new_page()
    yield page
    page.close()

@pytest.fixture
def live_server_url():
    """Django live server URL for testing."""
    # For now, assume Django server is running on localhost:8000
    # In production, this would use Django's LiveServerTestCase
    return "http://localhost:8000"

@pytest.fixture
def test_user(db):
    """Create an active test user for authentication tests."""
    if User is None:
        pytest.skip("Django User model not available")
    
    from userprofile.models import Profile
    
    # Clean up any existing test user first
    User.objects.filter(username='testuser123').delete()
    
    # Create active user (skip email activation for testing)
    user = User.objects.create_user(
        username='testuser123',
        email='testuser@example.com',
        password='ComplexPass123!',
        first_name='Test',
        last_name='User',
        is_active=True  # Make user active for testing
    )
    
    # Create associated profile if needed
    try:
        Profile.objects.create(
            user=user,
            profession='Dentist',
            health_professional_body='ADA',
            reg_num='TEST123',
            email=user.email
        )
    except Exception:
        pass  # Profile creation is optional for basic auth tests
    
    return user

@pytest.fixture
def staff_user(db):
    """Create a staff user."""
    if User is None:
        pytest.skip("Django User model not available")
    
    # Clean up any existing staff user first
    User.objects.filter(username='staffuser').delete()
        
    return User.objects.create_user(
        username='staffuser',
        email='staff@example.com',
        password='staffpassword123',
        first_name='Staff',
        last_name='User',
        is_staff=True
    )

@pytest.fixture
def superuser(db):
    """Create a superuser."""
    if User is None:
        pytest.skip("Django User model not available")
    
    # Clean up any existing superuser first
    User.objects.filter(username='admin').delete()
        
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword123',
        first_name='Admin',
        last_name='User'
    )
