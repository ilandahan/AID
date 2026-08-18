# Storybook Component Preview

Manage Storybook preview for extracted Figma components.

## Overview

This command helps you preview React components in Storybook without duplicating files. It uses **symlinks** to connect your component's actual location to the Storybook preview server.

## Usage

When user mentions they want to preview a component in Storybook, or explicitly uses this command:

### Add Component to Storybook
```
/storybook add <path-to-component>
```

**Example:**
```
/storybook add ./my-project/src/components/Button
```

**What it does:**
1. Validates the component folder has required files (.tsx, .stories.tsx)
2. Detects the atomic level from the component header (atom/molecule/organism)
3. Creates a symlink from `storybook-preview/src/components/{level}/{name}/` → user's path
4. Offers to start Storybook server if not running

### Start Storybook Server
```
/storybook start
```

Starts the Storybook dev server on port 6006.

### Stop Storybook Server
```
/storybook stop
```

Stops the running Storybook process.

### List Linked Components
```
/storybook list
```

Shows all components currently linked to Storybook.

### Remove Component from Storybook
```
/storybook remove <component-name>
```

Removes the symlink (does NOT delete the original files).

---

## Implementation Instructions for Claude

When this command is invoked:

### For `/storybook add <path>`:

1. **Validate the path exists:**
   ```bash
   # Check if directory exists
   dir "<path>" /b
   ```

2. **Check for required files:**
   - Must have a `.tsx` file (not just `.stories.tsx`)
   - Must have a `.stories.tsx` file
   ```bash
   dir "<path>\*.tsx" /b
   ```

3. **Detect atomic level** by reading the component file header:
   ```
   Look for: "Atomic Level: Atom|Molecule|Organism|Template|Page"
   Default to "molecule" if not found
   ```

4. **Create symlink (Windows junction):**
   ```bash
   # Create parent directory if needed
   if not exist "storybook-preview\src\components\{level}s" mkdir "storybook-preview\src\components\{level}s"

   # Create junction (Windows symlink for directories)
   mklink /J "storybook-preview\src\components\{level}s\{ComponentName}" "<absolute-path>"
   ```

   For Mac/Linux:
   ```bash
   mkdir -p storybook-preview/src/components/{level}s
   ln -s "<absolute-path>" "storybook-preview/src/components/{level}s/{ComponentName}"
   ```

5. **Offer to start Storybook:**
   Ask user if they want to start Storybook to preview the component.

### For `/storybook start`:

```bash
# Windows
cd storybook-preview && npm run storybook

# Mac/Linux
cd storybook-preview && npm run storybook
```

Run in background so user can continue working.

### For `/storybook stop`:

Find and kill the Storybook process:
```bash
# Windows
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *storybook*"

# Or find by port
netstat -ano | findstr :6006
taskkill /F /PID <pid>
```

### For `/storybook list`:

List all symlinks in the components directories:
```bash
# Windows
dir storybook-preview\src\components\*s\* /AL /B

# Mac/Linux
find storybook-preview/src/components -type l
```

### For `/storybook remove <name>`:

Remove the symlink:
```bash
# Windows (junction)
rmdir "storybook-preview\src\components\*s\{name}"

# Mac/Linux
rm "storybook-preview/src/components/*s/{name}"
```

---

## Conversational Handling

When user says things like:
- "I extracted the Button component" → Offer to add to Storybook
- "Can I preview this in Storybook?" → Guide them through /storybook add
- "Show me the component" → Start Storybook and provide URL
- "Add Button to Storybook" → Run /storybook add with detected path

**Example Response Flow:**

```
User: "I extracted the Button component to my-app/src/components/Button"

Claude: I can add this to Storybook for preview. Would you like me to:
1. Link the component to Storybook
2. Start the Storybook server

[Yes, link and start] [Just link] [No thanks]

---

User: [Yes, link and start]

Claude:
✓ Detected atomic level: molecule (from component header)
✓ Created symlink: storybook-preview/src/components/molecules/Button/
✓ Starting Storybook server on port 6006...

Your Button component is now available at:
http://localhost:6006/?path=/docs/molecules-button--docs

The original files remain at: my-app/src/components/Button/
Any edits there will reflect immediately in Storybook (hot reload).
```

---

## No Duplication Guarantee

This command uses **symlinks** (Windows: junctions, Mac/Linux: symbolic links) which means:

- ✅ Files exist in ONE place only (user's project)
- ✅ Storybook reads via the symlink
- ✅ Edits in original location reflect immediately
- ✅ Removing from Storybook doesn't delete original files

```
User's Project                      Storybook Preview
─────────────────                   ──────────────────
my-app/
└── src/
    └── components/
        └── Button/          ←──────  storybook-preview/
            ├── Button.tsx            └── src/components/
            ├── Button.stories.tsx        └── molecules/
            ├── Button.module.css             └── Button/ (symlink)
            └── index.ts

Only ONE copy exists!
```

---

## Prerequisites

- Storybook must be installed (run during AID installation)
- Component must have `.stories.tsx` file (generated by Figma plugin)
- On Windows: No admin rights needed for junctions
