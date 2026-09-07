# Architecture Overview

## Overview

Jango101 is a Django project with two principal application areas:

- **`my1stapp`** — the main web application and user-facing functionality.
- **`api`** — the REST API, API credentials, serializers, API views, and custom administration.

The Django project package (`demo`) provides project-level configuration and application wiring.

```mermaid
flowchart TB
    Browser[Web browser] --> Django[Django application]
    APIClient[API client] --> API[REST API]

    Django --> Web[my1stapp]
    Django --> API

    Web --> Auth[Django authentication]
    Web --> Todo[ToDoItem model]

    API --> Serializers[DRF serializers]
    API --> Views[DRF API views]
    API --> Credentials[API client credentials]
    API --> JWT[Simple JWT]

    Credentials --> User[User]
    Todo --> User

    Admin[Django admin] --> UserAdmin[CustomUserAdmin]
    UserAdmin --> Credentials
```

# Application layers

## Project configuration

The `demo` project package provides Django configuration, including installed applications, middleware, URLs, authentication, database configuration, static files, and API/schema integration.

The type-checking setup uses the Django mypy plugin and django-stubs with:

```text
demo.settings
```

## Web application: `my1stapp`

Known functionality includes:

- user authentication flows
- password-change functionality
- user profile functionality
- user-owned ToDo data

The password-change tests cover both access control and successful password updates.

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant D as Django
    participant A as Authentication

    U->>B: Open password-change page
    B->>D: GET password-change URL
    D->>A: Check session

    alt Not logged in
        A-->>D: Anonymous
        D-->>B: Redirect to login
    else Logged in
        A-->>D: Authenticated user
        D-->>B: Password-change form
    end
```

# REST API: `api`

The API application uses Django REST Framework and provides:

- authenticated user information
- user-owned ToDo operations
- API client credential validation
- JWT access-token issuance

## Who Am I endpoint

`WhoAmIView` requires authentication and returns:

- user ID
- username
- email address

## ToDo ownership boundary

The ToDo API filters data using the authenticated request user. The detail endpoint uses the same ownership boundary.

```mermaid
flowchart LR
    U1[Authenticated User One] --> Q1[Query ToDo items]
    U2[Authenticated User Two] --> Q2[Query ToDo items]
    Q1 --> F1[owner = User One]
    Q2 --> F2[owner = User Two]
    F1 --> T1[Only User One data]
    F2 --> T2[Only User Two data]
```

# API client credentials

`APIClientCredential` is associated one-to-one with a user and stores:

- generated client ID
- hashed client secret
- active flag
- creation timestamp
- update timestamp

The model generates values when required during saving. Client secrets are stored using Django password hashing rather than as raw values.

```mermaid
erDiagram
    USER ||--|| API_CLIENT_CREDENTIAL : has
    USER ||--o{ TODO_ITEM : owns
```

# Client-credentials token flow

The token endpoint validates submitted credentials through a serializer, obtains the associated user, and creates a JWT access token.

```mermaid
sequenceDiagram
    participant C as API client
    participant V as Token API view
    participant S as Credentials serializer
    participant DB as Database
    participant J as Simple JWT

    C->>V: POST client_id + client_secret
    V->>S: Validate request data
    S->>DB: Find and validate credential
    DB-->>S: Credential and user
    S-->>V: Validated credential
    V->>J: Create token for user
    J-->>V: Access token
    V-->>C: access + Bearer token type
```

# Django admin

`CustomUserAdmin` provides:

- custom user creation and change forms
- custom CSS and JavaScript
- language in the Personal info fieldset
- an API credentials section
- read-only credential display for existing users

The API credentials fieldset is inserted before **Important dates** when that fieldset exists; otherwise it is appended.

```mermaid
flowchart TD
    A[Open existing user in Django admin] --> B[CustomUserAdmin.get_fieldsets]
    B --> C[Start with parent fieldsets]
    C --> D[Ensure language is in Personal info]
    D --> E{Important dates exists?}
    E -->|Yes| F[Insert API credentials before Important dates]
    E -->|No| G[Append API credentials]
    F --> H[Render admin page]
    G --> H
```

# Type checking

The project uses:

- `mypy`
- `django-stubs`
- `djangorestframework-stubs`
- `mypy_django_plugin`

The project was verified with:

```text
Success: no issues found in 57 source files
```

The exact count may change as the project grows.

# Quality architecture

```mermaid
flowchart LR
    Code[Source changes]
    Code --> Django[Django]
    Code --> Ruff[Ruff]
    Code --> Mypy[mypy]
    Code --> Templates[djLint]
    Code --> Security[Bandit]
    Code --> Dependencies[pip-audit]
    Code --> Schema[OpenAPI]
    Code --> Tests[Django tests]
    Code --> Browser[Playwright]

    Django --> Gate[Quality gate]
    Ruff --> Gate
    Mypy --> Gate
    Templates --> Gate
    Security --> Gate
    Dependencies --> Gate
    Schema --> Gate
    Tests --> Gate
    Browser --> Gate

    Gate -->|Pass| Commit[Commit allowed]
    Gate -->|Fail| Fix[Fix and rerun]
```
