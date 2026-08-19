# Cucumber for Python (Behave)

Guide for implementing BDD in Python using Behave (the Python Cucumber implementation).

---

## Prerequisites

- Python 3.8+
- pip or poetry
- pytest (optional, for integration)

---

## Installation

```bash
# pip
pip install behave

# With browser testing
pip install behave selenium playwright

# With API testing
pip install behave requests

# All common dependencies
pip install behave selenium requests pytest-bdd
```

---

## Project Structure

```
project/
├── features/
│   ├── auth/
│   │   └── login.feature
│   ├── checkout/
│   │   └── cart.feature
│   ├── steps/
│   │   ├── auth_steps.py
│   │   ├── common_steps.py
│   │   └── api_steps.py
│   └── environment.py          # Hooks and setup
├── reports/
├── behave.ini                  # Configuration
└── requirements.txt
```

---

## Configuration (behave.ini)

```ini
# behave.ini
[behave]
paths = features
format = progress
show_skipped = false
show_timings = true
junit = true
junit_directory = reports

[behave.userdata]
browser = chrome
headless = true
base_url = http://localhost:3000

# Tag filtering
[behave.tags]
wip = false
skip = false
```

---

## Environment Setup

```python
# features/environment.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

def before_all(context):
    """Run once before all scenarios."""
    context.base_url = context.config.userdata.get('base_url', 'http://localhost:3000')
    context.headless = context.config.userdata.get('headless', 'true') == 'true'

def before_scenario(context, scenario):
    """Run before each scenario."""
    # Setup browser
    options = Options()
    if context.headless:
        options.add_argument('--headless')
    context.browser = webdriver.Chrome(options=options)
    context.browser.implicitly_wait(10)

def after_scenario(context, scenario):
    """Run after each scenario."""
    # Screenshot on failure
    if scenario.status == 'failed':
        screenshot_path = f"reports/failure-{scenario.name}.png"
        context.browser.save_screenshot(screenshot_path)

    # Cleanup browser
    if hasattr(context, 'browser'):
        context.browser.quit()

def before_tag(context, tag):
    """Run before scenarios with specific tags."""
    if tag == 'auth':
        context.auth_token = authenticate_test_user()
    elif tag == 'database':
        context.db_transaction = start_transaction()

def after_tag(context, tag):
    """Run after scenarios with specific tags."""
    if tag == 'database' and hasattr(context, 'db_transaction'):
        context.db_transaction.rollback()
```

---

## Step Definitions

```python
# features/steps/auth_steps.py
from behave import given, when, then
from selenium.webdriver.common.by import By

@given('I am on the login page')
def step_on_login_page(context):
    context.browser.get(f"{context.base_url}/login")

@given('I have a registered account with email "{email}"')
def step_registered_account(context, email):
    # Create test user in database
    context.test_user = create_test_user(email=email)

@when('I enter email "{email}"')
def step_enter_email(context, email):
    email_field = context.browser.find_element(By.NAME, 'email')
    email_field.clear()
    email_field.send_keys(email)

@when('I enter password "{password}"')
def step_enter_password(context, password):
    password_field = context.browser.find_element(By.NAME, 'password')
    password_field.clear()
    password_field.send_keys(password)

@when('I click the login button')
def step_click_login(context):
    login_button = context.browser.find_element(By.ID, 'login-button')
    login_button.click()

@then('I should be redirected to the dashboard')
def step_redirected_to_dashboard(context):
    assert '/dashboard' in context.browser.current_url

@then('I should see "{text}"')
def step_should_see_text(context, text):
    body = context.browser.find_element(By.TAG_NAME, 'body')
    assert text in body.text

@then('I should see error message "{message}"')
def step_should_see_error(context, message):
    error_element = context.browser.find_element(By.CLASS_NAME, 'error-message')
    assert error_element.text == message
```

---

## API Step Definitions

```python
# features/steps/api_steps.py
from behave import given, when, then
import requests
import json

@given('I am authenticated')
def step_authenticated(context):
    response = requests.post(
        f"{context.base_url}/api/auth/login",
        json={'email': 'test@example.com', 'password': 'password'}
    )
    context.auth_token = response.json()['token']

@when('I send a GET request to "{endpoint}"')
def step_get_request(context, endpoint):
    headers = {}
    if hasattr(context, 'auth_token'):
        headers['Authorization'] = f"Bearer {context.auth_token}"

    context.response = requests.get(
        f"{context.base_url}{endpoint}",
        headers=headers
    )

@when('I send a POST request to "{endpoint}" with')
def step_post_request(context, endpoint):
    headers = {'Content-Type': 'application/json'}
    if hasattr(context, 'auth_token'):
        headers['Authorization'] = f"Bearer {context.auth_token}"

    context.response = requests.post(
        f"{context.base_url}{endpoint}",
        headers=headers,
        json=json.loads(context.text)
    )

@then('the response status should be {status:d}')
def step_response_status(context, status):
    assert context.response.status_code == status

@then('the response should contain')
def step_response_contains(context):
    expected = json.loads(context.text)
    actual = context.response.json()
    for key, value in expected.items():
        assert actual.get(key) == value
```

---

## Data Tables

```python
# features/steps/data_steps.py
from behave import given

@given('the following users exist')
def step_users_exist(context):
    for row in context.table:
        create_user(
            email=row['email'],
            role=row['role'],
            active=row['active'] == 'true'
        )

# Usage in feature file:
# Given the following users exist
#   | email              | role    | active |
#   | alice@example.com  | admin   | true   |
#   | bob@example.com    | user    | false  |
```

---

## Alternative: pytest-bdd

```python
# If you prefer pytest, use pytest-bdd
# pip install pytest-bdd

# tests/step_defs/test_login.py
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

scenarios('../features/auth/login.feature')

@given('I am on the login page')
def login_page(browser):
    browser.get('/login')

@when(parsers.parse('I enter email "{email}"'))
def enter_email(browser, email):
    browser.find_element_by_name('email').send_keys(email)

@then(parsers.parse('I should see "{text}"'))
def should_see_text(browser, text):
    assert text in browser.page_source
```

---

## Running Tests

```bash
# Run all features
behave

# Run specific feature
behave features/auth/login.feature

# Run with tags
behave --tags=@smoke
behave --tags="@critical and @auth"
behave --tags="not @wip"

# Dry run
behave --dry-run

# Generate JUnit report
behave --junit --junit-directory=reports

# Run with specific format
behave --format=pretty
behave --format=progress

# With browser visible (not headless)
behave -D headless=false
```

---

## Resources

- [Behave Documentation](https://behave.readthedocs.io/)
- [Behave GitHub](https://github.com/behave/behave)
- [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/)
- [Selenium Python](https://selenium-python.readthedocs.io/)
