# Cucumber for Ruby

Guide for implementing Cucumber BDD in Ruby projects.

---

## Prerequisites

- Ruby 3.0+ (recommended)
- Bundler
- RSpec (optional, for matchers)

---

## Installation

```ruby
# Gemfile
group :test do
  gem 'cucumber', '~> 9.1'
  gem 'rspec-expectations', '~> 3.12'  # For expect syntax
  gem 'capybara', '~> 3.39'            # For browser testing
  gem 'selenium-webdriver', '~> 4.16'  # WebDriver
end
```

```bash
bundle install
cucumber --init  # Creates directory structure
```

---

## Project Structure

```
project/
├── features/
│   ├── auth/
│   │   └── login.feature
│   ├── step_definitions/
│   │   ├── auth_steps.rb
│   │   └── common_steps.rb
│   └── support/
│       ├── env.rb                # Environment setup
│       ├── hooks.rb              # Before/After hooks
│       └── world_extensions.rb   # Custom World methods
├── Gemfile
└── cucumber.yml                  # Cucumber configuration
```

---

## Configuration (cucumber.yml)

```yaml
# cucumber.yml
default: >
  --format progress
  --format html --out reports/cucumber-report.html
  --require features/support
  --require features/step_definitions
  --tags "not @wip"

ci: >
  --format progress
  --format junit --out reports/cucumber-junit.xml
  --strict
  --tags "not @wip and not @skip"

smoke: >
  --format progress
  --tags @smoke

critical: >
  --format progress
  --tags @critical
  --strict
```

---

## Environment Setup

```ruby
# features/support/env.rb
require 'capybara'
require 'capybara/cucumber'
require 'rspec/expectations'

# Configure Capybara
Capybara.default_driver = :selenium_chrome_headless
Capybara.app_host = ENV['APP_HOST'] || 'http://localhost:3000'
Capybara.default_max_wait_time = 5

# Include RSpec matchers in World
World(RSpec::Matchers)
```

---

## Step Definitions

```ruby
# features/step_definitions/auth_steps.rb

Given('I am on the login page') do
  visit '/login'
end

Given('I have a registered account with email {string}') do |email|
  @test_user = User.create!(
    email: email,
    password: 'SecurePass123!'
  )
end

When('I enter email {string}') do |email|
  fill_in 'Email', with: email
end

When('I enter password {string}') do |password|
  fill_in 'Password', with: password
end

When('I click the login button') do
  click_button 'Login'
end

Then('I should be redirected to the dashboard') do
  expect(page).to have_current_path('/dashboard')
end

Then('I should see {string}') do |text|
  expect(page).to have_content(text)
end

Then('I should see error message {string}') do |message|
  within('.error-message') do
    expect(page).to have_content(message)
  end
end
```

---

## Hooks

```ruby
# features/support/hooks.rb

Before do
  # Runs before each scenario
  @scenario_data = {}
end

After do |scenario|
  # Screenshot on failure
  if scenario.failed?
    screenshot_path = "reports/failure-#{Time.now.to_i}.png"
    page.save_screenshot(screenshot_path)
    attach(screenshot_path, 'image/png')
  end
end

Before('@database') do
  DatabaseCleaner.start
end

After('@database') do
  DatabaseCleaner.clean
end

Before('@auth') do
  @auth_token = authenticate_test_user
end

# Tagged hooks
Around('@slow') do |scenario, block|
  Capybara.default_max_wait_time = 30
  block.call
  Capybara.default_max_wait_time = 5
end
```

---

## World Extensions

```ruby
# features/support/world_extensions.rb

module AuthHelpers
  def login_as(email, password = 'password')
    visit '/login'
    fill_in 'Email', with: email
    fill_in 'Password', with: password
    click_button 'Login'
  end

  def current_user
    @current_user
  end
end

module ApiHelpers
  def api_get(endpoint, headers = {})
    @response = HTTParty.get(
      "#{Capybara.app_host}#{endpoint}",
      headers: headers.merge('Authorization' => "Bearer #{@auth_token}")
    )
  end

  def api_post(endpoint, body, headers = {})
    @response = HTTParty.post(
      "#{Capybara.app_host}#{endpoint}",
      body: body.to_json,
      headers: headers.merge(
        'Authorization' => "Bearer #{@auth_token}",
        'Content-Type' => 'application/json'
      )
    )
  end
end

World(AuthHelpers)
World(ApiHelpers)
```

---

## Data Tables

```ruby
Given('the following users exist:') do |table|
  table.hashes.each do |row|
    User.create!(
      email: row['email'],
      role: row['role'],
      active: row['active'] == 'true'
    )
  end
end

# Vertical table (key-value pairs)
When('I update my profile with:') do |table|
  data = table.rows_hash
  fill_in 'Name', with: data['name']
  fill_in 'Bio', with: data['bio']
  fill_in 'Location', with: data['location']
end
```

---

## Doc Strings

```ruby
When('I create a post with content:') do |content|
  fill_in 'Content', with: content
  click_button 'Create Post'
end

When('I send a POST request to {string} with:') do |endpoint, body|
  api_post(endpoint, JSON.parse(body))
end
```

---

## Running Tests

```bash
# Run all features
bundle exec cucumber

# Run with specific profile
bundle exec cucumber --profile ci

# Run specific feature
bundle exec cucumber features/auth/login.feature

# Run specific scenario by line
bundle exec cucumber features/auth/login.feature:15

# Run with tags
bundle exec cucumber --tags @smoke
bundle exec cucumber --tags "@critical and @auth"
bundle exec cucumber --tags "not @wip"

# Dry run
bundle exec cucumber --dry-run
```

---

## Resources

- [Cucumber Ruby Documentation](https://cucumber.io/docs/installation/ruby/)
- [Cucumber Ruby GitHub](https://github.com/cucumber/cucumber-ruby)
- [Capybara Documentation](https://rubydoc.info/github/teamcapybara/capybara)
- [RSpec Expectations](https://rspec.info/features/3-12/rspec-expectations/)
