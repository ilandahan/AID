# Root Cause Tracing Guide

When bugs appear deep in the call stack, your instinct is to fix where the error manifests. That's treating a symptom, not the disease.

**Core principle**: Trace backward to find where bad data originates. Fix at the source.

---

## The Technique

```
Error appears here (symptom)
        ↑
Who called this with bad data?
        ↑
Who called THAT with bad data?
        ↑
Keep going until you find the SOURCE
        ↓
Fix at source, not at symptom
```

---

## Step-by-Step Process

### Step 1: Identify the Symptom

Note exactly what's wrong:
- What value is incorrect?
- What was expected?
- Where does the error appear?

```typescript
// Error in WorktreeManager.gitInit()
// Expected: '/tmp/project-abc/workspace'
// Actual: '' (empty string)
// Result: git init runs in process.cwd() instead of temp dir
```

### Step 2: Find the Caller

Look at the stack trace or add logging to find who called with bad data:

```typescript
async gitInit(directory: string) {
  console.log('gitInit called with:', { 
    directory, 
    caller: new Error().stack 
  });
  // ...
}
```

Output:
```
gitInit called with: { directory: '' }
Stack:
  at WorktreeManager.gitInit (worktree-manager.ts:45)
  at WorkspaceManager.createWorkspace (workspace-manager.ts:23)  ← CALLER
  at Project.create (project.ts:12)
  at test.spec.ts:8
```

### Step 3: Trace Up the Chain

Now investigate `WorkspaceManager.createWorkspace`:

```typescript
async createWorkspace(projectDir: string) {
  console.log('createWorkspace called with:', { projectDir });
  // ...
  await this.worktreeManager.gitInit(projectDir); // Passes empty string!
}
```

Output:
```
createWorkspace called with: { projectDir: '' }
```

The empty string came from the caller. Continue tracing up.

### Step 4: Find the Source

```typescript
// In Project.create()
static create(name: string, directory: string) {
  console.log('Project.create called with:', { name, directory });
  // ...
}
```

Output:
```
Project.create called with: { name: 'test-project', directory: '' }
```

Now check the test:

```typescript
// test.spec.ts
it('creates a project', async () => {
  const project = await Project.create('test-project', ''); // ← SOURCE!
});
```

**Found it!** The test passes empty string for directory.

### Step 5: Fix at Source

**Wrong approach** (fixing symptom):
```typescript
// In gitInit - checking for empty
async gitInit(directory: string) {
  if (!directory) {
    directory = process.cwd(); // WRONG: hides the bug
  }
}
```

**Right approach** (fixing source + defense-in-depth):
```typescript
// Layer 1: Fix the test
it('creates a project', async () => {
  const tempDir = await createTempDir();
  const project = await Project.create('test-project', tempDir);
});

// Layer 2: Add validation at entry point
static create(name: string, directory: string) {
  if (!directory?.trim()) {
    throw new Error('directory is required');
  }
}

// Layer 3: Add validation at each layer (defense-in-depth)
async createWorkspace(projectDir: string) {
  if (!projectDir) {
    throw new Error('projectDir required for workspace');
  }
}
```

---

## Real-World Example

### The Bug

```
Error: ENOENT: no such file or directory, open '/app/.git/config'
  at Object.openSync (fs.js:498:3)
  at GitRepository.getConfig (git-repository.ts:156)
```

### Initial (Wrong) Instinct

"The .git directory doesn't exist. Let me add a check in getConfig."

```typescript
// WRONG: Treating symptom
getConfig() {
  if (!existsSync(this.gitDir)) {
    return {}; // Silently return empty - hides the real bug
  }
}
```

### Trace Backward

```
getConfig()
  ↑ called by: Repository.init()
  ↑ called by: Project.setup()
  ↑ called by: test setup

// Add logging at each level:
Repository.init: { repoPath: '/app' }  // Expected: '/tmp/test-123'
Project.setup: { projectDir: '/app' }  // Wrong dir passed!
test setup: Project.setup(process.cwd()) // BUG: Using cwd instead of temp
```

### Root Cause

Test was using `process.cwd()` instead of creating a temp directory.

### Proper Fix

```typescript
// Fix at source (test)
beforeEach(async () => {
  testDir = await fs.mkdtemp(path.join(os.tmpdir(), 'test-'));
  project = await Project.setup(testDir);
});

afterEach(async () => {
  await fs.rm(testDir, { recursive: true });
});

// Add defense-in-depth (validation at multiple layers)
class Project {
  static async setup(directory: string) {
    if (!directory || directory === process.cwd()) {
      throw new Error('Must provide explicit project directory, not cwd');
    }
  }
}
```

---

## Quick Reference

| Step | Action | Question to Ask |
|------|--------|-----------------|
| 1 | Identify symptom | What's the bad value? Where does error appear? |
| 2 | Find caller | Who passed this bad value? |
| 3 | Trace up | Who passed it to THEM? |
| 4 | Find source | Where did bad value originate? |
| 5 | Fix at source | How do we prevent this at origin? |
| 6 | Defense-in-depth | What validation stops this at each layer? |

---

## Anti-Patterns

### ❌ Fixing at Symptom Location

```typescript
// Deep in call stack
function processData(data) {
  if (!data) data = getDefaultData(); // Hides upstream bug
}
```

### ❌ Adding Defensive Defaults

```typescript
// Silently "fixing" bad input
function createUser(name = 'Anonymous') { // Who's passing empty name?
}
```

### ❌ Swallowing Errors

```typescript
// Hiding the problem
try {
  await riskyOperation();
} catch (e) {
  // ignore - it sometimes fails
}
```

### ✅ Validate and Fail Fast

```typescript
// Make bugs visible
function createUser(name: string) {
  if (!name?.trim()) {
    throw new Error('name is required - check caller');
  }
}
```

---

## Tools for Tracing

### Stack Trace Logging

```typescript
function suspiciousFunction(data: unknown) {
  console.log('Called with:', {
    data,
    stack: new Error().stack?.split('\n').slice(1, 5),
    timestamp: Date.now(),
  });
}
```

### Git Bisect for Regressions

```bash
# Find which commit introduced the bug
git bisect start
git bisect bad HEAD
git bisect good v1.2.3
# Git will binary search to find the bad commit
```

### Conditional Breakpoints

In debugger, set breakpoint with condition:
```
directory === '' || directory === undefined
```

This pauses only when bad data flows through.

---

## Summary

1. **Don't fix where error appears** - that's the symptom
2. **Trace backward** through call stack
3. **Find the source** of bad data
4. **Fix at source** to prevent the bug
5. **Add defense-in-depth** at each layer
6. **Validate and fail fast** instead of defensive defaults
