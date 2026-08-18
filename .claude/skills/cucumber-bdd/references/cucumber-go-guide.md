# Cucumber for Go (Godog)

Guide for implementing BDD in Go using Godog (the official Cucumber implementation for Go).

---

## Prerequisites

- Go 1.21+
- Go modules enabled
- Understanding of Go testing package

---

## Installation

```bash
# Add godog to your project
go get github.com/cucumber/godog

# Install godog CLI (optional, for running features directly)
go install github.com/cucumber/godog/cmd/godog@latest
```

---

## Project Structure

```
project/
├── features/
│   ├── auth/
│   │   └── login.feature
│   └── checkout/
│       └── cart.feature
├── internal/
│   └── ... (your application code)
├── test/
│   ├── features_test.go         # Test runner
│   ├── auth_steps_test.go       # Auth step definitions
│   ├── api_steps_test.go        # API step definitions
│   └── context_test.go          # Test context
├── go.mod
└── go.sum
```

---

## Test Runner

```go
// test/features_test.go
package test

import (
    "os"
    "testing"

    "github.com/cucumber/godog"
    "github.com/cucumber/godog/colors"
)

var opts = godog.Options{
    Output: colors.Colored(os.Stdout),
    Format: "progress",
    Paths:  []string{"../features"},
    Tags:   "~@wip",
}

func init() {
    godog.BindCommandLineFlags("godog.", &opts)
}

func TestFeatures(t *testing.T) {
    suite := godog.TestSuite{
        ScenarioInitializer: InitializeScenario,
        Options:             &opts,
    }

    if suite.Run() != 0 {
        t.Fatal("non-zero status returned, failed to run feature tests")
    }
}

func InitializeScenario(ctx *godog.ScenarioContext) {
    // Initialize test context
    testCtx := &TestContext{}

    // Register hooks
    ctx.Before(func(ctx context.Context, sc *godog.Scenario) (context.Context, error) {
        testCtx.Reset()
        return ctx, nil
    })

    ctx.After(func(ctx context.Context, sc *godog.Scenario, err error) (context.Context, error) {
        testCtx.Cleanup()
        return ctx, nil
    })

    // Register step definitions
    RegisterAuthSteps(ctx, testCtx)
    RegisterAPISteps(ctx, testCtx)
    RegisterCommonSteps(ctx, testCtx)
}
```

---

## Test Context

```go
// test/context_test.go
package test

import (
    "net/http"
    "net/http/httptest"
)

type TestContext struct {
    Server      *httptest.Server
    Client      *http.Client
    AuthToken   string
    Response    *http.Response
    ResponseBody []byte
    TestUser    *User
    Error       error
}

func (tc *TestContext) Reset() {
    tc.AuthToken = ""
    tc.Response = nil
    tc.ResponseBody = nil
    tc.TestUser = nil
    tc.Error = nil
}

func (tc *TestContext) Cleanup() {
    if tc.Server != nil {
        tc.Server.Close()
    }
}

type User struct {
    ID    string
    Email string
    Role  string
}
```

---

## Step Definitions

```go
// test/auth_steps_test.go
package test

import (
    "context"
    "fmt"

    "github.com/cucumber/godog"
)

func RegisterAuthSteps(ctx *godog.ScenarioContext, tc *TestContext) {
    ctx.Step(`^I am on the login page$`, tc.iAmOnTheLoginPage)
    ctx.Step(`^I have a registered account with email "([^"]*)"$`, tc.iHaveARegisteredAccount)
    ctx.Step(`^I enter email "([^"]*)"$`, tc.iEnterEmail)
    ctx.Step(`^I enter password "([^"]*)"$`, tc.iEnterPassword)
    ctx.Step(`^I click the login button$`, tc.iClickTheLoginButton)
    ctx.Step(`^I should be redirected to the dashboard$`, tc.iShouldBeRedirectedToDashboard)
    ctx.Step(`^I should see "([^"]*)"$`, tc.iShouldSee)
    ctx.Step(`^I should see error message "([^"]*)"$`, tc.iShouldSeeErrorMessage)
}

func (tc *TestContext) iAmOnTheLoginPage() error {
    // Navigate to login page
    return nil
}

func (tc *TestContext) iHaveARegisteredAccount(email string) error {
    tc.TestUser = &User{
        ID:    "test-id",
        Email: email,
        Role:  "user",
    }
    // Create user in test database
    return nil
}

func (tc *TestContext) iEnterEmail(email string) error {
    // Store email for login
    return nil
}

func (tc *TestContext) iEnterPassword(password string) error {
    // Store password for login
    return nil
}

func (tc *TestContext) iClickTheLoginButton() error {
    // Perform login
    tc.AuthToken = "test-token"
    return nil
}

func (tc *TestContext) iShouldBeRedirectedToDashboard() error {
    if tc.AuthToken == "" {
        return fmt.Errorf("not logged in")
    }
    return nil
}

func (tc *TestContext) iShouldSee(text string) error {
    // Check page contains text
    return nil
}

func (tc *TestContext) iShouldSeeErrorMessage(message string) error {
    if tc.Error == nil {
        return fmt.Errorf("expected error message but got none")
    }
    return nil
}
```

---

## API Step Definitions

```go
// test/api_steps_test.go
package test

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"

    "github.com/cucumber/godog"
)

func RegisterAPISteps(ctx *godog.ScenarioContext, tc *TestContext) {
    ctx.Step(`^I send a GET request to "([^"]*)"$`, tc.iSendGETRequest)
    ctx.Step(`^I send a POST request to "([^"]*)" with:$`, tc.iSendPOSTRequest)
    ctx.Step(`^the response status should be (\d+)$`, tc.theResponseStatusShouldBe)
    ctx.Step(`^the response should contain:$`, tc.theResponseShouldContain)
}

func (tc *TestContext) iSendGETRequest(endpoint string) error {
    req, err := http.NewRequest("GET", tc.Server.URL+endpoint, nil)
    if err != nil {
        return err
    }

    if tc.AuthToken != "" {
        req.Header.Set("Authorization", "Bearer "+tc.AuthToken)
    }

    tc.Response, err = tc.Client.Do(req)
    if err != nil {
        return err
    }

    tc.ResponseBody, err = io.ReadAll(tc.Response.Body)
    tc.Response.Body.Close()
    return err
}

func (tc *TestContext) iSendPOSTRequest(endpoint string, body *godog.DocString) error {
    req, err := http.NewRequest("POST", tc.Server.URL+endpoint, bytes.NewBufferString(body.Content))
    if err != nil {
        return err
    }

    req.Header.Set("Content-Type", "application/json")
    if tc.AuthToken != "" {
        req.Header.Set("Authorization", "Bearer "+tc.AuthToken)
    }

    tc.Response, err = tc.Client.Do(req)
    if err != nil {
        return err
    }

    tc.ResponseBody, err = io.ReadAll(tc.Response.Body)
    tc.Response.Body.Close()
    return err
}

func (tc *TestContext) theResponseStatusShouldBe(status int) error {
    if tc.Response.StatusCode != status {
        return fmt.Errorf("expected status %d, got %d", status, tc.Response.StatusCode)
    }
    return nil
}

func (tc *TestContext) theResponseShouldContain(expected *godog.DocString) error {
    var expectedData map[string]interface{}
    if err := json.Unmarshal([]byte(expected.Content), &expectedData); err != nil {
        return err
    }

    var actualData map[string]interface{}
    if err := json.Unmarshal(tc.ResponseBody, &actualData); err != nil {
        return err
    }

    for key, value := range expectedData {
        if actualData[key] != value {
            return fmt.Errorf("expected %s=%v, got %v", key, value, actualData[key])
        }
    }
    return nil
}
```

---

## Data Tables

```go
// test/data_steps_test.go
package test

import (
    "github.com/cucumber/godog"
)

func (tc *TestContext) theFollowingUsersExist(table *godog.Table) error {
    for _, row := range table.Rows[1:] { // Skip header row
        user := &User{
            Email: row.Cells[0].Value,
            Role:  row.Cells[1].Value,
        }
        // Create user in test database
        _ = user
    }
    return nil
}

// Feature file usage:
// Given the following users exist:
//   | email              | role    |
//   | alice@example.com  | admin   |
//   | bob@example.com    | user    |
```

---

## Hooks

```go
// In test/features_test.go - InitializeScenario function

func InitializeScenario(ctx *godog.ScenarioContext) {
    testCtx := &TestContext{}

    // Before all scenarios
    ctx.Before(func(ctx context.Context, sc *godog.Scenario) (context.Context, error) {
        testCtx.Reset()
        testCtx.Client = &http.Client{}
        return ctx, nil
    })

    // After all scenarios
    ctx.After(func(ctx context.Context, sc *godog.Scenario, err error) (context.Context, error) {
        testCtx.Cleanup()
        return ctx, nil
    })

    // Before specific tags
    ctx.Before(func(ctx context.Context, sc *godog.Scenario) (context.Context, error) {
        for _, tag := range sc.Tags {
            if tag.Name == "@auth" {
                testCtx.AuthToken = "test-auth-token"
            }
            if tag.Name == "@database" {
                // Start transaction
            }
        }
        return ctx, nil
    })
}
```

---

## Running Tests

```bash
# Run all features with go test
go test -v ./test/...

# Run with godog CLI
godog run features/

# Run specific feature
godog run features/auth/login.feature

# Run with tags
godog run --tags=@smoke features/
godog run --tags="@critical and not @wip" features/

# With specific format
godog run --format=pretty features/
godog run --format=progress features/
godog run --format=cucumber features/  # JSON output

# Generate JUnit report
godog run --format=junit:reports/junit.xml features/
```

---

## Configuration via Environment

```bash
# Set options via environment
GODOG_FORMAT=progress go test ./test/...
GODOG_TAGS="@smoke" go test ./test/...
```

---

## Resources

- [Godog Documentation](https://github.com/cucumber/godog)
- [Godog Examples](https://github.com/cucumber/godog/tree/main/_examples)
- [Go Testing Package](https://pkg.go.dev/testing)
- [Cucumber Expression Syntax](https://cucumber.io/docs/cucumber/cucumber-expressions/)
