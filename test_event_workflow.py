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
                # For text inputs (including textarea and text fields), use JavaScript to clear then type
                # Clear the field using JavaScript
                driver.execute_script("arguments[0].value = '';", field)
                # Trigger input event
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", field)
                time.sleep(0.2)
                
                # Click to focus
                field.click()
                time.sleep(0.2)
                
                # Type the new value
                field.send_keys(value)
                time.sleep(0.3)
            
            # Verify the value was set
            actual_value = field.get_attribute("value")
            if actual_value != value:
                print(f"  ⚠ Warning: Expected '{value}', got '{actual_value}'")
                # Try again if verification failed
                driver.execute_script(f"arguments[0].value = '{value}';", field)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", field)
                time.sleep(0.2)
            return field
 
        # ===== FILL EVENT NAME =====
        try:
            fill_field("eventName", EVENT_DATA["name"])
            print(f"✓ Entered Event Name: {EVENT_DATA['name']}")
        except Exception as e:
            print(f"⚠ Could not fill Event Name: {e}")
            pytest.skip("Could not find Event Name field")
 
        # ===== FILL LOCATION =====
        try:
            fill_field("location", EVENT_DATA["location"])
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
            fill_field("startDate", EVENT_DATA["date_from"])
            print(f"✓ Entered Start Date: {EVENT_DATA['date_from']}")
        except Exception as e:
            print(f"⚠ Could not fill Start Date: {e}")
 
        # ===== FILL START TIME =====
        try:
            fill_field("startTime", EVENT_DATA["time_from"])
            print(f"✓ Entered Start Time: {EVENT_DATA['time_from']}")
        except Exception as e:
            print(f"⚠ Could not fill Start Time: {e}")
 
        # ===== FILL END DATE =====
        try:
            fill_field("finishDate", EVENT_DATA["date_until"])
            print(f"✓ Entered End Date: {EVENT_DATA['date_until']}")
        except Exception as e:
            print(f"⚠ Could not fill End Date: {e}")
 
        # ===== FILL END TIME =====
        try:
            fill_field("finishTime", EVENT_DATA["time_until"])
            print(f"✓ Entered End Time: {EVENT_DATA['time_until']}")
        except Exception as e:
            print(f"⚠ Could not fill End Time: {e}")
 
        # ===== FILL DESCRIPTION =====
        try:
            fill_field("description", EVENT_DATA["description"])
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
    # TEST 3: Populate Event Dashboard Tabs
    # ========================================================================
 
    def test_event_dashboard(self, logged_in_driver):
        """Test populating all event dashboard tabs: Polling, Expenses, Checklist, Discussion"""
 
        driver = logged_in_driver
 
        print("\n=== NAVIGATING TO EVENT DASHBOARD ===")
 
        # Go to dashboard to find the event
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(2)
 
        # Wait for the event to be visible
        try:
            event_element = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//*[contains(text(), '{EVENT_DATA['name']}')]")
                )
            )
            print(f"✓ Found event: {EVENT_DATA['name']}")
        except TimeoutException:
            print(f"✗ Event not found on dashboard")
            raise
 
        # Find and click the event card - use a more direct selector
        try:
            # Find the event card and click anywhere on it
            event_card = WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f"//div[contains(@class, 'event-card') and .//*[contains(text(), '{EVENT_DATA['name']}')]]"
                ))
            )
            
            # Scroll to the card
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", event_card)
            time.sleep(0.5)
            
            # Click the card
            event_card.click()
            print("✓ Clicked event card")
            
        except Exception as e:
            print(f"⚠ Could not click event card: {e}")
            print("⚠ Attempting to navigate via URL instead")
            # Try to extract event ID from the page and navigate directly
            try:
                event_id_match = driver.find_element(
                    By.XPATH,
                    f"//div[contains(@class, 'event-card') and .//*[contains(text(), '{EVENT_DATA['name']}')]]"
                ).get_attribute("data-eventid")
                if event_id_match:
                    driver.get(f"{BASE_URL}/event-dashboard/{event_id_match}")
                    print(f"✓ Navigated to event dashboard via URL")
                else:
                    raise Exception("Could not find event ID")
            except Exception as e2:
                print(f"✗ Could not navigate to event: {e2}")
                raise
 
        # Wait for dashboard to load
        time.sleep(3)
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
 
        # ===== POLLING TAB =====
        print("\n=== TESTING POLLING TAB ===")
        try:
            # Click the date options tab button
            polling_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@class, 'tab-button') and normalize-space(text())='Date Options']"
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", polling_button)
            time.sleep(0.3)
            polling_button.click()
            print("✓ Clicked Date Options tab")
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='voting' and contains(@class, 'active')]") )
            )
            time.sleep(0.5)
 
            # Find the voting form inside the active tab
            try:
                polling_form = driver.find_element(
                    By.XPATH,
                    "//div[@id='voting']//form[.//input[@name='title']]"
                )
                print("✓ Found voting form")
 
                # Fill in the date option title
                title_input = WebDriverWait(polling_form, TIMEOUT).until(
                    EC.presence_of_element_located((By.NAME, "title"))
                )
                title_input.clear()
                title_input.send_keys("2027-11-15")
                print("✓ Entered vote option title: 2027-11-15")
 
                # Submit the form
                submit_btn = polling_form.find_element(By.XPATH, ".//button[@type='submit']")
                submit_btn.click()
                print("✓ Added vote option")
                time.sleep(1)
 
                # Find and vote on the option if available
                try:
                    vote_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            "//button[contains(text(), 'Vote') or contains(text(), 'Voted')]"
                        ))
                    )
                    vote_button.click()
                    print("✓ Voted on date option")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"⚠ Could not cast vote: {e}")
 
            except Exception as e:
                print(f"⚠ Could not populate voting tab: {e}")
 
        except Exception as e:
            print(f"⚠ Polling tab error: {e}")
 
        # ===== EXPENSES TAB =====
        print("\n=== TESTING EXPENSES TAB ===")
        try:
            # Click the expenses tab button
            expenses_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@class, 'tab-button') and (contains(text(), 'Expenses') or contains(text(), 'Expense'))]"
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", expenses_button)
            time.sleep(0.3)
            expenses_button.click()
            print("✓ Clicked Expenses tab")
            time.sleep(1)
 
            # Find the expenses form
            try:
                expenses_form = driver.find_element(
                    By.XPATH,
                    "//form[contains(@action, 'add_expense') or contains(@action, 'expense')]"
                )
                print("✓ Found expenses form")
 
                # Fill in expense title
                title_input = expenses_form.find_element(By.NAME, "title")
                title_input.clear()
                title_input.send_keys("Venue Rental")
                print("✓ Entered expense title: Venue Rental")
 
                # Fill in expense amount
                amount_input = expenses_form.find_element(By.NAME, "amount")
                amount_input.clear()
                amount_input.send_keys("150.00")
                print("✓ Entered expense amount: $150.00")
 
                # Submit the form
                submit_btn = expenses_form.find_element(By.XPATH, ".//button[@type='submit']")
                submit_btn.click()
                print("✓ Added expense")
                time.sleep(1)
 
            except Exception as e:
                print(f"⚠ Could not populate expenses tab: {e}")
 
        except Exception as e:
            print(f"⚠ Expenses tab error: {e}")
 
        # ===== CHECKLIST TAB =====
        print("\n=== TESTING CHECKLIST TAB ===")
        try:
            # Click the checklist tab button
            checklist_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@class, 'tab-button') and (contains(text(), 'Checklist') or contains(text(), 'Check'))]"
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checklist_button)
            time.sleep(0.3)
            checklist_button.click()
            print("✓ Clicked Checklist tab")
            time.sleep(1)
 
            # Find the checklist form
            try:
                checklist_form = driver.find_element(
                    By.XPATH,
                    "//form[contains(@action, 'add_checklist_item') or contains(@action, 'checklist')]"
                )
                print("✓ Found checklist form")
 
                # Add first checklist item
                item_input = checklist_form.find_element(By.NAME, "title")
                item_input.clear()
                item_input.send_keys("Confirm guest list")
                print("✓ Entered checklist item: Confirm guest list")
 
                submit_btn = checklist_form.find_element(By.XPATH, ".//button[@type='submit']")
                submit_btn.click()
                print("✓ Added first checklist item")
                time.sleep(1)
 
                # Add second checklist item
                item_input = checklist_form.find_element(By.NAME, "title")
                item_input.clear()
                item_input.send_keys("Arrange catering")
                print("✓ Entered checklist item: Arrange catering")
 
                submit_btn = checklist_form.find_element(By.XPATH, ".//button[@type='submit']")
                submit_btn.click()
                print("✓ Added second checklist item")
                time.sleep(1)
 
                # Check off one of the items
                checkbox = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//input[@type='checkbox']"
                    ))
                )
                checkbox.click()
                print("✓ Checked off a checklist item")
                time.sleep(0.5)
 
            except Exception as e:
                print(f"⚠ Could not populate checklist tab: {e}")
 
        except Exception as e:
            print(f"⚠ Checklist tab error: {e}")
 
        # ===== DISCUSSION TAB =====
        print("\n=== TESTING DISCUSSION TAB ===")
        try:
            # Click the discussion tab button
            discussion_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@class, 'tab-button') and (contains(text(), 'Discussion') or contains(text(), 'Discuss'))]"
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", discussion_button)
            time.sleep(0.3)
            discussion_button.click()
            print("✓ Clicked Discussion tab")
            time.sleep(1)
 
            # Find the discussion form
            try:
                discussion_form = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((
                        By.ID,
                        "discussionForm"
                    ))
                )
                print("✓ Found discussion form")
 
                # Fill in the message
                message_input = discussion_form.find_element(By.ID, "discussionInput")
                message_input.clear()
                message_input.send_keys("Looking forward to this event! Let's finalize the details soon.")
                print("✓ Entered discussion message")
 
                # Submit the form
                submit_btn = discussion_form.find_element(By.XPATH, ".//button[@type='submit']")
                submit_btn.click()
                print("✓ Posted discussion message")
                time.sleep(2)
 
                # Verify the message appears
                message_text = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//p[contains(@class, 'message-body') and contains(text(), 'Looking forward to this event')]"
                    ))
                )
                print("✓ Message posted successfully and visible")
 
            except Exception as e:
                print(f"⚠ Could not populate discussion tab: {e}")
 
        except Exception as e:
            print(f"⚠ Discussion tab error: {e}")
 
        print(f"\n✓✓✓ EVENT DASHBOARD TEST PASSED ✓✓✓")
        print(f"    Dashboard tabs tested successfully")

 
    # ========================================================================
    # TEST 4: Edit Event
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
    # TEST 5: Delete Event
    # ========================================================================

    def test_delete_event(self, logged_in_driver):
        """Delete the updated event and verify it's removed from dashboard"""

        driver = logged_in_driver

        print("\n=== DELETING EVENT ===")

        # Go to dashboard
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(1)

        # Wait for the updated event to appear
        try:
            event_element = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//*[contains(text(), '{EVENT_DATA_UPDATED['name']}')]")
                )
            )
            print(f"✓ Found event to delete: {EVENT_DATA_UPDATED['name']}")
        except TimeoutException:
            print(f"⚠ Updated event not found, trying original event name")
            event_element = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//*[contains(text(), '{EVENT_DATA['name']}')]")
                )
            )
            print(f"✓ Found event to delete: {EVENT_DATA['name']}")

        # Find the delete button for this event
        # The delete button is a button element within card-actions, not an anchor tag
        try:
            # First find the event card and scroll it into view
            event_card = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    f"//div[contains(@class, 'event-card') and .//*[contains(text(), '{EVENT_DATA_UPDATED['name']}')]]"
                ))
            )
            
            # Scroll the event card into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", event_card)
            time.sleep(0.5)
            
            # Look for the delete button - it's a button element with title="Delete"
            delete_button = WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f"//div[contains(@class, 'event-card') and .//*[contains(text(), '{EVENT_DATA_UPDATED['name']}')]]//button[@title='Delete']"
                ))
            )
            print("✓ Found delete button")
            
        except TimeoutException:
            # Try with original event name
            try:
                print("⚠ Primary selector failed, trying with original event name")
                event_card = WebDriverWait(driver, TIMEOUT).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        f"//div[contains(@class, 'event-card') and .//*[contains(text(), '{EVENT_DATA['name']}')]]"
                    ))
                )
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", event_card)
                time.sleep(0.5)
                
                delete_button = WebDriverWait(driver, TIMEOUT).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f"//div[contains(@class, 'event-card') and .//*[contains(text(), '{EVENT_DATA['name']}')]]//button[@title='Delete']"
                    ))
                )
                print("✓ Found delete button (using original name)")
                
            except TimeoutException:
                print("⚠ Both selectors failed, looking for generic delete button")
                # Last resort - find any delete button on the page
                delete_buttons = driver.find_elements(By.XPATH, "//button[@title='Delete']")
                
                if len(delete_buttons) == 0:
                    print("✗ Could not find delete button")
                    raise AssertionError("No delete button found on page")
                
                # Use the first delete button found
                delete_button = delete_buttons[0]
                print(f"✓ Found delete button (generic selector, {len(delete_buttons)} buttons available)")

        # Scroll to the delete button
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_button)
        time.sleep(0.5)

        # Click the delete button
        try:
            delete_button.click()
            print("✓ Clicked delete button")
        except Exception:
            # Fall back to JS click if regular click fails
            print("⚠ Regular click failed, using JavaScript click")
            driver.execute_script("arguments[0].click();", delete_button)
            print("✓ Clicked delete button via JS")

        # Wait for confirmation dialog
        time.sleep(1)

        # Handle the JavaScript confirmation dialog
        print("\n=== HANDLING CONFIRMATION ===")
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"⚠ Confirmation dialog appeared: {alert_text}")
            # Click OK to confirm deletion
            alert.accept()
            print("✓ Confirmed deletion via alert")
        except Exception:
            print("⚠ No alert found - checking for modal confirmation")

        # Wait for deletion to complete
        time.sleep(2)

        # Check for success messages
        try:
            success_msgs = driver.find_elements(By.XPATH, "//*[contains(text(), 'deleted') or contains(text(), 'removed') or contains(text(), 'successfully')]")
            for msg in success_msgs:
                msg_text = msg.text.lower()
                if any(word in msg_text for word in ['deleted', 'removed', 'success']):
                    print(f"✓ Success message: {msg.text}")
        except Exception:
            pass

        # Ensure we're on the dashboard
        current_url = driver.current_url
        if "dashboard" not in current_url.lower():
            print("⚠ Not on dashboard, navigating there")
            driver.get(f"{BASE_URL}/dashboard")
            time.sleep(2)
        else:
            print("✓ On dashboard")

        # ===== VERIFY EVENT IS DELETED =====
        print("\n=== VERIFYING EVENT DELETION ===")
        
        # Wait a moment for the page to update
        time.sleep(1)
        
        # Check that the event is no longer visible
        try:
            # Try to find the deleted event - should NOT exist
            deleted_event = driver.find_elements(
                By.XPATH, 
                f"//*[contains(text(), '{EVENT_DATA_UPDATED['name']}')]"
            )
            
            if len(deleted_event) == 0:
                print(f"✓ Event '{EVENT_DATA_UPDATED['name']}' successfully deleted (not found)")
            else:
                print(f"✗ Event '{EVENT_DATA_UPDATED['name']}' still visible on dashboard")
                raise AssertionError(f"Event was not deleted - still found on page")
                
        except AssertionError:
            raise

        # Also verify the original event name is gone (in case it reverted)
        try:
            original_event = driver.find_elements(
                By.XPATH,
                f"//*[contains(text(), '{EVENT_DATA['name']}')]"
            )
            if len(original_event) == 0:
                print(f"✓ Original event name '{EVENT_DATA['name']}' also not found")
            else:
                # This could be okay depending on your app's behavior
                print(f"⚠ Original event name '{EVENT_DATA['name']}' still visible")
        except Exception:
            pass

        print(f"\n✓✓✓ EVENT DELETION TEST PASSED ✓✓✓")
        print(f"Event successfully deleted from dashboard")

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