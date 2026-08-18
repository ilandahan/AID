# Test Patterns by Framework

Extended test patterns for Jest, Vitest, and Pytest.

---

## Jest / Vitest (TypeScript/JavaScript)

### Setup & Teardown

```typescript
// Global setup (runs once before all tests)
// jest.setup.ts or vitest.setup.ts
beforeAll(async () => {
  await db.connect();
  await db.migrate();
});

afterAll(async () => {
  await db.disconnect();
});

// Per-test setup
describe('UserService', () => {
  let testUser: User;

  beforeEach(async () => {
    // Fresh data for each test
    testUser = await createUser(testData);
  });

  afterEach(async () => {
    // Cleanup after each test
    await deleteUser(testUser.id);
  });
});
```

### Async Testing

```typescript
// Promises
test('fetches user data', async () => {
  const user = await fetchUser('usr_123');
  expect(user.name).toBe('Jane');
});

// Resolves/Rejects
test('resolves with user', async () => {
  await expect(fetchUser('usr_123')).resolves.toMatchObject({
    id: 'usr_123'
  });
});

test('rejects on not found', async () => {
  await expect(fetchUser('invalid')).rejects.toThrow('Not found');
});

// Callbacks (legacy)
test('callback style', (done) => {
  fetchUserCallback('usr_123', (err, user) => {
    expect(err).toBeNull();
    expect(user.name).toBe('Jane');
    done();
  });
});
```

### Mocking

```typescript
// Module mock
jest.mock('./database', () => ({
  query: jest.fn()
}));

// Inline mock
const mockFn = jest.fn()
  .mockReturnValue('default')
  .mockReturnValueOnce('first call')
  .mockResolvedValue('async result');

// Spy on existing
const spy = jest.spyOn(userService, 'create');
spy.mockResolvedValue(mockUser);

// Restore after test
afterEach(() => {
  jest.restoreAllMocks();
});

// Verify calls
expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
expect(mockFn).toHaveBeenCalledTimes(2);
```

### Fake Timers

```typescript
describe('scheduled tasks', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('executes after delay', () => {
    const callback = jest.fn();
    scheduleTask(callback, 5000);

    expect(callback).not.toHaveBeenCalled();

    jest.advanceTimersByTime(5000);

    expect(callback).toHaveBeenCalled();
  });

  test('debounces rapid calls', () => {
    const callback = jest.fn();
    const debounced = debounce(callback, 300);

    debounced();
    debounced();
    debounced();

    jest.advanceTimersByTime(300);

    expect(callback).toHaveBeenCalledTimes(1);
  });
});
```

### Snapshot Testing

```typescript
// Component snapshot
test('renders correctly', () => {
  const tree = render(<Button label="Click me" />);
  expect(tree).toMatchSnapshot();
});

// Inline snapshot
test('formats date', () => {
  expect(formatDate(new Date('2024-01-15'))).toMatchInlineSnapshot(
    `"January 15, 2024"`
  );
});

// Update snapshots: npm test -- -u
```

### Table-Driven Tests

```typescript
describe('validateEmail', () => {
  test.each([
    ['valid@example.com', true],
    ['user+tag@domain.co.uk', true],
    ['invalid', false],
    ['@nodomain.com', false],
    ['spaces in@email.com', false],
  ])('validateEmail(%s) returns %s', (email, expected) => {
    expect(validateEmail(email)).toBe(expected);
  });
});

// With objects
describe('calculateDiscount', () => {
  test.each([
    { price: 100, discount: 10, expected: 90 },
    { price: 100, discount: 0, expected: 100 },
    { price: 50, discount: 50, expected: 25 },
  ])('$price with $discount% off = $expected', ({ price, discount, expected }) => {
    expect(calculateDiscount(price, discount)).toBe(expected);
  });
});
```

### Error Testing

```typescript
// Sync errors
test('throws on invalid input', () => {
  expect(() => processData(null)).toThrow('Input required');
  expect(() => processData(null)).toThrow(ValidationError);
});

// Async errors
test('rejects on network failure', async () => {
  await expect(fetchData()).rejects.toThrow('Network error');
  await expect(fetchData()).rejects.toBeInstanceOf(NetworkError);
});

// Error properties
test('error has correct properties', async () => {
  try {
    await fetchData();
  } catch (error) {
    expect(error).toBeInstanceOf(ApiError);
    expect(error.statusCode).toBe(404);
    expect(error.message).toBe('Resource not found');
  }
});
```

---

## Pytest (Python)

### Fixtures

```python
import pytest
from datetime import datetime

# Simple fixture
@pytest.fixture
def test_user():
    return {
        'id': 'usr_123',
        'email': 'test@example.com',
        'name': 'Test User'
    }

# Fixture with setup/teardown
@pytest.fixture
def db_session():
    session = create_session()
    session.begin()
    yield session
    session.rollback()
    session.close()

# Fixture with parameters
@pytest.fixture(params=['admin', 'user', 'guest'])
def user_role(request):
    return request.param

def test_permissions(user_role):
    # Runs 3 times with different roles
    user = create_user(role=user_role)
    assert user.role == user_role

# Scoped fixtures
@pytest.fixture(scope='module')
def expensive_resource():
    # Created once per module
    return load_large_dataset()

@pytest.fixture(scope='session')
def database():
    # Created once per test session
    db = connect_database()
    yield db
    db.disconnect()
```

### Parametrized Tests

```python
@pytest.mark.parametrize('email,expected', [
    ('valid@example.com', True),
    ('user+tag@domain.co.uk', True),
    ('invalid', False),
    ('@nodomain.com', False),
])
def test_validate_email(email, expected):
    assert validate_email(email) == expected

# Multiple parameters
@pytest.mark.parametrize('a,b,expected', [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected

# Parametrize with IDs
@pytest.mark.parametrize('input,expected', [
    pytest.param('hello', 'HELLO', id='lowercase'),
    pytest.param('HELLO', 'HELLO', id='already_upper'),
    pytest.param('HeLLo', 'HELLO', id='mixed_case'),
])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_fetch_user():
    user = await fetch_user('usr_123')
    assert user['name'] == 'Jane'

@pytest.mark.asyncio
async def test_concurrent_operations():
    results = await asyncio.gather(
        fetch_user('usr_1'),
        fetch_user('usr_2'),
        fetch_user('usr_3')
    )
    assert len(results) == 3
```

### Exception Testing

```python
def test_raises_on_invalid_input():
    with pytest.raises(ValueError) as exc_info:
        process_data(None)

    assert 'Input required' in str(exc_info.value)

def test_raises_with_match():
    with pytest.raises(ValueError, match=r'Invalid.*format'):
        parse_date('not-a-date')

@pytest.mark.asyncio
async def test_async_raises():
    with pytest.raises(NetworkError):
        await fetch_data()
```

### Mocking with pytest-mock

```python
def test_with_mock(mocker):
    # Mock a function
    mock_fetch = mocker.patch('module.fetch_data')
    mock_fetch.return_value = {'data': 'mocked'}

    result = process_data()

    mock_fetch.assert_called_once()
    assert result['data'] == 'mocked'

def test_spy(mocker):
    # Spy on real function
    spy = mocker.spy(user_service, 'create')

    create_user(data)

    spy.assert_called_once_with(data)

def test_mock_datetime(mocker):
    # Mock datetime
    mock_now = mocker.patch('module.datetime')
    mock_now.now.return_value = datetime(2024, 1, 15, 10, 30)

    result = get_current_time()

    assert result.year == 2024
```

### Markers

```python
# Skip test
@pytest.mark.skip(reason='Not implemented yet')
def test_future_feature():
    pass

# Conditional skip
@pytest.mark.skipif(sys.platform == 'win32', reason='Unix only')
def test_unix_feature():
    pass

# Expected failure
@pytest.mark.xfail(reason='Known bug #123')
def test_known_bug():
    assert broken_function() == expected

# Slow tests
@pytest.mark.slow
def test_integration():
    pass

# Run with: pytest -m "not slow"

# Custom markers in pytest.ini
# [pytest]
# markers =
#     slow: marks tests as slow
#     integration: marks integration tests
```

---

## Common Patterns

### AAA Pattern (Arrange, Act, Assert)

```typescript
test('creates order with correct total', async () => {
  // Arrange
  const user = createTestUser();
  const items = [
    { productId: 'prod_1', quantity: 2, price: 10 },
    { productId: 'prod_2', quantity: 1, price: 25 }
  ];

  // Act
  const order = await createOrder(user.id, items);

  // Assert
  expect(order.total).toBe(45);
  expect(order.items).toHaveLength(2);
  expect(order.userId).toBe(user.id);
});
```

### Given-When-Then (BDD Style)

```typescript
describe('Order creation', () => {
  describe('given a user with items in cart', () => {
    let user: User;
    let cartItems: CartItem[];

    beforeEach(() => {
      user = createTestUser();
      cartItems = createTestCartItems(3);
    });

    describe('when creating an order', () => {
      let order: Order;

      beforeEach(async () => {
        order = await createOrder(user.id, cartItems);
      });

      it('then calculates the correct total', () => {
        const expectedTotal = cartItems.reduce(
          (sum, item) => sum + item.price * item.quantity,
          0
        );
        expect(order.total).toBe(expectedTotal);
      });

      it('then clears the cart', async () => {
        const cart = await getCart(user.id);
        expect(cart.items).toHaveLength(0);
      });
    });
  });
});
```

### Builder Pattern for Test Data

```typescript
class UserBuilder {
  private user: Partial<User> = {
    id: `usr_${randomId()}`,
    email: 'default@example.com',
    name: 'Default User',
    role: 'user',
    status: 'active'
  };

  withEmail(email: string): this {
    this.user.email = email;
    return this;
  }

  withRole(role: Role): this {
    this.user.role = role;
    return this;
  }

  asAdmin(): this {
    this.user.role = 'admin';
    return this;
  }

  inactive(): this {
    this.user.status = 'inactive';
    return this;
  }

  build(): User {
    return this.user as User;
  }
}

// Usage
const admin = new UserBuilder().asAdmin().build();
const inactiveUser = new UserBuilder().inactive().build();
```

### Test Helpers

```typescript
// tests/helpers/assertions.ts
export function expectValidUser(user: unknown): asserts user is User {
  expect(user).toMatchObject({
    id: expect.stringMatching(/^usr_/),
    email: expect.stringContaining('@'),
    createdAt: expect.any(Date)
  });
}

// tests/helpers/setup.ts
export async function setupTestDatabase() {
  await db.migrate();
  await db.seed();
}

export async function cleanupTestDatabase() {
  await db.truncateAll();
}

// Usage
test('creates valid user', async () => {
  const user = await createUser(data);
  expectValidUser(user);
});
```
