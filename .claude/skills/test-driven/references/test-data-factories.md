# Test Data Factories

Creating realistic, maintainable test data.

---

## Why Factories?

| Approach | Problem |
|----------|---------|
| Inline data | Repetitive, hard to maintain |
| Shared fixtures | Tests become coupled |
| Random data | Non-deterministic, hard to debug |
| **Factories** | Reusable, customizable, realistic |

---

## Basic Factory Pattern

### Simple Factory Function

```typescript
// tests/factories/userFactory.ts
import { v4 as uuid } from 'uuid';

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'guest';
  status: 'active' | 'inactive' | 'pending';
  createdAt: Date;
  updatedAt: Date;
}

let counter = 0;

export function createUser(overrides: Partial<User> = {}): User {
  counter++;
  const now = new Date();

  return {
    id: `usr_${uuid().slice(0, 8)}`,
    email: `user${counter}@example.com`,
    name: `Test User ${counter}`,
    role: 'user',
    status: 'active',
    createdAt: now,
    updatedAt: now,
    ...overrides
  };
}

// Usage
const user = createUser();
const admin = createUser({ role: 'admin' });
const inactive = createUser({ status: 'inactive', name: 'Inactive User' });
```

### Factory with Relationships

```typescript
// tests/factories/orderFactory.ts
import { createUser } from './userFactory';
import { createProduct } from './productFactory';

export interface OrderItem {
  productId: string;
  name: string;
  quantity: number;
  unitPrice: number;
}

export interface Order {
  id: string;
  userId: string;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  total: number;
  status: 'pending' | 'paid' | 'shipped' | 'delivered';
  createdAt: Date;
}

export function createOrder(overrides: Partial<Order> = {}): Order {
  // Generate items if not provided
  const items = overrides.items ?? [
    createOrderItem(),
    createOrderItem()
  ];

  const subtotal = items.reduce(
    (sum, item) => sum + item.unitPrice * item.quantity,
    0
  );
  const tax = Math.round(subtotal * 0.08 * 100) / 100;
  const total = subtotal + tax;

  return {
    id: `ord_${Date.now()}`,
    userId: overrides.userId ?? createUser().id,
    items,
    subtotal,
    tax,
    total,
    status: 'pending',
    createdAt: new Date(),
    ...overrides
  };
}

export function createOrderItem(overrides: Partial<OrderItem> = {}): OrderItem {
  const product = createProduct();
  return {
    productId: product.id,
    name: product.name,
    quantity: Math.floor(Math.random() * 3) + 1,
    unitPrice: product.price,
    ...overrides
  };
}

// Usage
const order = createOrder();
const paidOrder = createOrder({ status: 'paid' });
const orderWithItems = createOrder({
  items: [
    createOrderItem({ quantity: 5, unitPrice: 10 }),
    createOrderItem({ quantity: 2, unitPrice: 25 })
  ]
});
```

---

## Builder Pattern

### Fluent Builder

```typescript
// tests/factories/builders/UserBuilder.ts
export class UserBuilder {
  private data: Partial<User> = {};

  static create(): UserBuilder {
    return new UserBuilder();
  }

  withEmail(email: string): this {
    this.data.email = email;
    return this;
  }

  withName(name: string): this {
    this.data.name = name;
    return this;
  }

  withRole(role: User['role']): this {
    this.data.role = role;
    return this;
  }

  asAdmin(): this {
    this.data.role = 'admin';
    return this;
  }

  asGuest(): this {
    this.data.role = 'guest';
    return this;
  }

  active(): this {
    this.data.status = 'active';
    return this;
  }

  inactive(): this {
    this.data.status = 'inactive';
    return this;
  }

  pending(): this {
    this.data.status = 'pending';
    return this;
  }

  createdDaysAgo(days: number): this {
    const date = new Date();
    date.setDate(date.getDate() - days);
    this.data.createdAt = date;
    return this;
  }

  build(): User {
    return createUser(this.data);
  }
}

// Usage
const admin = UserBuilder.create()
  .asAdmin()
  .withEmail('admin@company.com')
  .build();

const oldInactiveUser = UserBuilder.create()
  .inactive()
  .createdDaysAgo(365)
  .build();

const guest = UserBuilder.create()
  .asGuest()
  .withName('Anonymous')
  .build();
```

### Builder with Validation

```typescript
export class OrderBuilder {
  private data: Partial<Order> = {};
  private itemBuilders: OrderItemBuilder[] = [];

  static create(): OrderBuilder {
    return new OrderBuilder();
  }

  forUser(userId: string): this {
    this.data.userId = userId;
    return this;
  }

  withItem(configure: (builder: OrderItemBuilder) => void): this {
    const itemBuilder = OrderItemBuilder.create();
    configure(itemBuilder);
    this.itemBuilders.push(itemBuilder);
    return this;
  }

  withStatus(status: Order['status']): this {
    this.data.status = status;
    return this;
  }

  paid(): this {
    return this.withStatus('paid');
  }

  shipped(): this {
    return this.withStatus('shipped');
  }

  build(): Order {
    if (this.itemBuilders.length === 0) {
      throw new Error('Order must have at least one item');
    }

    return createOrder({
      ...this.data,
      items: this.itemBuilders.map(b => b.build())
    });
  }
}

// Usage
const order = OrderBuilder.create()
  .forUser('usr_123')
  .withItem(item => item.product('prod_shirt').quantity(2))
  .withItem(item => item.product('prod_jeans').quantity(1))
  .paid()
  .build();
```

---

## Realistic Data Generation

### Using Faker

```typescript
import { faker } from '@faker-js/faker';

export function createRealisticUser(overrides: Partial<User> = {}): User {
  const firstName = faker.person.firstName();
  const lastName = faker.person.lastName();

  return {
    id: `usr_${faker.string.alphanumeric(10)}`,
    email: faker.internet.email({ firstName, lastName }),
    name: `${firstName} ${lastName}`,
    role: faker.helpers.arrayElement(['admin', 'user', 'guest']),
    status: faker.helpers.weightedArrayElement([
      { value: 'active', weight: 80 },
      { value: 'inactive', weight: 15 },
      { value: 'pending', weight: 5 }
    ]),
    createdAt: faker.date.past({ years: 2 }),
    updatedAt: faker.date.recent({ days: 30 }),
    ...overrides
  };
}

export function createRealisticAddress(): Address {
  return {
    street: faker.location.streetAddress(),
    city: faker.location.city(),
    state: faker.location.state({ abbreviated: true }),
    postalCode: faker.location.zipCode(),
    country: faker.location.countryCode()
  };
}

export function createRealisticProduct(): Product {
  return {
    id: `prod_${faker.string.alphanumeric(10)}`,
    name: faker.commerce.productName(),
    description: faker.commerce.productDescription(),
    price: parseFloat(faker.commerce.price({ min: 10, max: 500 })),
    category: faker.commerce.department(),
    sku: faker.string.alphanumeric(8).toUpperCase(),
    inStock: faker.datatype.boolean({ probability: 0.85 })
  };
}
```

### Seeded Random for Reproducibility

```typescript
import { faker } from '@faker-js/faker';

// Set seed for reproducible tests
faker.seed(12345);

// Same seed produces same data every time
const user1 = createRealisticUser(); // Always same user
const user2 = createRealisticUser(); // Always same second user

// Reset seed between test files
beforeEach(() => {
  faker.seed(Date.now());
});
```

---

## Specialized Factories

### Edge Case Factory

```typescript
export const EdgeCaseUsers = {
  // Unicode names
  unicode: () => createUser({
    name: '日本語名前 Émile Müller Иван',
    email: 'unicode.user@example.com'
  }),

  // Maximum length name
  maxLengthName: () => createUser({
    name: 'A'.repeat(100)
  }),

  // Special characters in email
  specialEmail: () => createUser({
    email: "test+special.chars'@sub.domain.example.co.uk"
  }),

  // Empty optional fields
  minimal: () => createUser({
    name: '',
    bio: undefined,
    phone: null
  }),

  // Boundary dates
  veryOld: () => createUser({
    createdAt: new Date('2000-01-01')
  }),

  justCreated: () => createUser({
    createdAt: new Date(),
    updatedAt: new Date()
  }),

  // All fields populated
  complete: () => createUser({
    name: 'Complete User',
    email: 'complete@example.com',
    bio: 'Full bio text',
    phone: '+1-555-123-4567',
    avatar: 'https://example.com/avatar.jpg',
    preferences: {
      theme: 'dark',
      language: 'en',
      notifications: true
    }
  })
};

// Usage in tests
test('handles unicode names', async () => {
  const user = EdgeCaseUsers.unicode();
  const saved = await userService.create(user);
  expect(saved.name).toBe(user.name);
});

test('validates max length', async () => {
  const user = EdgeCaseUsers.maxLengthName();
  await expect(userService.create(user))
    .rejects.toThrow('Name too long');
});
```

### Scenario Factories

```typescript
export const Scenarios = {
  // E-commerce checkout
  checkoutReady: () => {
    const user = createUser({ status: 'active' });
    const products = [createProduct(), createProduct(), createProduct()];
    const cart = createCart({
      userId: user.id,
      items: products.map(p => ({
        productId: p.id,
        quantity: Math.floor(Math.random() * 3) + 1
      }))
    });
    const address = createAddress({ userId: user.id });

    return { user, products, cart, address };
  },

  // User with order history
  returningCustomer: () => {
    const user = createUser({
      createdAt: new Date('2023-01-01'),
      status: 'active'
    });

    const orders = Array.from({ length: 5 }, (_, i) => {
      const date = new Date();
      date.setMonth(date.getMonth() - i);
      return createOrder({
        userId: user.id,
        status: 'delivered',
        createdAt: date
      });
    });

    return { user, orders };
  },

  // Admin with permissions
  adminWithTeam: () => {
    const admin = createUser({ role: 'admin' });
    const team = Array.from({ length: 5 }, () =>
      createUser({ managerId: admin.id })
    );

    return { admin, team };
  }
};

// Usage
test('checkout flow', async () => {
  const { user, cart, address } = Scenarios.checkoutReady();

  const order = await checkoutService.process({
    userId: user.id,
    cartId: cart.id,
    addressId: address.id
  });

  expect(order.status).toBe('pending');
});
```

---

## Database Factory (with Persistence)

### Factory that Saves to DB

```typescript
// tests/factories/dbFactories.ts
import { prisma } from '../setup/prisma';

export async function createDbUser(
  overrides: Partial<Prisma.UserCreateInput> = {}
): Promise<User> {
  return prisma.user.create({
    data: {
      email: `user${Date.now()}@example.com`,
      name: 'Test User',
      role: 'user',
      ...overrides
    }
  });
}

export async function createDbOrder(
  userId: string,
  overrides: Partial<Prisma.OrderCreateInput> = {}
): Promise<Order> {
  return prisma.order.create({
    data: {
      userId,
      status: 'pending',
      items: {
        create: [
          { productId: 'prod_1', quantity: 1, price: 10 },
          { productId: 'prod_2', quantity: 2, price: 20 }
        ]
      },
      ...overrides
    },
    include: { items: true }
  });
}

// Usage
test('user can view their orders', async () => {
  const user = await createDbUser();
  const order1 = await createDbOrder(user.id);
  const order2 = await createDbOrder(user.id);

  const orders = await orderService.getByUser(user.id);

  expect(orders).toHaveLength(2);
  expect(orders.map(o => o.id)).toContain(order1.id);
  expect(orders.map(o => o.id)).toContain(order2.id);
});
```

### Cleanup Helper

```typescript
const createdIds: { table: string; id: string }[] = [];

export async function createDbUserTracked(
  overrides: Partial<User> = {}
): Promise<User> {
  const user = await createDbUser(overrides);
  createdIds.push({ table: 'users', id: user.id });
  return user;
}

export async function cleanupCreated() {
  // Delete in reverse order (respects foreign keys)
  for (const { table, id } of createdIds.reverse()) {
    await prisma[table].delete({ where: { id } }).catch(() => {});
  }
  createdIds.length = 0;
}

// In tests
afterEach(async () => {
  await cleanupCreated();
});
```

---

## Factory Organization

### File Structure

```
tests/
├── factories/
│   ├── index.ts              # Export all factories
│   ├── userFactory.ts
│   ├── orderFactory.ts
│   ├── productFactory.ts
│   ├── builders/
│   │   ├── UserBuilder.ts
│   │   └── OrderBuilder.ts
│   ├── scenarios/
│   │   ├── checkoutScenarios.ts
│   │   └── adminScenarios.ts
│   └── edgeCases/
│       ├── userEdgeCases.ts
│       └── orderEdgeCases.ts
```

### Central Export

```typescript
// tests/factories/index.ts
export * from './userFactory';
export * from './orderFactory';
export * from './productFactory';

export * from './builders/UserBuilder';
export * from './builders/OrderBuilder';

export { Scenarios } from './scenarios';
export { EdgeCases } from './edgeCases';
```

### Usage in Tests

```typescript
import {
  createUser,
  createOrder,
  UserBuilder,
  Scenarios,
  EdgeCases
} from '../factories';

describe('OrderService', () => {
  test('processes standard order', async () => {
    const user = createUser();
    const order = createOrder({ userId: user.id });
    // ...
  });

  test('handles edge case: unicode', async () => {
    const user = EdgeCases.Users.unicode();
    // ...
  });

  test('full checkout scenario', async () => {
    const { user, cart, address } = Scenarios.checkoutReady();
    // ...
  });
});
```
