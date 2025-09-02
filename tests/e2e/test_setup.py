"""
Basic setup test to verify E2E testing environment is working
"""
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_basic_setup(page: Page):
    """Test that Playwright is working correctly."""
    page.goto('https://httpbin.org/html')
    expect(page.locator('h1')).to_contain_text('Herman Melville')

@pytest.mark.e2e 
def test_django_setup(db):
    """Test that Django database setup is working."""
    # This test just verifies that the Django database fixture works
    assert True  # If we get here, Django setup worked

@pytest.mark.e2e
def test_user_creation(test_user):
    """Test that user creation fixture works."""
    if test_user:
        assert test_user.username == 'testuser123'
        assert test_user.email == 'testuser@example.com'
    else:
        pytest.skip("User model not available")
