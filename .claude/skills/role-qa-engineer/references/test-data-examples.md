# Test Data Examples

Comprehensive examples of realistic test data for common scenarios.

---

## String Data

### Names

```typescript
const testNames = [
  // Basic
  'John Smith',
  'María García',
  
  // Unicode
  'José García-López',
  '日本語の名前',
  'Müller',
  'Øystein',
  'Αλέξανδρος',
  'محمد',
  '中文名字',
  
  // Special characters
  "O'Brien",
  'Mary-Jane',
  'van der Berg',
  'Dr. Smith Jr.',
  
  // Edge cases
  'A',                          // Single character
  'X'.repeat(100),              // Very long
  '',                           // Empty
  '   ',                        // Only whitespace
  '  Padded  ',                 // Leading/trailing whitespace
  'ALL CAPS',
  'all lower',
  
  // Potentially dangerous
  '<script>alert("xss")</script>',
  'Robert"); DROP TABLE users;--',
  '🎉 Emoji Name 🎊',
];
```

### Emails

```typescript
const testEmails = [
  // Valid formats
  'user@example.com',
  'user.name@example.com',
  'user+tag@example.com',
  'user@subdomain.example.com',
  
  // International
  'user@example.co.uk',
  'пользователь@example.com',    // Cyrillic
  'user@例え.jp',                 // IDN domain
  
  // Edge cases
  'a@b.co',                      // Minimal
  'very.long.email.address.that.goes.on@really-long-domain-name.com',
  'UPPER@CASE.COM',
  
  // Invalid (for error testing)
  '',
  'not-an-email',
  '@nodomain.com',
  'noat.com',
  'spaces in@email.com',
  'user@',
];
```

### Passwords

```typescript
const testPasswords = [
  // Valid
  'SecureP@ss123!',
  'CorrectHorseBatteryStaple',
  
  // Edge cases
  'a',                           // Too short
  'A'.repeat(1000),              // Very long
  '12345678',                    // No letters
  'password',                    // Common/weak
  'пароль123!',                  // Unicode
  'pass word',                   // Spaces
  '',                            // Empty
  
  // Special characters
  'P@$$w0rd!#$%^&*()',
  "It's a \"quoted\" password",
  'Pass\nWith\nNewlines',
];
```

---

## Numeric Data

### Integers

```typescript
const testIntegers = [
  // Normal
  0, 1, 42, 100, 1000,
  
  // Negative
  -1, -100, -1000,
  
  // Boundaries
  Number.MAX_SAFE_INTEGER,       // 9007199254740991
  Number.MIN_SAFE_INTEGER,       // -9007199254740991
  Number.MAX_VALUE,
  Number.MIN_VALUE,
  
  // Special
  Infinity,
  -Infinity,
  NaN,
  
  // Edge cases for parsing
  '42',                          // String that looks like number
  '42.0',
  '42abc',
  '',
];
```

### Decimals / Currency

```typescript
const testDecimals = [
  // Normal
  0.00, 1.50, 99.99, 1234.56,
  
  // Precision issues
  0.1 + 0.2,                     // 0.30000000000000004
  0.01, 0.001, 0.0001,
  
  // Edge cases
  0.005,                         // Rounding boundary
  -0.01,                         // Negative cents
  1000000.00,                    // Large amounts
  0.999999999,                   // Many decimals
  
  // Currency-specific
  '$100.00',                     // Formatted string
  '1,234.56',                    // With comma
  '1.234,56',                    // European format
];
```

---

## Date and Time Data

### Dates

```typescript
const testDates = [
  // Normal
  new Date('2024-01-15'),
  new Date('2024-06-30'),
  new Date('2024-12-31'),
  
  // Boundaries
  new Date('1970-01-01'),        // Unix epoch
  new Date('1969-12-31'),        // Before epoch
  new Date('2038-01-19'),        // Near Y2K38
  new Date('9999-12-31'),        // Far future
  
  // Special dates
  new Date('2024-02-29'),        // Leap year
  new Date('2023-02-28'),        // Non-leap year
  
  // DST transitions (US)
  new Date('2024-03-10T02:30:00'),  // Spring forward
  new Date('2024-11-03T01:30:00'),  // Fall back
  
  // Edge cases
  new Date('invalid'),           // Invalid date
  null,
  undefined,
  '',
  
  // String formats
  '2024-01-15',                  // ISO
  '01/15/2024',                  // US format
  '15/01/2024',                  // European format
  '15-Jan-2024',                 // Named month
];
```

### Times

```typescript
const testTimes = [
  '00:00:00',                    // Midnight
  '12:00:00',                    // Noon
  '23:59:59',                    // End of day
  '00:00:00.000',                // With milliseconds
  '23:59:59.999',
  
  // Edge cases
  '24:00:00',                    // Invalid? (depends on spec)
  '12:60:00',                    // Invalid minutes
  '-01:00:00',                   // Negative
];
```

### Timezones

```typescript
const testTimezones = [
  'UTC',
  'America/New_York',
  'Europe/London',
  'Asia/Tokyo',
  'Pacific/Auckland',            // +12/+13
  'Pacific/Samoa',               // -11
  'Asia/Kolkata',                // +5:30 (half hour)
  'Asia/Kathmandu',              // +5:45 (45 min offset)
];
```

---

## Collection Data

### Arrays

```typescript
const testArrays = [
  [],                            // Empty
  [1],                           // Single element
  [1, 2, 3],                     // Normal
  Array(1000).fill(0),           // Large
  [null, undefined, ''],         // Mixed nullish
  [1, 'two', { three: 3 }],      // Mixed types
  [[1, 2], [3, 4]],              // Nested
];
```

### Objects

```typescript
const testObjects = [
  {},                            // Empty
  { a: 1 },                      // Single property
  { a: 1, b: 2, c: 3 },          // Normal
  { nested: { deep: { value: 1 } } },  // Nested
  { 'special-key': 1 },          // Special characters in key
  { '': 1 },                     // Empty string key
  { [Symbol('key')]: 1 },        // Symbol key
  null,                          // Null object
];
```

---

## File Data

### File Names

```typescript
const testFileNames = [
  // Normal
  'document.pdf',
  'image.jpg',
  'report-2024.xlsx',
  
  // Unicode
  'документ.pdf',
  '文件.txt',
  
  // Special characters
  'file with spaces.txt',
  'file-with-dashes.txt',
  'file_with_underscores.txt',
  'file.multiple.dots.txt',
  
  // Edge cases
  '.hidden',
  'no-extension',
  'UPPERCASE.TXT',
  'a',                           // Single char
  'x'.repeat(255),               // Max length
  
  // Dangerous
  '../../../etc/passwd',         // Path traversal
  'file.txt\x00.jpg',            // Null byte
  'CON',                         // Windows reserved (Windows)
  'file|name.txt',               // Invalid chars (Windows)
];
```

### File Sizes

```typescript
const testFileSizes = [
  0,                             // Empty file
  1,                             // 1 byte
  1024,                          // 1 KB
  1024 * 1024,                   // 1 MB
  1024 * 1024 * 10,              // 10 MB
  1024 * 1024 * 100,             // 100 MB (large)
  1024 * 1024 * 1024,            // 1 GB (very large)
  -1,                            // Invalid
];
```

---

## API Data

### HTTP Status Codes

```typescript
const testStatusCodes = {
  success: [200, 201, 204],
  redirect: [301, 302, 304],
  clientError: [400, 401, 403, 404, 409, 422, 429],
  serverError: [500, 502, 503, 504],
  edge: [0, 999, -1],            // Invalid
};
```

### Pagination

```typescript
const testPagination = [
  { page: 1, limit: 10 },        // Normal first page
  { page: 1, limit: 100 },       // Large page
  { page: 100, limit: 10 },      // Deep pagination
  { page: 0, limit: 10 },        // Zero page
  { page: -1, limit: 10 },       // Negative page
  { page: 1, limit: 0 },         // Zero limit
  { page: 1, limit: -1 },        // Negative limit
  { page: 1, limit: 10000 },     // Huge limit
];
```

---

## Factory Pattern

```typescript
// Base factory
function createTestUser(overrides: Partial<User> = {}): User {
  return {
    id: crypto.randomUUID(),
    name: 'Test User',
    email: `test.${Date.now()}@example.com`,
    createdAt: new Date(),
    ...overrides,
  };
}

// Edge case variants
const userEdgeCases = {
  unicode: () => createTestUser({ name: 'José García-López' }),
  minimal: () => createTestUser({ name: 'A', email: 'a@b.co' }),
  long: () => createTestUser({ name: 'X'.repeat(100) }),
  empty: () => createTestUser({ name: '', email: '' }),
  special: () => createTestUser({ name: "O'Brien <script>" }),
};

// Batch generator
function createTestUsers(count: number): User[] {
  return Array.from({ length: count }, (_, i) => 
    createTestUser({ name: `User ${i + 1}` })
  );
}
```

---

## Quick Reference

| Category | Normal | Edge Cases | Invalid |
|----------|--------|------------|---------|
| Strings | "hello" | "", "A", long, unicode | null, undefined |
| Numbers | 42 | 0, -1, MAX_INT, decimals | NaN, Infinity, "42" |
| Dates | today | epoch, leap year, DST | "invalid", null |
| Arrays | [1,2,3] | [], [1], large, nested | null, undefined |
| Objects | {a:1} | {}, nested, special keys | null |
| Files | doc.pdf | .hidden, long, unicode | path traversal |
