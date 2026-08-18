# Architecture Diagram Templates

## System Context Diagram

```mermaid
C4Context
  title System Context - [System Name]

  Person(user, "User", "End user of the system")
  System(system, "Our System", "Main system being designed")
  System_Ext(ext1, "External System", "Third-party integration")
  System_Ext(ext2, "Email Service", "Notification delivery")

  Rel(user, system, "Uses", "HTTPS")
  Rel(system, ext1, "Fetches data", "REST API")
  Rel(system, ext2, "Sends emails", "SMTP")
```

## Container Diagram

```mermaid
C4Container
  title Container Diagram - [System Name]

  Person(user, "User")

  Container_Boundary(system, "System") {
    Container(web, "Web App", "React", "User interface")
    Container(api, "API", "Node.js", "Business logic")
    Container(worker, "Worker", "Node.js", "Background jobs")
    ContainerDb(db, "Database", "PostgreSQL", "Data storage")
    ContainerDb(cache, "Cache", "Redis", "Session & cache")
    ContainerDb(queue, "Queue", "RabbitMQ", "Job queue")
  }

  Rel(user, web, "Uses", "HTTPS")
  Rel(web, api, "Calls", "REST/JSON")
  Rel(api, db, "Reads/Writes", "SQL")
  Rel(api, cache, "Caches", "Redis protocol")
  Rel(api, queue, "Publishes", "AMQP")
  Rel(worker, queue, "Consumes", "AMQP")
  Rel(worker, db, "Reads/Writes", "SQL")
```

## Component Diagram

```mermaid
C4Component
  title Component Diagram - API Service

  Container_Boundary(api, "API Service") {
    Component(router, "Router", "Express", "HTTP routing")
    Component(auth, "Auth Module", "Passport", "Authentication")
    Component(users, "Users Module", "Service", "User management")
    Component(orders, "Orders Module", "Service", "Order processing")
    Component(repo, "Repository Layer", "TypeORM", "Data access")
  }

  Rel(router, auth, "Uses")
  Rel(router, users, "Routes to")
  Rel(router, orders, "Routes to")
  Rel(users, repo, "Uses")
  Rel(orders, repo, "Uses")
```

## Sequence Diagram

```mermaid
sequenceDiagram
  participant U as User
  participant W as Web App
  participant A as API
  participant D as Database
  participant C as Cache

  U->>W: Login request
  W->>A: POST /auth/login
  A->>D: Query user
  D-->>A: User data
  A->>A: Validate password
  A->>C: Store session
  A-->>W: JWT token
  W-->>U: Redirect to dashboard
```

## Data Flow Diagram

```mermaid
flowchart LR
  subgraph Input
    A[User Request]
    B[Webhook]
    C[Scheduled Job]
  end

  subgraph Processing
    D[API Gateway]
    E[Business Logic]
    F[Validation]
  end

  subgraph Storage
    G[(Database)]
    H[(Cache)]
    I[(File Storage)]
  end

  subgraph Output
    J[Response]
    K[Notification]
    L[Report]
  end

  A --> D --> F --> E
  B --> D
  C --> E
  E --> G
  E --> H
  E --> I
  E --> J
  E --> K
  E --> L
```

## State Machine Diagram

```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> Review: Submit
  Review --> Draft: Reject
  Review --> Approved: Approve
  Approved --> Published: Publish
  Published --> Archived: Archive
  Archived --> [*]

  Draft --> [*]: Delete
  Review --> [*]: Delete
```

## Entity Relationship Diagram

```mermaid
erDiagram
  USER ||--o{ ORDER : places
  USER {
    uuid id PK
    string email UK
    string name
    datetime created_at
  }

  ORDER ||--|{ ORDER_ITEM : contains
  ORDER {
    uuid id PK
    uuid user_id FK
    string status
    int total_cents
    datetime created_at
  }

  ORDER_ITEM }|--|| PRODUCT : references
  ORDER_ITEM {
    uuid id PK
    uuid order_id FK
    uuid product_id FK
    int quantity
    int price_cents
  }

  PRODUCT {
    uuid id PK
    string name
    int price_cents
    string status
  }
```

## Infrastructure Diagram (AWS Example)

```mermaid
flowchart TB
  subgraph Internet
    U[Users]
  end

  subgraph AWS
    subgraph Public
      CF[CloudFront CDN]
      ALB[Application Load Balancer]
    end

    subgraph Private
      subgraph ECS[ECS Cluster]
        API1[API Instance]
        API2[API Instance]
        Worker[Worker Instance]
      end

      RDS[(RDS PostgreSQL)]
      Redis[(ElastiCache Redis)]
      SQS[SQS Queue]
      S3[S3 Bucket]
    end
  end

  U --> CF --> ALB --> API1 & API2
  API1 & API2 --> RDS
  API1 & API2 --> Redis
  API1 & API2 --> SQS
  Worker --> SQS
  Worker --> RDS
  API1 & API2 --> S3
```

## Diagram Selection Guide

| Scenario | Diagram Type |
|----------|--------------|
| High-level overview | System Context |
| Technical architecture | Container |
| Module structure | Component |
| API flow | Sequence |
| Data processing | Data Flow |
| Entity state | State Machine |
| Database schema | ER Diagram |
| Cloud setup | Infrastructure |
