# Page Composition Patterns

## Layout Patterns

### Grid-Based Layout
```tsx
/**
 * Standard grid layout from Figma
 * @figma Extracted grid: 12 columns, 24px gap
 */
import styles from './GridLayout.module.css';

export const GridLayout = ({ children }) => (
  <div className={styles.grid}>
    {children}
  </div>
);
```

```css
/* GridLayout.module.css */
.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--spacing-6);  /* 24px from tokens */
  padding: var(--spacing-8);
}

/* Responsive - from Figma breakpoints */
@media (max-width: 1024px) {
  .grid {
    grid-template-columns: repeat(8, 1fr);
    gap: var(--spacing-4);
  }
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-3);
  }
}
```

### Dashboard Layout
```tsx
/**
 * Dashboard with sidebar + main content
 * @figma Sidebar: 280px, Main: fluid
 */
import { Sidebar } from '@/organisms/Sidebar';
import { Header } from '@/organisms/Header';
import styles from './DashboardLayout.module.css';

export const DashboardLayout = ({ children }) => (
  <div className={styles.dashboard}>
    <Sidebar className={styles.sidebar} />
    <div className={styles.main}>
      <Header className={styles.header} />
      <main className={styles.content}>
        {children}
      </main>
    </div>
  </div>
);
```

```css
.dashboard {
  display: grid;
  grid-template-columns: 280px 1fr;
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
}

.main {
  display: flex;
  flex-direction: column;
}

.header {
  position: sticky;
  top: 0;
  z-index: var(--z-header);
}

.content {
  flex: 1;
  padding: var(--spacing-6);
}

@media (max-width: 1024px) {
  .dashboard {
    grid-template-columns: 1fr;
  }
  .sidebar {
    display: none;  /* Mobile: hamburger menu */
  }
}
```

### Split View Layout
```tsx
/**
 * Master-detail split view
 * @figma Left panel: 320px, Right: fluid
 */
export const SplitLayout = ({ list, detail }) => (
  <div className={styles.split}>
    <aside className={styles.list}>{list}</aside>
    <main className={styles.detail}>{detail}</main>
  </div>
);
```

## Component Slot Patterns

### Card with Slots
```tsx
/**
 * Card component with named slots
 */
import { Card } from '@/molecules/Card';

// Usage
<Card>
  <Card.Header>
    <h3>Title</h3>
    <Badge>Status</Badge>
  </Card.Header>
  <Card.Body>
    Content here
  </Card.Body>
  <Card.Footer>
    <Button>Action</Button>
  </Card.Footer>
</Card>
```

### Modal with Slots
```tsx
/**
 * Modal composition
 */
import { Modal } from '@/organisms/Modal';

<Modal isOpen={isOpen} onClose={onClose}>
  <Modal.Header>
    <Modal.Title>Confirm Action</Modal.Title>
  </Modal.Header>
  <Modal.Body>
    Are you sure?
  </Modal.Body>
  <Modal.Actions>
    <Button variant="secondary" onClick={onClose}>Cancel</Button>
    <Button variant="primary" onClick={onConfirm}>Confirm</Button>
  </Modal.Actions>
</Modal>
```

## Responsive Patterns

### Mobile-First
```css
/* Base: Mobile */
.container {
  padding: var(--spacing-4);
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    padding: var(--spacing-6);
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    padding: var(--spacing-8);
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

### Container Queries
```css
.card-grid {
  container-type: inline-size;
}

@container (min-width: 600px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@container (min-width: 900px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## Data Fetching Patterns

### Page with Data
```tsx
/**
 * Page component with data fetching
 */
export const UsersPage = () => {
  const { data, isLoading, error } = useUsers();

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} />;

  return (
    <PageLayout title="Users">
      <DataTable
        columns={userColumns}
        data={data}
      />
    </PageLayout>
  );
};
```

### Suspense Pattern
```tsx
/**
 * Using Suspense for data loading
 */
export const DashboardPage = () => (
  <PageLayout>
    <Suspense fallback={<StatsSkeleton />}>
      <StatsSection />
    </Suspense>
    <Suspense fallback={<ChartSkeleton />}>
      <ChartsSection />
    </Suspense>
    <Suspense fallback={<TableSkeleton />}>
      <RecentActivity />
    </Suspense>
  </PageLayout>
);
```

## Import Organization

```tsx
// 1. External libraries
import { useState, useEffect } from 'react';

// 2. Design system components (by hierarchy)
import { PageLayout } from '@/templates/PageLayout';
import { DataTable, Modal } from '@/organisms';
import { Card, Form } from '@/molecules';
import { Button, Input, Badge } from '@/atoms';

// 3. Hooks and utilities
import { useUsers } from '@/hooks/useUsers';
import { formatDate } from '@/utils/format';

// 4. Local styles
import styles from './UsersPage.module.css';

// 5. Types
import type { User } from '@/types';
```
