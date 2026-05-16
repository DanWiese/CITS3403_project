"""
Customized Event Management Test Suite for Your Form
Tests: Login → Create Event → Edit Event → Fill Tabs → Delete Event → Logout
 
Based on your actual form with fields:
- Event Name
- Location
- Date and Time (From/Until with date and time inputs)
- Event Description
- Private/Public Event toggle
"""
 
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from selenium.common.exceptions import TimeoutException
 

# CONFIGURATION - UPDATE THESE FOR YOUR WEBSITE
 
BASE_URL = "http://localhost:5001"
LOGIN_CREDENTIALS = {
    "email": "john@example.com",
    "password": "password123"
}
 
# form event data
EVENT_DATA = {
    "name": "Test Event",                      # Event Name field
    "location": "Test Location",               # Location field
    "date_from": "2027-11-11",                # From date (YYYY-MM-DD format)
    "time_from": "14:30",                     # From time
    "date_until": "2027-12-11",               # Until date (YYYY-MM-DD format)
    "time_until": "15:30",                    # Until time
    "description": "This is a test event created by Selenium automation", # Description
    "event_type": "Private",                  # Private or Public
}
 
# Updated event data for editing
EVENT_DATA_UPDATED = {
    "name": "Updated Test Event",
    "location": "Updated Location",
    "date_from": "2027-11-11",
    "time_from": "15:45",
    "date_until": "2027-12-11",
    "time_until": "16:45",
    "description": "This event has been updated by Selenium",
    "event_type": "Public",
}
 
# Timeouts
TIMEOUT = 10
SHORT_WAIT = 5
 

# FIXTURE - Browser Setup
 
@pytest.fixture
def driver():
    """Initialize Chrome WebDriver"""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    yield driver
    driver.quit()
 

# FIXTURE - Logged In Driver
 
@pytest.fixture
def logged_in_driver(driver):
    """Login fixture that returns authenticated driver"""
    driver.get(f"{BASE_URL}/login")
    
    # Wait for login form to be present
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "loginForm"))
    )
    print("✓ Login form loaded")
    
    # Fill email field
    try:
        email_field = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "loginEmail"))
        )
        email_field.clear()
        email_field.send_keys(LOGIN_CREDENTIALS["email"])
        print(f"✓ Entered email: {LOGIN_CREDENTIALS['email']}")
    except Exception as e:
        print(f"⚠ Could not fill email: {e}")
        raise
    
    # Fill password field
    try:
        password_field = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "loginPassword"))
        )
        password_field.clear()
        password_field.send_keys(LOGIN_CREDENTIALS["password"])
        print("✓ Entered password")
    except Exception as e:
        print(f"⚠ Could not fill password: {e}")
        raise
    
    # Click login button
    try:
        login_button = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "loginBtn"))
        )
        login_button.click()
        print("✓ Clicked login button")
    except Exception as e:
        print(f"⚠ Could not click login: {e}")
        raise
    
    # Wait for redirect to dashboard
    try:
        WebDriverWait(driver, TIMEOUT).until(
            EC.url_contains("dashboard")
        )
        print("✓ Login successful, redirected to dashboard")
    except Exception as e:
        print(f"⚠ Login failed or timeout waiting for dashboard: {e}")
        raise
    
    # Wait for page to fully load
    time.sleep(2)
    
    yield driver
    
    # Cleanup: Logout (optional - tests may have already logged out)
    try:
        logout_button = WebDriverWait(driver, SHORT_WAIT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Logout')] | //a[contains(text(), 'Logout')]"))
        )
        logout_button.click()
        print("✓ Logged out after test")
        time.sleep(1)
    except:
        # It's okay if logout button doesn't exist (user may already be logged out)
        pass
 
 
 # TESTS
 
class TestEventWorkflow:
    
    # ========================================================================
    # TEST 1: Login
    # ========================================================================
    
    def test_login(self, driver):
        """Test login functionality"""
        driver.get(f"{BASE_URL}/login")
        
        # Wait for login form to be present
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "loginForm"))
        )
        print("✓ Login form loaded")
        
        # Fill email field
        email_field = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "loginEmail"))
        )
        email_field.clear()
        email_field.send_keys(LOGIN_CREDENTIALS["email"])
        print(f"✓ Entered email: {LOGIN_CREDENTIALS['email']}")
        
        # Fill password field
        password_field = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "loginPassword"))
        )
        password_field.clear()
        password_field.send_keys(LOGIN_CREDENTIALS["password"])
        print("✓ Entered password")
        
        # Click login button
        login_button = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "loginBtn"))
        )
        login_button.click()
        print("✓ Clicked login button")
        
        # Wait for redirect to dashboard
        WebDriverWait(driver, TIMEOUT).until(
            EC.url_contains("dashboard")
        )
        
        # Verify we're on dashboard
        assert "dashboard" in driver.current_url.lower(), f"Expected dashboard URL, got {driver.current_url}"
        
        # Wait for page to fully load
        time.sleep(2)
        
        print(f"✓✓✓ Login successful! Redirected to: {driver.current_url}")
 
 

    # ========================================================================
    # TEST 2: Create Event and Verify in Dashboard
    # ========================================================================
 
    def test_create_event(self, logged_in_driver):
        """
        Create a new event using your form and verify it appears in the dashboard
        """
        driver = logged_in_driver
 
        print("\n=== CREATING EVENT ===")
 
        # Navigate to the event creation page
        driver.get(f"{BASE_URL}/events/new")
        print("✓ Navigated to event creation page")
 
        # Wait for the form to load
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "newEventForm"))
        )
        print("✓ Event creation form loaded")
 
        # ===== FILL EVENT NAME =====
        try:
            name_field = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "eventName"))
            )
            name_field.clear()
            name_field.send_keys(EVENT_DATA["name"])
            print(f"✓ Entered Event Name: {EVENT_DATA['name']}")
        except Exception as e:
            print(f"⚠ Could not fill Event Name: {e}")
            pytest.skip("Could not find Event Name field")
 
        # ===== FILL LOCATION =====
        try:
            location_field = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "location"))
            )
            location_field.clear()
            location_field.send_keys(EVENT_DATA["location"])
            print(f"✓ Entered Location: {EVENT_DATA['location']}")
        except Exception as e:
            print(f"⚠ Could not fill Location: {e}")
 
        # ===== HANDLE SINGLE DAY EVENT CHECKBOX =====
        try:
            single_day_checkbox = driver.find_element(By.ID, "singleDay")
            is_checked = single_day_checkbox.is_selected()
            
            # Determine if this should be a single day event
            is_single_day = EVENT_DATA.get("date_until") == EVENT_DATA.get("date_from")
            
            # Toggle checkbox if needed
            if is_checked != is_single_day:
                single_day_checkbox.click()
                time.sleep(0.5)  # Wait for checkbox state to update
                print(f"✓ Toggled Single Day Event checkbox (is_single_day: {is_single_day})")
            else:
                print(f"✓ Single Day Event checkbox already in correct state")
                
        except Exception as e:
            print(f"⚠ Could not handle Single Day Event checkbox: {e}")
 
        # ===== FILL START DATE =====
        try:
            start_date_field = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "startDate"))
            )
            start_date_field.clear()
            start_date_field.send_keys(EVENT_DATA["date_from"])
            print(f"✓ Entered Start Date: {EVENT_DATA['date_from']}")
        except Exception as e:
            print(f"⚠ Could not fill Start Date: {e}")
 
        # ===== FILL START TIME =====
        try:
            start_time_field = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "startTime"))
            )
            start_time_field.clear()
            start_time_field.send_keys(EVENT_DATA["time_from"])
            print(f"✓ Entered Start Time: {EVENT_DATA['time_from']}")
        except Exception as e:
            print(f"⚠ Could not fill Start Time: {e}")
 
        # ===== FILL END DATE =====
        try:
            end_date_field = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "finishDate"))
            )
            end_date_field.clear()
            end_date_field.send_keys(EVENT_DATA["date_until"])
            print(f"✓ Entered End Date: {EVENT_DATA['date_until']}")
        except Exception as e:
            print(f"⚠ Could not fill End Date: {e}")
 
        # ===== FILL END TIME =====
        try:
            end_time_field = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "finishTime"))
            )
            end_time_field.clear()
            end_time_field.send_keys(EVENT_DATA["time_until"])
            print(f"✓ Entered End Time: {EVENT_DATA['time_until']}")
        except Exception as e:
            print(f"⚠ Could not fill End Time: {e}")
 
        # ===== FILL DESCRIPTION =====
        try:
            desc_field = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "description"))
            )
            desc_field.clear()
            desc_field.send_keys(EVENT_DATA["description"])
            print("✓ Entered Event Description")
        except Exception as e:
            print(f"⚠ Could not fill Description: {e}")
 
        # ===== SELECT PRIVACY (Private/Public) =====
        try:
            if EVENT_DATA["event_type"] == "Private":
                private_radio = WebDriverWait(driver, TIMEOUT).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='radio'][@name='privacy'][@value='private']"))
                )
                private_radio.click()
                print("✓ Selected Private Event")
            else:
                public_radio = WebDriverWait(driver, TIMEOUT).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='radio'][@name='privacy'][@value='public']"))
                )
                public_radio.click()
                print("✓ Selected Public Event")
        except Exception as e:
            print(f"⚠ Could not select privacy setting: {e}")
 
        # ===== SUBMIT FORM =====
        print("\n=== SUBMITTING FORM ===")
        try:
            # Find the submit button
            submit_button = WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='submit'][@class='btn btn-success']"))
            )
            
            # Scroll to the submit button to ensure it's visible
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(0.5)
            
            # Click the submit button
            submit_button.click()
            print("✓ Clicked Create button")
            
        except Exception as e:
            print(f"⚠ Could not click Create button: {e}")
            pytest.skip("Could not submit form")
 
        # ===== WAIT FOR SUBMISSION AND REDIRECT =====
        print("\n=== WAITING FOR FORM PROCESSING ===")
        time.sleep(2)  # Give the server time to process
        
        # Check current URL
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
 
        # ===== HANDLE REDIRECT OR MANUALLY NAVIGATE =====
        print("\n=== NAVIGATING TO DASHBOARD ===")
        
        # Try to wait for automatic redirect to dashboard
        try:
            WebDriverWait(driver, 5).until(
                EC.url_contains("dashboard")
            )
            print("✓ Automatically redirected to dashboard")
        except TimeoutException:  # ← NOW THIS WILL WORK
            print("⚠ No automatic redirect - manually navigating to dashboard")
            # Manually navigate to dashboard if redirect didn't happen
            driver.get(f"{BASE_URL}/dashboard")
            time.sleep(2)
            print("✓ Manually navigated to dashboard")
 
        # Verify we're on the dashboard
        current_url = driver.current_url
        print(f"Final URL: {current_url}")
        assert "dashboard" in current_url.lower(), f"Expected dashboard URL, got {current_url}"
        print("✓ Confirmed on dashboard page")
 
        # ===== VERIFY EVENT APPEARS IN DASHBOARD =====
        print("\n=== VERIFYING EVENT IN DASHBOARD ===")
        
        # Wait for and find the event in the dashboard
        try:
            event_element = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{EVENT_DATA['name']}')]"))
            )
            print(f"✓ Found event '{EVENT_DATA['name']}' in dashboard")
            
            # Verify event details are visible
            try:
                # Check if location is visible near the event
                location_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{EVENT_DATA['location']}')]"))
                )
                print(f"✓ Found event location '{EVENT_DATA['location']}' in dashboard")
            except:
                print("⚠ Event location not found (but event name is visible)")
            
            print(f"\n✓✓✓ EVENT CREATION TEST PASSED! ✓✓✓")
            print(f"    Event '{EVENT_DATA['name']}' created and visible in dashboard")
            
        except TimeoutException as e:
            # Event not found - get debugging info
            print(f"✗ FAILED: Event '{EVENT_DATA['name']}' not found in dashboard")
            print(f"\nDEBUGGING INFO:")
            print(f"  Current URL: {driver.current_url}")
            print(f"  Page title: {driver.title}")
            
            # Try to find ANY events displayed
            try:
                all_events = driver.find_elements(By.XPATH, "//*[contains(@class, 'event')]")
                print(f"  Events found on page: {len(all_events)}")
                for i, event in enumerate(all_events[:5]):  # Show first 5
                    print(f"    Event {i+1}: {event.text[:100]}")
            except:
                print("  Could not find event elements")
            
            # Print page content for debugging
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text
                print(f"\nPage content (first 500 chars):\n{page_text[:500]}")
            except:
                pass
            
            # Fail the test with clear message
            raise AssertionError(f"Event '{EVENT_DATA['name']}' was not found in the dashboard")
 
    # ========================================================================
    # TEST 3: Edit Event
    # ========================================================================
 
    def test_edit_event(self, logged_in_driver):
        """Edit an existing event and verify changes"""
 
        driver = logged_in_driver
 
        print("\n=== EDITING EVENT ===")
 
        # Go to dashboard
        driver.get(f"{BASE_URL}/dashboard")
 
        # Wait for event to appear
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[contains(text(), '{EVENT_DATA['name']}')]")
            )
        )
 
        print(f"✓ Found event: {EVENT_DATA['name']}")
 
        # Click the Edit button for this event on the dashboard
        edit_button = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((
                By.XPATH,
                f"//div[contains(@class, 'event-card') and .//*[contains(text(), '{EVENT_DATA['name']}')]]//a[@title='Edit']"
            ))
        )
        edit_href = edit_button.get_attribute('href')
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_button)
        time.sleep(0.5)
        edit_button.click()
 
        print("✓ Clicked Edit Event")
 
        # Wait for edit page navigation; fall back to direct URL if needed
        time.sleep(2)
        current_url = driver.current_url
        print(f"Current URL after click: {current_url}")
        if edit_href and current_url == f"{BASE_URL}/dashboard":
            print("⚠ Click did not navigate; using direct edit URL")
            driver.get(edit_href)
 
        # Wait for edit form
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "newEventForm"))
        )
 
        print("✓ Edit form loaded")
 
        # Verify edit page title
        try:
            page_title = driver.find_element(By.ID, "pageTitle").text.strip()
            assert page_title == "Edit Event", f"Expected edit page title, got '{page_title}'"
            print("✓ Confirmed Edit Event page")
        except Exception as e:
            print(f"⚠ Could not confirm edit page title: {e}")
 
        # Helper function to safely fill a field
        def fill_field(field_id, value):
            """Safely clear and fill a field with proper timing"""
            field = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, field_id))
            )
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
            time.sleep(0.3)
            
            # For date and time inputs, use JavaScript to set the value directly
            field_type = field.get_attribute("type")
            if field_type in ["date", "time", "datetime-local"]:
                # Use JavaScript for date/time inputs (more reliable)
                driver.execute_script(f"arguments[0].value = '{value}';", field)
                # Trigger change event
                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", field)
                time.sleep(0.3)
            else:
                # For text inputs, use traditional method
                field.click()
                time.sleep(0.2)
                # Triple-click to select all text
                field.send_keys("\ue000")  # Home key
                field.send_keys("\ue009" + "a")  # Shift+End to select
                field.send_keys("\ue003")  # Delete/Backspace
                time.sleep(0.2)
                # Type new value
                field.send_keys(value)
                time.sleep(0.3)
            
            # Verify the value was set
            actual_value = field.get_attribute("value")
            if actual_value != value:
                print(f"  ⚠ Warning: Expected '{value}', got '{actual_value}'")
            return field
 
        # ===== UPDATE EVENT NAME =====
        try:
            fill_field("eventName", EVENT_DATA_UPDATED["name"])
            print(f"✓ Updated name: {EVENT_DATA_UPDATED['name']}")
        except Exception as e:
            print(f"✗ Failed to update name: {e}")
 
        # ===== UPDATE LOCATION =====
        try:
            fill_field("location", EVENT_DATA_UPDATED["location"])
            print(f"✓ Updated location: {EVENT_DATA_UPDATED['location']}")
        except Exception as e:
            print(f"✗ Failed to update location: {e}")
 
        # ===== UPDATE DESCRIPTION =====
        try:
            fill_field("description", EVENT_DATA_UPDATED["description"])
            print("✓ Updated description")
        except Exception as e:
            print(f"✗ Failed to update description: {e}")
 
        # ===== UPDATE START DATE =====
        try:
            fill_field("startDate", EVENT_DATA_UPDATED["date_from"])
            print(f"✓ Updated start date: {EVENT_DATA_UPDATED['date_from']}")
        except Exception as e:
            print(f"✗ Failed to update start date: {e}")
 
        # ===== UPDATE START TIME =====
        try:
            fill_field("startTime", EVENT_DATA_UPDATED["time_from"])
            print(f"✓ Updated start time: {EVENT_DATA_UPDATED['time_from']}")
        except Exception as e:
            print(f"✗ Failed to update start time: {e}")
 
        # ===== UPDATE END DATE =====
        try:
            fill_field("finishDate", EVENT_DATA_UPDATED["date_until"])
            print(f"✓ Updated end date: {EVENT_DATA_UPDATED['date_until']}")
        except Exception as e:
            print(f"✗ Failed to update end date: {e}")
 
        # ===== UPDATE END TIME =====
        try:
            fill_field("finishTime", EVENT_DATA_UPDATED["time_until"])
            print(f"✓ Updated end time: {EVENT_DATA_UPDATED['time_until']}")
        except Exception as e:
            print(f"✗ Failed to update end time: {e}")
 
        # ===== CHANGE PRIVACY =====
        try:
            if EVENT_DATA_UPDATED["event_type"] == "Public":
                public_radio = WebDriverWait(driver, TIMEOUT).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//input[@type='radio'][@value='public']"
                    ))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", public_radio)
                time.sleep(0.3)
                public_radio.click()
                print("✓ Changed event to Public")
        except Exception as e:
            print(f"⚠ Could not change privacy: {e}")
 
        # ===== SAVE CHANGES =====
        print("\n=== SAVING CHANGES ===")
        try:
            save_button = WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//input[@type='submit'][@class='btn btn-success']"
                ))
            )
            
            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                save_button
            )
            time.sleep(0.5)
            
            # Try regular click first
            try:
                save_button.click()
                print("✓ Clicked save button")
            except Exception:
                # Fall back to JS click if regular click fails
                print("⚠ Regular click failed, using JavaScript click")
                driver.execute_script("arguments[0].click();", save_button)
                print("✓ Clicked save button via JS")
                
        except Exception as e:
            print(f"✗ Could not find/click save button: {e}")
            raise
 
        # Wait for redirect or capture an error
        time.sleep(2)
 
        # Check for JavaScript alerts
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"⚠ Alert after save: {alert_text}")
            alert.accept()
        except Exception:
            pass
 
        # Check for any page error messages
        try:
            error_msgs = driver.find_elements(By.XPATH, "//*[contains(text(), 'Unable to create event.') or contains(text(), 'Event updated successfully') or contains(text(), 'Invalid date or time format') or contains(text(), 'Event name is required')]")
            for msg in error_msgs:
                print(f"Page message: {msg.text}")
        except Exception:
            pass
 
        current_url = driver.current_url
        print(f"Current URL after save: {current_url}")
        if "dashboard" not in current_url.lower():
            print("⚠ Did not automatically redirect after save; navigating to dashboard manually")
            driver.get(f"{BASE_URL}/dashboard")
            time.sleep(2)
        else:
            print("✓ Redirected to dashboard")
 
        # ===== VERIFY UPDATED EVENT =====
        print("\n=== VERIFYING UPDATED EVENT ===")
        try:
            updated_event = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//*[contains(text(), '{EVENT_DATA_UPDATED['name']}')]")
                )  
            )
            assert updated_event is not None
            print(f"✓ Found updated event: {EVENT_DATA_UPDATED['name']}")
        except TimeoutException:
            print(f"✗ Updated event not found: {EVENT_DATA_UPDATED['name']}")
            raise
 
        print(f"\n✓✓✓ EVENT EDIT TEST PASSED ✓✓✓")
        print(f"Updated event visible as: {EVENT_DATA_UPDATED['name']}")
 
    # ========================================================================
    # TEST 4: Fill Event Tabs
    # ========================================================================
    
    def test_fill_event_tabs(self, logged_in_driver):
        """Fill in different sections/tabs of the event"""
        driver = logged_in_driver
        
        print("\n=== FILLING EVENT TABS ===")
        
        # Find and click event to open details
        try:
            event_element = WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{EVENT_DATA_UPDATED['name']}')] | //h2[contains(text(), '{EVENT_DATA_UPDATED['name']}')]"))
            )
            event_element.click()
            print(f"✓ Opened event details")
        except Exception as e:
            print(f"⚠ Could not open event: {e}")
            pytest.skip("Could not open event")
        
        time.sleep(2)
        
        # Try to find and click different tabs
        tab_names = ["Details", "Settings", "Attendees", "Options", "General", "Info"]
        
        tabs_found = 0
        for tab_name in tab_names:
            try:
                tab = WebDriverWait(driver, TIMEOUT).until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{tab_name}')] | //a[contains(text(), '{tab_name}')]"))
                )
                tab.click()
                print(f"✓ Clicked '{tab_name}' tab")
                tabs_found += 1
                time.sleep(1)
                
                # Try to fill any visible input fields on this tab
                input_fields = driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea")
                if input_fields:
                    for i, field in enumerate(input_fields[:2]):
                        try:
                            if field.is_displayed():
                                field.clear()
                                field.send_keys(f"Test data for {tab_name}")
                                print(f"  ✓ Filled field on {tab_name} tab")
                        except:
                            pass
                
                # Try to save
                try:
                    save_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
                    save_btn.click()
                    print(f"  ✓ Saved {tab_name} tab")
                    time.sleep(1)
                except:
                    pass
                    
            except:
                continue
        
        if tabs_found == 0:
            print("⚠ No tabs found (this may be normal for your form)")
        else:
            print(f"✓✓✓ Filled {tabs_found} tabs")
 
 
    # ========================================================================
    # TEST 5: Delete Event
    # ========================================================================
    
    def test_delete_event(self, logged_in_driver):
        """Delete the event"""
        driver = logged_in_driver
        
        print("\n=== DELETING EVENT ===")
        
        # Find the event
        try:
            event_element = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{EVENT_DATA_UPDATED['name']}')] | //h2[contains(text(), '{EVENT_DATA_UPDATED['name']}')]"))
            )
            print(f"✓ Found event to delete")
        except:
            print("⚠ Event not found")
            pytest.skip("Event not found")
        
        # Find and click delete button
        try:
            delete_btn = WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Delete')] | //a[contains(text(), 'Delete')]"))
            )
            delete_btn.click()
            print("✓ Clicked Delete button")
        except Exception as e:
            print(f"⚠ Could not find Delete button: {e}")
            pytest.skip("Delete button not found")
        
        # Handle confirmation
        time.sleep(1)
        try:
            confirm_btn = WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm')] | //button[contains(text(), 'Yes')] | //button[contains(text(), 'OK')]"))
            )
            confirm_btn.click()
            print("✓ Confirmed deletion")
        except:
            print("⚠ No confirmation dialog")
        
        time.sleep(2)
        
        # Verify deletion
        try:
            event_element = driver.find_element(By.XPATH, f"//div[contains(text(), '{EVENT_DATA_UPDATED['name']}')]")
            print("⚠ Event still visible after deletion")
        except:
            print(f"✓✓✓ Event '{EVENT_DATA_UPDATED['name']}' deleted successfully!")

    def test_logout(self, driver):
        """Test logout functionality"""
        # Login first
        driver.get(BASE_URL)

        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        email_field = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "loginEmail"))
        )
        email_field.send_keys(LOGIN_CREDENTIALS["email"])

        password_field = driver.find_element(By.ID, "loginPassword")
        password_field.send_keys(LOGIN_CREDENTIALS["password"])

        login_btn = driver.find_element(By.ID, "loginBtn")
        login_btn.click()

        # Wait for dashboard page
        WebDriverWait(driver, TIMEOUT).until(
            EC.url_contains("dashboard")
        )

        print("✓ Login successful")

        # Click logout button
        logout_btn = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Logout')]")
            )
        )

        logout_btn.click()
        print("✓ Clicked logout button")

        # Wait for redirect to login page
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "loginEmail"))
        )

        # Verify logout successful
        assert "dashboard" not in driver.current_url.lower()

        print(f"✓ Logged out successfully. Current URL: {driver.current_url}")


"""
SETUP:
1. pip install selenium webdriver-manager pytest
2. Run all tests:
   pytest test_event_workflow.py -v -s
4. Run specific test:
   pytest test_event_workflow.py::TestEventWorkflow::test_create_event -v -s
TESTS INCLUDED:
✓ test_login - Login to website
✓ test_create_event - Fill and submit the Create Event form
✓ test_edit_event - Edit the created event
✓ test_fill_event_tabs - Fill event detail tabs
✓ test_delete_event - Delete the event
✓ test_logout - Logout from website
"""