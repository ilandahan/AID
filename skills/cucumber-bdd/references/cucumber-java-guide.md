# Cucumber for Java

Guide for implementing Cucumber BDD in Java projects.

---

## Prerequisites

- Java 11+ (JDK)
- Maven or Gradle
- IDE with Cucumber plugin (IntelliJ IDEA, Eclipse)

---

## Installation (Maven)

```xml
<!-- pom.xml -->
<dependencies>
    <!-- Cucumber -->
    <dependency>
        <groupId>io.cucumber</groupId>
        <artifactId>cucumber-java</artifactId>
        <version>7.15.0</version>
        <scope>test</scope>
    </dependency>

    <!-- JUnit 5 Integration -->
    <dependency>
        <groupId>io.cucumber</groupId>
        <artifactId>cucumber-junit-platform-engine</artifactId>
        <version>7.15.0</version>
        <scope>test</scope>
    </dependency>

    <!-- Assertions -->
    <dependency>
        <groupId>org.assertj</groupId>
        <artifactId>assertj-core</artifactId>
        <version>3.24.2</version>
        <scope>test</scope>
    </dependency>
</dependencies>

<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <version>3.2.3</version>
            <configuration>
                <properties>
                    <configurationParameters>
                        cucumber.junit-platform.naming-strategy=long
                    </configurationParameters>
                </properties>
            </configuration>
        </plugin>
    </plugins>
</build>
```

---

## Installation (Gradle)

```groovy
// build.gradle
dependencies {
    testImplementation 'io.cucumber:cucumber-java:7.15.0'
    testImplementation 'io.cucumber:cucumber-junit-platform-engine:7.15.0'
    testImplementation 'org.assertj:assertj-core:3.24.2'
}

tasks.named('test') {
    useJUnitPlatform()
    systemProperty("cucumber.junit-platform.naming-strategy", "long")
}
```

---

## Project Structure

```
src/
├── main/java/
│   └── com/example/
│       └── ...
└── test/
    ├── java/
    │   └── com/example/
    │       ├── RunCucumberTest.java      # Test runner
    │       └── stepdefs/
    │           ├── AuthSteps.java        # Step definitions
    │           └── CommonSteps.java
    └── resources/
        ├── features/
        │   ├── auth/
        │   │   └── login.feature
        │   └── checkout/
        │       └── cart.feature
        └── cucumber.properties           # Configuration
```

---

## Test Runner

```java
// src/test/java/com/example/RunCucumberTest.java
package com.example;

import org.junit.platform.suite.api.ConfigurationParameter;
import org.junit.platform.suite.api.IncludeEngines;
import org.junit.platform.suite.api.SelectPackages;
import org.junit.platform.suite.api.Suite;

import static io.cucumber.junit.platform.engine.Constants.*;

@Suite
@IncludeEngines("cucumber")
@SelectPackages("com.example")
@ConfigurationParameter(key = FEATURES_PROPERTY_NAME, value = "src/test/resources/features")
@ConfigurationParameter(key = GLUE_PROPERTY_NAME, value = "com.example.stepdefs")
@ConfigurationParameter(key = PLUGIN_PROPERTY_NAME, value = "pretty, html:target/cucumber-report.html")
public class RunCucumberTest {
}
```

---

## Step Definitions

```java
// src/test/java/com/example/stepdefs/AuthSteps.java
package com.example.stepdefs;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.When;
import io.cucumber.java.en.Then;
import io.cucumber.java.Before;
import io.cucumber.java.After;

import static org.assertj.core.api.Assertions.assertThat;

public class AuthSteps {

    private String currentUser;
    private boolean loginSuccess;
    private String errorMessage;

    @Before
    public void setup() {
        // Runs before each scenario
        currentUser = null;
        loginSuccess = false;
    }

    @Given("I am on the login page")
    public void i_am_on_the_login_page() {
        // Navigate to login page
        System.out.println("Navigating to login page");
    }

    @Given("I have a registered account with email {string}")
    public void i_have_a_registered_account(String email) {
        // Create test user or verify exists
        this.currentUser = email;
    }

    @When("I enter email {string}")
    public void i_enter_email(String email) {
        // Enter email in form
    }

    @When("I enter password {string}")
    public void i_enter_password(String password) {
        // Enter password in form
    }

    @When("I click the login button")
    public void i_click_login_button() {
        // Submit login form
        loginSuccess = true; // Simulated
    }

    @Then("I should be redirected to the dashboard")
    public void i_should_be_redirected_to_dashboard() {
        assertThat(loginSuccess).isTrue();
    }

    @Then("I should see {string}")
    public void i_should_see(String text) {
        // Verify text is visible
        assertThat(text).isNotEmpty();
    }

    @Then("I should see error message {string}")
    public void i_should_see_error_message(String message) {
        assertThat(errorMessage).isEqualTo(message);
    }

    @After
    public void cleanup() {
        // Runs after each scenario
        currentUser = null;
    }
}
```

---

## Data Tables

```java
@Given("the following users exist:")
public void the_following_users_exist(DataTable dataTable) {
    List<Map<String, String>> users = dataTable.asMaps();
    for (Map<String, String> user : users) {
        String email = user.get("email");
        String role = user.get("role");
        // Create user
    }
}
```

---

## Scenario Context (Dependency Injection)

```java
// Using PicoContainer for DI
// Add to pom.xml:
// <dependency>
//     <groupId>io.cucumber</groupId>
//     <artifactId>cucumber-picocontainer</artifactId>
//     <version>7.15.0</version>
// </dependency>

public class ScenarioContext {
    private String token;
    private Response lastResponse;

    public void setToken(String token) { this.token = token; }
    public String getToken() { return token; }
    public void setLastResponse(Response r) { this.lastResponse = r; }
    public Response getLastResponse() { return lastResponse; }
}

// In step definitions
public class AuthSteps {
    private final ScenarioContext context;

    public AuthSteps(ScenarioContext context) {
        this.context = context;
    }

    @When("I login as {string}")
    public void i_login_as(String email) {
        String token = authService.login(email, "password");
        context.setToken(token);
    }
}
```

---

## Running Tests

```bash
# Maven
mvn test

# With specific tags
mvn test -Dcucumber.filter.tags="@smoke"

# With specific feature
mvn test -Dcucumber.features="src/test/resources/features/auth"

# Gradle
./gradlew test

# With tags
./gradlew test -Dcucumber.filter.tags="@critical"
```

---

## Configuration

```properties
# src/test/resources/cucumber.properties
cucumber.publish.quiet=true
cucumber.plugin=pretty, html:target/cucumber-report.html, json:target/cucumber-report.json
cucumber.glue=com.example.stepdefs
cucumber.features=src/test/resources/features
```

---

## Resources

- [Cucumber-JVM Documentation](https://cucumber.io/docs/installation/java/)
- [Cucumber-JVM GitHub](https://github.com/cucumber/cucumber-jvm)
- [AssertJ Documentation](https://assertj.github.io/doc/)
