# Architecture & Design

This boilerplate follows **Clean Architecture** principles to ensure scalability, maintainability, and testability. The codebase is organized into distinct layers with clear responsibilities.

## Folder Structure

```
src/
├── dependencies/   # Dependency Injection (Config, DB, Logger, Tracer)
├── exceptions/     # Custom Exception handling
├── models/         # Database Models (SQLModel)
├── repositories/   # Data Access Layer
├── routers/        # API Interface Layer
├── schemas/        # Data Transfer Objects (Pydantic)
├── services/       # Business Logic Layer
├── main.py         # Application Entrypoint
└── ...
```

## Layers Explained

### 1. Routers (`src/routers/`)

The entry point for HTTP requests. Routers define endpoints, handle request parsing, and delegate work to Services. They should remain thin and devoid of business logic.

- **Responsibility**: HTTP parsing, validation, calling services, returning responses.
- **Dependencies**: Services, Schemas.

### 2. Services (`src/services/`)

The core of the application. Services contain the business logic and rules. They orchestrate operations between repositories and other providers.

- **Responsibility**: Business rules, transactions, logic.
- **Dependencies**: Repositories, internal helpers.

### 3. Repositories (`src/repositories/`)

The abstraction layer for data access. Repositories handle direct interactions with the database, ensuring that services don't need to know about SQL or ORM specifics.

- **Responsibility**: CRUD operations, complex queries.
- **Dependencies**: Database Session, Models.

### 4. Models (`src/models/`)

Defines the database schema using **SQLModel**. These classes represent tables in your database.

### 5. Schemas (`src/schemas/`)

Defines the structure of data moving in and out of the API using **Pydantic**. This includes Request Bodies, Query Parameters, and Response formats.

- **Separation**: We keep DB Models separate from API Schemas to prevent leaking database details to the API clients.

## Dependency Injection

We leverage FastAPI's `Depends` system heavily to inject dependencies:

- `Config`: Application settings.
- `Database`: Async database session management.
- `Logger`: Structured logging instance.
- `HttpClient`: Async HTTP client for external requests.

This makes unit testing easier by allowing us to mock these dependencies.
