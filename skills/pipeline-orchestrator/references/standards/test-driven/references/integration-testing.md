# Integration Testing Guide

Real integration testing for databases, APIs, and external services.

---

## Database Integration Testing

### PostgreSQL with Transactions

```typescript
// tests/setup/database.ts
import { Pool } from 'pg';

let pool: Pool;

export async function setupTestDatabase() {
  pool = new Pool({
    connectionString: process.env.TEST_DATABASE_URL
  });

  // Run migrations
  await pool.query(fs.readFileSync('./migrations/schema.sql', 'utf8'));
}

export async function getTestConnection() {
  const client = await pool.connect();
  await client.query('BEGIN');
  return client;
}

export async function rollbackAndRelease(client: PoolClient) {
  await client.query('ROLLBACK');
  client.release();
}

// Usage in tests
describe('UserRepository', () => {
  let client: PoolClient;

  beforeEach(async () => {
    client = await getTestConnection();
  });

  afterEach(async () => {
    await rollbackAndRelease(client);
  });

  test('creates user in database', async () => {
    const repo = new UserRepository(client);

    const user = await repo.create({
      email: 'test@example.com',
      name: 'Test User'
    });

    // Verify in database
    const result = await client.query(
      'SELECT * FROM users WHERE id = $1',
      [user.id]
    );
    expect(result.rows[0].email).toBe('test@example.com');
  });
});
```

### MongoDB with Test Database

```typescript
import { MongoClient, Db } from 'mongodb';
import { MongoMemoryServer } from 'mongodb-memory-server';

let mongod: MongoMemoryServer;
let client: MongoClient;
let db: Db;

beforeAll(async () => {
  mongod = await MongoMemoryServer.create();
  const uri = mongod.getUri();
  client = new MongoClient(uri);
  await client.connect();
  db = client.db('test');
});

afterAll(async () => {
  await client.close();
  await mongod.stop();
});

beforeEach(async () => {
  // Clear all collections
  const collections = await db.collections();
  await Promise.all(collections.map(c => c.deleteMany({})));
});

test('inserts and retrieves document', async () => {
  const users = db.collection('users');

  await users.insertOne({
    email: 'test@example.com',
    name: 'Test User'
  });

  const user = await users.findOne({ email: 'test@example.com' });
  expect(user?.name).toBe('Test User');
});
```

### Prisma with Test Database

```typescript
// tests/setup/prisma.ts
import { PrismaClient } from '@prisma/client';
import { execSync } from 'child_process';

const prisma = new PrismaClient();

beforeAll(async () => {
  // Push schema to test database
  execSync('npx prisma db push', {
    env: {
      ...process.env,
      DATABASE_URL: process.env.TEST_DATABASE_URL
    }
  });
});

beforeEach(async () => {
  // Clean tables in correct order (respect foreign keys)
  await prisma.orderItem.deleteMany();
  await prisma.order.deleteMany();
  await prisma.user.deleteMany();
});

afterAll(async () => {
  await prisma.$disconnect();
});

export { prisma };

// Usage
test('creates user with Prisma', async () => {
  const user = await prisma.user.create({
    data: {
      email: 'test@example.com',
      name: 'Test User'
    }
  });

  expect(user.id).toBeDefined();

  const found = await prisma.user.findUnique({
    where: { id: user.id }
  });
  expect(found?.email).toBe('test@example.com');
});
```

---

## Redis Integration Testing

### Using Test Instance

```typescript
import Redis from 'ioredis';

let redis: Redis;

beforeAll(() => {
  redis = new Redis({
    host: process.env.TEST_REDIS_HOST || 'localhost',
    port: parseInt(process.env.TEST_REDIS_PORT || '6379'),
    db: 15 // Use separate database for tests
  });
});

afterAll(async () => {
  await redis.quit();
});

beforeEach(async () => {
  await redis.flushdb();
});

test('caches user data', async () => {
  const cache = new UserCache(redis);

  await cache.set('usr_123', { name: 'Test User' });

  const cached = await cache.get('usr_123');
  expect(cached?.name).toBe('Test User');
});

test('expires after TTL', async () => {
  jest.useFakeTimers();

  await redis.set('key', 'value', 'EX', 60);

  jest.advanceTimersByTime(61000);

  const value = await redis.get('key');
  expect(value).toBeNull();

  jest.useRealTimers();
});
```

### Using Docker Test Container

```typescript
// docker-compose.test.yml
/*
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"
*/

// Start before tests: docker-compose -f docker-compose.test.yml up -d
// Stop after tests: docker-compose -f docker-compose.test.yml down
```

---

## HTTP API Integration Testing

### Express with Supertest

```typescript
import request from 'supertest';
import { app } from '../src/app';

describe('Users API', () => {
  test('GET /users returns list', async () => {
    const response = await request(app)
      .get('/api/users')
      .set('Authorization', `Bearer ${testToken}`)
      .expect('Content-Type', /json/)
      .expect(200);

    expect(response.body).toEqual({
      users: expect.arrayContaining([
        expect.objectContaining({ id: expect.any(String) })
      ]),
      total: expect.any(Number)
    });
  });

  test('POST /users creates user', async () => {
    const response = await request(app)
      .post('/api/users')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        email: 'new@example.com',
        name: 'New User'
      })
      .expect(201);

    expect(response.body.user.email).toBe('new@example.com');
  });

  test('POST /users validates input', async () => {
    const response = await request(app)
      .post('/api/users')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        email: 'invalid-email' // Invalid
      })
      .expect(400);

    expect(response.body.errors).toContainEqual(
      expect.objectContaining({ field: 'email' })
    );
  });

  test('GET /users requires authentication', async () => {
    await request(app)
      .get('/api/users')
      .expect(401);
  });
});
```

### Next.js API Routes

```typescript
import { createMocks } from 'node-mocks-http';
import handler from '../pages/api/users';

describe('/api/users', () => {
  test('GET returns users', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      headers: { authorization: `Bearer ${testToken}` }
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(200);
    expect(JSON.parse(res._getData())).toHaveProperty('users');
  });

  test('POST creates user', async () => {
    const { req, res } = createMocks({
      method: 'POST',
      headers: { authorization: `Bearer ${adminToken}` },
      body: {
        email: 'new@example.com',
        name: 'New User'
      }
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(201);
  });
});
```

---

## External API Testing (Record/Replay)

### Using MSW (Mock Service Worker)

```typescript
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

const server = setupServer(
  // Default handlers
  http.get('https://api.stripe.com/v1/customers/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      email: 'customer@example.com'
    });
  }),

  http.post('https://api.stripe.com/v1/charges', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      id: 'ch_test123',
      amount: body.amount,
      status: 'succeeded'
    });
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('creates charge via Stripe', async () => {
  const result = await paymentService.charge({
    customerId: 'cus_123',
    amount: 1000
  });

  expect(result.status).toBe('succeeded');
});

// Override for specific test
test('handles Stripe error', async () => {
  server.use(
    http.post('https://api.stripe.com/v1/charges', () => {
      return HttpResponse.json(
        { error: { message: 'Card declined' } },
        { status: 402 }
      );
    })
  );

  await expect(paymentService.charge({ amount: 1000 }))
    .rejects.toThrow('Card declined');
});
```

### Using Nock

```typescript
import nock from 'nock';

beforeEach(() => {
  nock.cleanAll();
});

afterAll(() => {
  nock.restore();
});

test('fetches weather data', async () => {
  nock('https://api.weather.com')
    .get('/v1/current')
    .query({ city: 'London' })
    .reply(200, {
      temperature: 15,
      conditions: 'Cloudy'
    });

  const weather = await weatherService.getCurrent('London');

  expect(weather.temperature).toBe(15);
});

test('handles API timeout', async () => {
  nock('https://api.weather.com')
    .get('/v1/current')
    .query(true)
    .delay(5000) // Delay longer than timeout
    .reply(200, {});

  await expect(weatherService.getCurrent('London'))
    .rejects.toThrow('Request timeout');
});

// Record real requests (for creating fixtures)
test('record mode', async () => {
  nock.recorder.rec({
    output_objects: true,
    dont_print: true
  });

  await realApiCall();

  const recordings = nock.recorder.play();
  console.log(JSON.stringify(recordings, null, 2));
  // Save to fixtures file
});
```

---

## Message Queue Testing

### Bull/BullMQ

```typescript
import { Queue, Worker } from 'bullmq';
import IORedis from 'ioredis';

let connection: IORedis;
let queue: Queue;

beforeAll(() => {
  connection = new IORedis({
    host: 'localhost',
    port: 6379,
    db: 15,
    maxRetriesPerRequest: null
  });

  queue = new Queue('test-queue', { connection });
});

afterAll(async () => {
  await queue.close();
  await connection.quit();
});

beforeEach(async () => {
  await queue.drain();
});

test('processes job successfully', async () => {
  const processedJobs: any[] = [];

  const worker = new Worker(
    'test-queue',
    async (job) => {
      processedJobs.push(job.data);
      return { success: true };
    },
    { connection }
  );

  await queue.add('email', { to: 'test@example.com' });

  // Wait for processing
  await new Promise(resolve => setTimeout(resolve, 100));

  expect(processedJobs).toContainEqual({ to: 'test@example.com' });

  await worker.close();
});
```

---

## File System Testing

### Using Temp Directories

```typescript
import { mkdtemp, rm, writeFile, readFile } from 'fs/promises';
import { tmpdir } from 'os';
import { join } from 'path';

let testDir: string;

beforeEach(async () => {
  testDir = await mkdtemp(join(tmpdir(), 'test-'));
});

afterEach(async () => {
  await rm(testDir, { recursive: true, force: true });
});

test('writes and reads file', async () => {
  const filePath = join(testDir, 'test.txt');

  await fileService.write(filePath, 'Hello, World!');

  const content = await readFile(filePath, 'utf8');
  expect(content).toBe('Hello, World!');
});

test('handles missing directory', async () => {
  const filePath = join(testDir, 'nested/deep/file.txt');

  await fileService.write(filePath, 'Content');

  const content = await readFile(filePath, 'utf8');
  expect(content).toBe('Content');
});
```

---

## Docker-Based Integration Tests

### Docker Compose for Tests

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test_db
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
```

### Test Script

```json
// package.json
{
  "scripts": {
    "test:integration": "docker-compose -f docker-compose.test.yml up -d --wait && jest --config jest.integration.config.js && docker-compose -f docker-compose.test.yml down",
    "test:integration:watch": "docker-compose -f docker-compose.test.yml up -d --wait && jest --config jest.integration.config.js --watch"
  }
}
```

### Jest Integration Config

```javascript
// jest.integration.config.js
module.exports = {
  ...require('./jest.config'),
  testMatch: ['**/*.integration.test.ts'],
  setupFilesAfterEnv: ['./tests/setup/integration.ts'],
  testTimeout: 30000
};
```

---

## CI/CD Integration Tests

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      - run: npm run test:integration
        env:
          DATABASE_URL: postgres://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
```
