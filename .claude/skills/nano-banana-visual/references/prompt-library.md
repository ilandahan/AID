# Nano Banana Pro Prompt Library

Ready-to-use prompts for AID visual artifacts.

---

## Discovery Phase

### Stakeholder Map
```
Create a professional stakeholder map for [PROJECT NAME].

Center: "[Project Name]" in blue circle

Inner Ring (Core Team):
- Product Manager (purple)
- Tech Lead (blue)
- Developers (green)
- QA (orange)

Middle Ring (Decision Makers):
- [Role 1] (gold star)
- [Role 2] (silver star)

Outer Ring (Users & External):
- End Users (person icons)
- External Systems (cloud icons)

Connections: Dotted lines showing relationships
Legend: Bottom right

Style: Modern infographic, soft gradients, professional
Background: White with subtle grid
```

### Problem Impact Infographic
```
Create an infographic showing the impact of [PROBLEM].

Title: "The Cost of [PROBLEM]"

Section 1 - Current State:
- Large number: "[METRIC]"
- Subtitle: "[Description]"

Section 2 - Pain Points (3 icons):
- Clock: "X hours wasted"
- Dollar: "$X lost monthly"
- User: "X% frustration"

Section 3 - Future State:
- Before → After arrow
- Red/orange for problems
- Green/blue for solutions

Style: Corporate presentation, data visualization focus
```

### Current vs Future State
```
Create a before/after comparison diagram.

Left - "Current State" (red header):
- Process 1: "[Manual step]"
- Process 2: "[Pain point]"
- Warning icons on each

Right - "Future State" (green header):
- Process 1: "[Automated]"
- Process 2: "[Improved]"
- Checkmarks on each

Center: Large arrow "Transformation"

Bottom: Metrics comparison table
| Metric | Current | Target |

Style: Split-screen, high contrast
```

---

## PRD Phase

### User Flow - Authentication
```
Create a user flow diagram for authentication.

Flow:
1. START: "App Launch"
2. DECISION: "Has Account?"
   - YES → Login Screen
   - NO → Registration
3. LOGIN:
   - Enter Credentials
   - DECISION: Valid?
     - YES → Dashboard (green)
     - NO → Error → Retry
4. REGISTRATION:
   - Enter Details
   - Verify Email
   - Dashboard (green)

Styling:
- Start/End: Rounded (gray/green)
- Actions: Rectangles (blue)
- Decisions: Diamonds (orange)
- Errors: Red borders
- Arrows with labels

Background: White
```

### User Flow - E-commerce Checkout
```
Create checkout flow diagram.

Screens (left to right):
1. "Cart" - Items, subtotal, Checkout button
2. "Shipping" - Address form, delivery options
3. "Payment" - Card details, billing
4. "Review" - Order summary, edit buttons
5. "Confirmation" - Order number, thank you

Each screen shows:
- Title at top
- Key UI elements
- Primary action button
- Progress indicator (1/5, 2/5...)

Error branches from Payment: "Failed" → Retry

Color: Primary blue (#3B82F6), success green (#22C55E)
```

### Feature Priority Matrix
```
Create a 2x2 priority matrix.

Axes:
- X: "Effort" (Low → High)
- Y: "Impact" (Low → High)

Quadrants:
- Top-Left: "Quick Wins" (Green)
  [Feature A], [Feature B]
- Top-Right: "Big Bets" (Blue)
  [Feature C]
- Bottom-Left: "Fill-ins" (Yellow)
  [Feature D]
- Bottom-Right: "Avoid" (Red)
  [Feature E]

Features as labeled dots
Clear axis labels with arrows
Legend for quadrant names

Style: Strategic planning visual, clean corporate
```

### Customer Journey Map
```
Create journey map for [PERSONA].

Header: Persona card - name, photo placeholder, attributes

Timeline Stages (horizontal):
1. DISCOVER | 2. EVALUATE | 3. PURCHASE | 4. ONBOARD | 5. USE | 6. ADVOCATE

Swimlanes per stage:
- Actions: What user does
- Touchpoints: Where interaction happens
- Emotions: Happy/Neutral/Sad faces
- Opportunities: Improvement ideas

Emotion Curve: Line graph overlay

Colors: Green=positive, Red=pain, Gray=neutral

Style: Service design template, horizontal scroll
```

---

## Tech Spec Phase

### Microservices Architecture
```
Create microservices architecture diagram.

CLIENT LAYER (top):
- Web App (React icon)
- Mobile App (phone icon)

API GATEWAY (below):
- Single "API Gateway" box

SERVICES (middle, horizontal):
- User Service (person icon)
- Order Service (cart icon)
- Payment Service (dollar icon)
- Notification Service (bell icon)

DATA LAYER (bottom):
- PostgreSQL
- Redis
- MongoDB

EXTERNAL (right side):
- Stripe
- SendGrid

Connections:
- Solid arrows: Sync calls
- Dashed arrows: Async/Events

Style: Cloud architecture aesthetic, consistent icons
```

### Data Flow Diagram
```
Create DFD for [PROCESS].

External Entities (squares):
- "Customer"
- "Payment Processor"

Processes (rounded rectangles):
- "1.0 Process Order"
- "2.0 Validate Payment"
- "3.0 Update Inventory"

Data Stores (open rectangles):
- "D1: Orders"
- "D2: Products"

Data Flows (labeled arrows):
- "Order Details" (Customer → Process)
- "Payment Info" (Process → Validate)

Style: Classic DFD notation, technical
```

### API Sequence Diagram
```
Create API sequence diagram.

Participants (left to right):
- Client
- API Gateway
- Auth Service
- Database

Sequence:
1. Client → Gateway: "POST /login"
2. Gateway → Auth: "Validate"
3. Auth → Database: "Query user"
4. Database → Auth: "User data"
5. Auth → Gateway: "JWT token"
6. Gateway → Client: "200 OK"

Style:
- Lifelines: Vertical dashed
- Messages: Horizontal arrows
- Activation boxes on lifelines
```

### Database ERD
```
Create ERD for [SYSTEM].

Entities:

USERS:
- id (PK)
- email (unique)
- password_hash
- created_at

ORGANIZATIONS:
- id (PK)
- name
- owner_id (FK → Users)

PROJECTS:
- id (PK)
- name
- organization_id (FK)
- created_by (FK)

Relationships:
- Users 1:N Organizations
- Organizations 1:N Projects

Style: Crow's foot notation, colors by domain
```

---

## Development Phase

### Dashboard Screen
```
Create SaaS dashboard screen.

Design Tokens:
- Primary: #3B82F6
- Background: #F9FAFB
- Surface: #FFFFFF
- Text: #111827
- Text Secondary: #6B7280
- Border: #E5E7EB
- Radius: 8px
- Font: Inter

Layout:

HEADER:
| Logo | -- Navigation -- | Search | Notifications | Avatar |

SIDEBAR:
| Dashboard (active)
| Analytics
| Users
| Settings

MAIN:
Row 1: 4 Stat Cards
- Total Users: 12,847 (+12%)
- Revenue: $48,352
- Sessions: 2,341
- Conversion: 3.2%

Row 2:
- 2/3: Line Chart (Weekly Trends)
- 1/3: Pie Chart (Traffic Sources)

Row 3: Recent Activity Table (5 rows)

Style: Clean SaaS, subtle shadows, 16px grid
```

### Form Screen
```
Create registration form screen.

Design Tokens: [Same as dashboard]

Layout:
CENTER CARD (480px max):

HEADER:
- Logo centered
- "Create Account" heading
- "Have account? Sign in" link

FORM:
- Full Name* [text]
- Email* [email] - show error state
- Password* [password with toggle]
- Confirm Password*
- [ ] Terms checkbox
- [Create Account] primary button

FOOTER:
- "Or continue with"
- [Google] [GitHub] buttons

States: Default, Focused (blue), Error (red)
```

### Settings Page
```
Create settings page with tabs.

Layout:

HEADER:
- "Settings" title
- Breadcrumb: Home > Settings

TABS:
| Profile | Security | Notifications | Billing |
(Profile active)

CONTENT:

Section: "Personal Information"
- Avatar upload circle
- First Name | Last Name [inputs]
- Email [disabled] + "Verified" badge

Section: "Preferences"
- Language [dropdown]
- Timezone [dropdown]

Section: "Danger Zone" (red border)
- "Delete Account" [danger button]

Actions: [Cancel] [Save Changes]

Style: Organized sections, 32px section gaps
```

### Empty State
```
Create empty state for "No Projects".

Center:
- Illustration: Folder with sparkles (simple, professional)
- Heading: "No projects yet"
- Subtext: "Create your first project to get started"
- [Create Project] primary button
- "Learn more" link

Style: Friendly but professional
Illustration: Line art with accent color
Layout: Vertically centered, 400px max width
```

### Data Table
```
Create data table with states.

HEADER ROW:
| [ ] | Name (sortable) | Email | Role | Status | Actions |

DATA (5 rows):
| [ ] | John Smith | john@ex.com | Admin | Active | ... |
| [x] | Jane Doe | jane@ex.com | Editor | Active | ... |
| [ ] | Bob Wilson | bob@ex.com | Viewer | Pending | ... |

Status badges:
- Active: Green
- Pending: Yellow
- Inactive: Gray

States: Hover, Selected (light blue)

FOOTER:
| Showing 1-5 of 124 | [<] [1] [2] [3] [...] [>] |

Style: Clean borders, proper padding
```

### Mobile Navigation
```
Create mobile app bottom navigation.

5 tabs, equal width:
1. Home (house icon) - active, blue
2. Search (magnifier icon)
3. Add (plus in circle) - larger, elevated
4. Notifications (bell icon) - with badge "3"
5. Profile (person icon)

Active state: Blue icon + label
Inactive: Gray icon only

Background: White with top shadow
Height: 56dp safe area aware

Style: iOS/Material hybrid, clean
```

### Loading States
```
Create loading state variations.

Show 4 states in 2x2 grid:

1. Skeleton Screen:
   - Gray animated shimmer
   - Card shape with text lines

2. Spinner:
   - Circular progress
   - "Loading..." text below

3. Progress Bar:
   - Horizontal bar at 60%
   - "Uploading file..." label

4. Placeholder:
   - Dotted border box
   - Cloud upload icon
   - "Drop files here"

Style: Consistent with design system
```

---

## Quick Customization

Replace these placeholders in any prompt:

| Variable | Replace With |
|----------|--------------|
| `[PROJECT NAME]` | Actual project name |
| `[FLOW NAME]` | Feature/flow name |
| `[PERSONA]` | User persona name |
| `[PROBLEM]` | Problem statement |
| `[SYSTEM]` | System name |
| `#3B82F6` | Your primary color |
| `Inter` | Your font family |

---

## Tips for Best Results

1. **Be specific** - Include exact colors, sizes, labels
2. **Use design tokens** - Maintain consistency across visuals
3. **Describe layout** - Left-to-right, grid, centered
4. **Specify style** - "Modern SaaS", "Technical diagram", "Infographic"
5. **Include states** - Hover, active, error, empty
