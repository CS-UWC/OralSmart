"""
Debug script to understand the assessment form structure
"""
import sys
import os
sys.path.append('src')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oralsmart.test_settings')
django.setup()

from playwright.sync_api import sync_playwright
import time

def debug_assessment_form():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible browser for debugging
        page = browser.new_page()
        
        try:
            # Login
            page.goto("http://localhost:8000/login_user/")
            page.fill('input[name="username"]', 'testuser123')
            page.fill('input[name="password"]', 'ComplexPass123!')
            page.click('button[type="submit"]')
            page.wait_for_url("http://localhost:8000/home/")
            
            # Create patient and navigate to dental screening
            page.goto("http://localhost:8000/create_patient/")
            page.fill('input[name="name"]', 'Debug')
            page.fill('input[name="surname"]', 'Patient')
            page.select_option('select[name="age"]', '2')
            page.select_option('select[name="gender"]', 'Male')
            page.fill('input[name="parent_name"]', 'Parent')
            page.fill('input[name="parent_surname"]', 'Debug')
            page.fill('input[name="parent_id"]', '1234567890123')
            page.fill('input[name="parent_contact"]', '0123456789')
            
            # Click dental screening button
            page.click('button[onclick="submitAndRedirect(\'dental\')"]')
            page.wait_for_load_state('networkidle', timeout=10000)
            
            print(f"Current URL: {page.url}")
            
            # Take screenshot
            page.screenshot(path="debug_dental_form.png")
            
            # Check what elements are visible
            print("Checking form structure...")
            
            # Check if sections exist
            section_one = page.locator('#sectionOne')
            print(f"Section One exists: {section_one.count() > 0}")
            if section_one.count() > 0:
                print(f"Section One visible: {section_one.is_visible()}")
            
            # Check for first checkbox
            sa_citizen_yes = page.locator('#sa_citizen_yes')
            print(f"SA Citizen Yes checkbox exists: {sa_citizen_yes.count() > 0}")
            if sa_citizen_yes.count() > 0:
                print(f"SA Citizen Yes checkbox visible: {sa_citizen_yes.is_visible()}")
            
            # Wait so we can see the form
            print("Sleeping for 10 seconds so you can see the form...")
            time.sleep(10)
            
            # Try to fill just the first field
            print("Trying to check first checkbox...")
            try:
                if sa_citizen_yes.is_visible():
                    sa_citizen_yes.check()
                    print("Successfully checked SA Citizen Yes")
                else:
                    print("SA Citizen Yes not visible")
            except Exception as e:
                print(f"Error checking SA Citizen: {e}")
                
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="debug_error.png")
        
        finally:
            browser.close()

if __name__ == "__main__":
    debug_assessment_form()
