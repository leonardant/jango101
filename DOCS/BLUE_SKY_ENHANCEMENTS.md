# Blue Sky Thinking: Future Enhancements

This document explores possible future directions for Jango101. These are intentionally aspirational ideas rather than a committed roadmap.

# 1. Evolve the ToDo application into a productivity platform

Possible additions:

- due dates
- priorities
- tags
- recurring tasks
- reminders
- subtasks
- projects
- attachments
- archived tasks

```mermaid
mindmap
  root((Jango101))
    Tasks
      Due dates
      Priorities
      Recurrence
      Subtasks
    Organisation
      Tags
      Projects
      Lists
    Collaboration
      Sharing
      Comments
      Mentions
    Automation
      Reminders
      Integrations
```

# 2. API scopes and fine-grained permissions

Future scopes could include:

```text
todos:read
todos:write
profile:read
credentials:manage
```

```mermaid
flowchart LR
    Credential --> Scope[Assigned scopes]
    Scope --> Token[JWT claims]
    Token --> API[API request]
    API --> Check{Scope allowed?}
    Check -->|Yes| Allow[Allow]
    Check -->|No| Deny[Deny]
```

# 3. Service accounts

Introduce machine identities separate from human users for:

- integrations
- CI jobs
- automation
- external services

```mermaid
erDiagram
    USER ||--o{ SERVICE_ACCOUNT : owns
    SERVICE_ACCOUNT ||--o{ API_CREDENTIAL : has
    SERVICE_ACCOUNT }o--o{ SCOPE : receives
```

# 4. User-facing developer dashboard

Build on the existing API credential capability with a dashboard where users can:

- create credentials
- regenerate secrets
- deactivate credentials
- manage scopes
- view last-used timestamps
- inspect API activity

# 5. API analytics

Track:

- requests by credential
- endpoint usage
- authentication failures
- error rates
- latency
- rate-limit events

```mermaid
flowchart LR
    API[API requests] --> Events[Usage events]
    Events --> Store[Analytics]
    Store --> Dashboard[Dashboard]
```

# 6. Rate limiting

Potential policies:

- per IP
- per user
- per API credential
- per endpoint

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Rate limiter
    participant API as API

    C->>R: Request
    R->>R: Check quota
    alt Within limit
        R->>API: Forward
        API-->>C: Response
    else Exceeded
        R-->>C: 429
    end
```

# 7. Background jobs

Useful for:

- reminders
- recurring tasks
- reports
- credential expiry notifications
- webhook delivery

```mermaid
flowchart LR
    Web[Django / API] --> Queue[Task queue]
    Queue --> Worker[Worker]
    Worker --> DB[(Database)]
    Worker --> Email[Email]
    Worker --> External[External services]
```

# 8. Notifications

Potential channels:

- in-app
- email
- browser
- future mobile push notifications

Examples include task reminders, credential expiry and security events.

# 9. Collaboration

Possible future features:

- shared lists
- assignments
- comments
- mentions
- roles
- activity history

```mermaid
flowchart LR
    Owner[Owner] --> List[Shared list]
    Editor[Editor] --> List
    Viewer[Viewer] --> List
```

# 10. Webhooks and integrations

Possible events:

```text
todo.created
todo.updated
todo.completed
credential.rotated
```

```mermaid
sequenceDiagram
    participant App as Jango101
    participant Event as Event system
    participant Client as Integration

    App->>Event: Event occurs
    Event->>Client: Webhook
    Client-->>Event: Acknowledgement
```

# 11. Search and smart lists

Future search could support:

```text
status:open tag:work due:this-week
```

This could evolve into:

- saved searches
- smart lists
- filtered dashboards

# 12. Internationalisation

The existing language concept could become a foundation for:

- translated templates
- language preferences
- timezone preferences
- locale-aware dates

# 13. Progressive Web App

A PWA could provide:

- installability
- mobile-friendly UX
- offline access
- background synchronisation

# 14. Real-time updates

Collaboration could eventually justify:

- WebSockets
- live task updates
- live comments
- assignment notifications

# 15. Mobile clients and generated SDKs

The existing OpenAPI foundation could support:

```mermaid
flowchart LR
    Django[DRF API] --> Schema[OpenAPI]
    Schema --> Python[Python SDK]
    Schema --> JS[JavaScript SDK]
    Schema --> Mobile[Mobile clients]
```

# 16. Feature flags

Feature flags could support:

- beta functionality
- gradual rollout
- internal-only features
- controlled experiments

# 17. AI-assisted productivity

Potential AI features:

- convert natural language into tasks
- summarise projects
- suggest priorities
- identify dependencies
- draft task descriptions

Principle:

> AI suggests; the user remains in control.

# Possible long-term evolution

```mermaid
timeline
    title Possible Jango101 evolution
    Current : Web app
            : REST API
            : JWT
            : Strong local quality pipeline
    Next : CI
         : Production hardening
         : Observability
    Growth : Projects
           : Reminders
           : API scopes
           : Developer dashboard
    Collaboration : Sharing
                  : Comments
                  : Assignments
    Platform : Webhooks
             : Service accounts
             : Mobile clients
             : Generated SDKs
```

# Most promising directions

## Near term

- projects and task organisation
- due dates and reminders
- developer credential dashboard
- API scopes

## Platform maturity

- CI
- observability
- rate limiting
- service accounts
- webhooks

## Larger product evolution

- collaboration
- mobile clients
- PWA
- generated SDKs
- AI-assisted productivity

## Final thought

The application already has strong engineering foundations. Future work can increasingly focus on **capability and user value** rather than repeatedly rebuilding quality controls.

The best rule for blue-sky development is:

> Add complexity only when it unlocks a real capability.
