# Security Vulnerability Patterns

Extended examples by language and framework.

---

## Injection Vulnerabilities

### SQL Injection

```typescript
// ❌ VULNERABLE: String concatenation
const query = `SELECT * FROM users WHERE id = ${userId}`;
const query = "SELECT * FROM users WHERE id = " + userId;
const query = `SELECT * FROM users WHERE name = '${name}'`;

// ✅ SAFE: Parameterized queries
// Node.js (mysql2)
const [rows] = await db.execute('SELECT * FROM users WHERE id = ?', [userId]);

// Node.js (pg)
const result = await client.query('SELECT * FROM users WHERE id = $1', [userId]);

// Prisma
const user = await prisma.user.findUnique({ where: { id: userId } });

// TypeORM
const user = await userRepository.findOne({ where: { id: userId } });
```

```python
# ❌ VULNERABLE
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.execute("SELECT * FROM users WHERE id = " + user_id)

# ✅ SAFE: Parameterized
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# SQLAlchemy
user = session.query(User).filter(User.id == user_id).first()
```

### NoSQL Injection

```typescript
// ❌ VULNERABLE: Direct object from user input
const user = await db.users.findOne({ username: req.body.username });
// Attack: { "username": { "$gt": "" } } returns first user

// ✅ SAFE: Validate/sanitize input type
const username = String(req.body.username);
const user = await db.users.findOne({ username });

// ✅ SAFE: Use schema validation (Mongoose)
const UserSchema = new Schema({
  username: { type: String, required: true }
});
```

### Command Injection

```typescript
// ❌ VULNERABLE: Shell command with user input
exec(`convert ${filename} output.png`);
exec('ls ' + userPath);

// ✅ SAFE: Use spawn with array args (no shell)
spawn('convert', [filename, 'output.png']);

// ✅ SAFE: Use built-in APIs instead of shell
import { readdir } from 'fs/promises';
const files = await readdir(userPath);
```

```python
# ❌ VULNERABLE
os.system(f"convert {filename} output.png")
subprocess.call("ls " + user_path, shell=True)

# ✅ SAFE: Use array args, no shell
subprocess.run(['convert', filename, 'output.png'], shell=False)

# ✅ SAFE: Use built-in
os.listdir(user_path)
```

---

## XSS (Cross-Site Scripting)

### DOM-Based XSS

```typescript
// ❌ VULNERABLE: innerHTML with user data
element.innerHTML = userComment;
document.write(userData);

// ❌ VULNERABLE: React dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: userContent }} />

// ✅ SAFE: textContent (no HTML parsing)
element.textContent = userComment;

// ✅ SAFE: React auto-escapes in JSX
<div>{userContent}</div>

// ✅ SAFE: If HTML needed, use sanitizer
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userComment);
```

### URL-Based XSS

```typescript
// ❌ VULNERABLE: Unvalidated redirect
window.location = req.query.redirect;

// ❌ VULNERABLE: javascript: URLs
<a href={userProvidedUrl}>Link</a>

// ✅ SAFE: Validate URL
const url = new URL(redirectUrl);
if (url.origin === window.location.origin) {
  window.location = url.href;
}

// ✅ SAFE: Check protocol
const safeUrl = userUrl.startsWith('https://') ? userUrl : '#';
```

---

## Authentication & Session

### Weak Password Storage

```typescript
// ❌ VULNERABLE: Plain text or weak hash
const hash = md5(password);
const hash = sha1(password);
db.save({ password: password }); // Plain text!

// ✅ SAFE: bcrypt with sufficient rounds
import bcrypt from 'bcrypt';
const hash = await bcrypt.hash(password, 12);
const isValid = await bcrypt.compare(password, hash);

// ✅ SAFE: Argon2 (even better)
import argon2 from 'argon2';
const hash = await argon2.hash(password);
```

### Weak Session Tokens

```typescript
// ❌ VULNERABLE: Predictable tokens
const token = Date.now().toString();
const token = Math.random().toString();
const token = `user_${userId}`;

// ✅ SAFE: Cryptographically random
import crypto from 'crypto';
const token = crypto.randomBytes(32).toString('hex');
const token = crypto.randomUUID();
```

### Missing Auth Checks

```typescript
// ❌ VULNERABLE: No auth check
app.get('/api/admin/users', async (req, res) => {
  const users = await getUsers();
  res.json(users);
});

// ✅ SAFE: Auth middleware
app.get('/api/admin/users',
  authMiddleware,           // Verify logged in
  requireRole('admin'),     // Verify role
  async (req, res) => {
    const users = await getUsers();
    res.json(users);
  }
);
```

---

## Sensitive Data Exposure

### Secrets in Code

```typescript
// ❌ VULNERABLE: Hardcoded secrets
const apiKey = 'sk-1234567890abcdef';
const dbPassword = 'supersecret123';
const jwtSecret = 'my-jwt-secret';

// ✅ SAFE: Environment variables
const apiKey = process.env.API_KEY;
const dbPassword = process.env.DB_PASSWORD;
const jwtSecret = process.env.JWT_SECRET;

// ✅ SAFE: Fail if missing
const apiKey = process.env.API_KEY;
if (!apiKey) throw new Error('API_KEY required');
```

### Secrets in Logs

```typescript
// ❌ VULNERABLE: Logging sensitive data
console.log('User login:', { email, password });
logger.info('Request:', req.body); // May contain passwords
logger.error('Auth failed:', { token: authToken });

// ✅ SAFE: Redact sensitive fields
console.log('User login:', { email, password: '[REDACTED]' });
logger.info('Request:', sanitizeBody(req.body));

// ✅ SAFE: Use structured logging with filters
const sanitize = (obj) => {
  const sensitive = ['password', 'token', 'secret', 'key'];
  return Object.fromEntries(
    Object.entries(obj).map(([k, v]) =>
      [k, sensitive.some(s => k.toLowerCase().includes(s)) ? '[REDACTED]' : v]
    )
  );
};
```

### Error Details to Users

```typescript
// ❌ VULNERABLE: Stack traces to client
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.stack });
});

// ✅ SAFE: Generic message, log details
app.use((err, req, res, next) => {
  logger.error('Server error:', err); // Full details in logs
  res.status(500).json({ error: 'Internal server error' }); // Generic to user
});
```

---

## Access Control

### IDOR (Insecure Direct Object Reference)

```typescript
// ❌ VULNERABLE: No ownership check
app.get('/api/documents/:id', async (req, res) => {
  const doc = await Document.findById(req.params.id);
  res.json(doc); // Anyone can access any document!
});

// ✅ SAFE: Verify ownership
app.get('/api/documents/:id', async (req, res) => {
  const doc = await Document.findOne({
    _id: req.params.id,
    userId: req.user.id  // Only owner's docs
  });
  if (!doc) return res.status(404).json({ error: 'Not found' });
  res.json(doc);
});
```

### Missing Role Checks

```typescript
// ❌ VULNERABLE: Any logged-in user can access
app.delete('/api/users/:id', authMiddleware, async (req, res) => {
  await User.delete(req.params.id);
});

// ✅ SAFE: Role-based access
app.delete('/api/users/:id',
  authMiddleware,
  requireRole('admin'),
  async (req, res) => {
    await User.delete(req.params.id);
  }
);
```

---

## File Upload Vulnerabilities

```typescript
// ❌ VULNERABLE: No validation
app.post('/upload', upload.single('file'), (req, res) => {
  // Accepts any file type, any size
});

// ✅ SAFE: Validate type, size, and sanitize name
const upload = multer({
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB max
  fileFilter: (req, file, cb) => {
    const allowed = ['image/jpeg', 'image/png', 'image/gif'];
    if (allowed.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type'));
    }
  },
  storage: multer.diskStorage({
    filename: (req, file, cb) => {
      // Don't use original name (could be malicious)
      const safeName = crypto.randomUUID() + path.extname(file.originalname);
      cb(null, safeName);
    }
  })
});
```

---

## CORS Misconfiguration

```typescript
// ❌ VULNERABLE: Allow all origins
app.use(cors({ origin: '*' }));
app.use(cors({ origin: true }));

// ❌ VULNERABLE: Reflect origin header
app.use(cors({ origin: req.headers.origin }));

// ✅ SAFE: Whitelist specific origins
app.use(cors({
  origin: ['https://myapp.com', 'https://admin.myapp.com'],
  credentials: true
}));
```

---

## Quick Reference: Red Flags

| Pattern | Vulnerability |
|---------|--------------|
| `${variable}` in SQL | SQL Injection |
| `innerHTML =` | XSS |
| `dangerouslySetInnerHTML` | XSS |
| `eval()` | Code Injection |
| `exec()` with string | Command Injection |
| `md5(password)` | Weak Hashing |
| `Math.random()` for tokens | Weak Randomness |
| `cors({ origin: '*' })` | CORS Misconfiguration |
| No auth middleware | Missing Authentication |
| `findById(req.params.id)` alone | IDOR |
| `console.log(password)` | Secret Exposure |
| `res.json(err.stack)` | Info Leakage |
