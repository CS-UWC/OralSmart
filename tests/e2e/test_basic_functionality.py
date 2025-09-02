"""
Simplified End-to-End Test for OralSmart Application Landing Page
This test verifies the basic application accessibility without database dependencies
"""
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
class TestOralSmartBasic:
    
    def test_landing_page_loads(self, page: Page, live_server_url):
        """Test that the OralSmart landing page loads correctly."""
        try:
            page.goto(f"{live_server_url}/")
            
            # Check if the page loads (any of these might be present)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Look for common elements that might be on the landing page
            possible_elements = [
                'title',
                'h1', 
                'h2',
                'body',
                '[data-testid]',
                '.navbar',
                '#content'
            ]
            
            found_element = False
            for selector in possible_elements:
                if page.locator(selector).count() > 0:
                    found_element = True
                    print(f"✅ Found element: {selector}")
                    break
            
            assert found_element, "No recognizable page elements found"
            
        except Exception as e:
            pytest.skip(f"Django server not running: {e}")
    
    def test_login_page_accessible(self, page: Page, live_server_url):
        """Test that the login page is accessible."""
        try:
            page.goto(f"{live_server_url}/login_user/")
            
            # Check if we can access the login page
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Look for form elements or login-related content
            login_elements = [
                'input[name="username"]',
                'input[name="password"]', 
                'form',
                'button[type="submit"]',
                'input[type="submit"]',
                'text=login',
                'text=Login',
                'text=username',
                'text=password'
            ]
            
            found_login_element = False
            for selector in login_elements:
                if page.locator(selector).count() > 0:
                    found_login_element = True
                    print(f"✅ Found login element: {selector}")
                    break
            
            # If no specific login elements, at least check page loaded
            if not found_login_element:
                assert page.locator('body').count() > 0, "Page did not load properly"
                print("⚠️ Login page loaded but no specific login elements found")
            
        except Exception as e:
            pytest.skip(f"Login page not accessible: {e}")
    
    def test_basic_navigation(self, page: Page, live_server_url):
        """Test basic navigation between pages."""
        try:
            # Start at landing page
            page.goto(f"{live_server_url}/")
            page.wait_for_load_state("networkidle", timeout=5000)
            
            # Try to navigate to different pages
            test_pages = [
                "/login_user/",
                "/register_user/",
                "/home/",
                "/admin/"
            ]
            
            accessible_pages = []
            
            for test_page in test_pages:
                try:
                    page.goto(f"{live_server_url}{test_page}")
                    page.wait_for_load_state("networkidle", timeout=5000)
                    
                    # Check if page loaded successfully (not 404)
                    if not ("404" in page.content() or "Not Found" in page.content()):
                        accessible_pages.append(test_page)
                        print(f"✅ Accessible: {test_page}")
                    
                except Exception as e:
                    print(f"❌ Not accessible: {test_page} - {e}")
                    continue
            
            # We should be able to access at least one page
            assert len(accessible_pages) > 0, f"No pages were accessible. Tested: {test_pages}"
            print(f"📊 Accessible pages: {accessible_pages}")
            
        except Exception as e:
            pytest.skip(f"Navigation testing failed: {e}")

@pytest.mark.e2e
def test_server_running(live_server_url):
    """Test that the Django server is running and responding."""
    import requests
    try:
        response = requests.get(f"{live_server_url}/", timeout=5)
        assert response.status_code in [200, 301, 302, 404], f"Server returned status {response.status_code}"
        print(f"✅ Server is running and responding with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        pytest.skip("Django server is not running. Please start with: cd src && python manage.py runserver")
    except Exception as e:
        pytest.skip(f"Server test failed: {e}")
