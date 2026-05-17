# Repository Map

```markdown
/ (.)
├── .git/
├── backend/
    ├── .pytest_cache/
    ├── .venv/
    ├── alembic/
    │   ├── __pycache__/
    │   ├── versions/
    │   │   ├── __pycache__/
    │   │   ├── 0001_create_users_table.py (Python)
    │   │   │   ├── Description: Alembic migration script that creates the initial users table in the database.
    │   │   │   ├── Maintenance Flag: Stable
    │   │   │   ├── Architectural Role: Persistence
    │   │   │   ├── Critical Dependencies:
    │   │   │   ├──   - alembic.op: Provides operations for database schema migrations.
    │   │   │   └──   - sqlalchemy: Defines the schema and column types for the users table.
    │   │   ├── 0002_create_cart_tables.py (Python)
    │   │   │   ├── Description: Alembic migration script that creates the cart and cart_items tables in the database.
    │   │   │   ├── Maintenance Flag: Stable
    │   │   │   ├── Architectural Role: Persistence
    │   │   │   ├── Critical Dependencies:
    │   │   │   ├──   - alembic.op: Provides operations for modifying the database schema.
    │   │   │   └──   - sqlalchemy: Defines the table schema and column types.
    │   │   └── 0003_create_orders_tables.py (Python)
    │   │       ├── Description: Alembic migration script that creates the orders and order_items tables in the database.
    │   │       ├── Maintenance Flag: Generated
    │   │       ├── Architectural Role: Persistence
    │   │       ├── Critical Dependencies:
    │   │       ├──   - alembic.op: Provides operations for modifying the database schema.
    │   │       └──   - sqlalchemy: Defines the table schema and column types.
    │   ├── README (None)
    │   ├── env.py (Python)
    │   │   ├── Description: Alembic environment configuration file that sets up database connection and migration context for SQLAlchemy models.
    │   │   ├── Developer Consideration: Migration scripts depend on the correct SQLAlchemy engine configuration; ensure environment variables are properly set before running migrations.
    │   │   ├── Maintenance Flag: Stable
    │   │   ├── Architectural Role: Persistence
    │   │   ├── Security Assessment: Ensure database credentials are securely managed via environment variables to prevent exposure in version control.
    │   │   ├── Critical Dependencies:
    │   │   ├──   - sqlalchemy: Core database abstraction layer and engine configuration.
    │   │   └──   - alembic: Migration framework for managing database schema changes.
    │   └── script.py.mako (None)
    ├── app/
    │   ├── __pycache__/
    │   ├── core/
    │   │   ├── __pycache__/
    │   │   ├── __init__.py (Python)
    │   │   ├── config.py (Python)
    │   │   │   ├── Description: Central configuration management using Pydantic Settings, handling environment variables and application settings.
    │   │   │   ├── Developer Consideration: Environment variables must be prefixed with 'APP_' to be recognized by the settings model.
    │   │   │   ├── Maintenance Flag: Stable
    │   │   │   ├── Architectural Role: Configuration
    │   │   │   ├── Critical Dependencies:
    │   │   │   ├──   - pydantic_settings.BaseSettings: Base class for defining settings models with environment variable support.
    │   │   │   └──   - pydantic_settings.SettingsConfigDict: Configuration dictionary for Pydantic settings models.
    │   │   ├── database.py (Python)
    │   │   │   ├── Description: Provides async database session management and engine configuration using SQLAlchemy and SQLModel.
    │   │   │   ├── Developer Consideration: Database sessions are managed via async context managers; ensure proper async/await usage to avoid connection leaks.
    │   │   │   ├── Maintenance Flag: Stable
    │   │   │   ├── Architectural Role: Persistence
    │   │   │   ├── Security Assessment: Database credentials are sourced from environment variables; ensure proper secrets management in production.
    │   │   │   ├── Critical Dependencies:
    │   │   │   ├──   - sqlalchemy.ext.asyncio: Async SQLAlchemy engine and session management.
    │   │   │   ├──   - sqlmodel: ORM layer combining SQLAlchemy with Pydantic models.
    │   │   │   └──   - app.core.config.settings: Database connection configuration from environment variables.
    │   │   ├── dependencies.py (Python)
    │   │   │   ├── Description: Centralized dependency injection for FastAPI routes, handling authentication, database sessions, and user context.
    │   │   │   ├── Developer Consideration: Authentication dependencies rely on JWT tokens; ensure token expiration and validation logic aligns with security requirements.
    │   │   │   ├── Maintenance Flag: Stable
    │   │   │   ├── Architectural Role: Service
    │   │   │   ├── Security Assessment: JWT token validation should include additional checks for token freshness and audience claims to prevent token replay attacks.
    │   │   │   ├── Critical Dependencies:
    │   │   │   ├──   - fastapi.security.HTTPBearer: Bearer token authentication scheme for API endpoints.
    │   │   │   ├──   - sqlalchemy.ext.asyncio.AsyncSession: Async database session management for route handlers.
    │   │   │   └──   - jose.jwt: JWT token decoding and validation for authentication.
    │   │   ├── error_handlers.py (Python)
    │   │   │   ├── Description: Centralized error handling for FastAPI routes, converting exceptions into structured JSON responses.
    │   │   │   ├── Developer Consideration: Error handlers must be registered in the FastAPI app initialization to take effect.
    │   │   │   ├── Maintenance Flag: Stable
    │   │   │   ├── Architectural Role: Utility
    │   │   │   ├── Critical Dependencies:
    │   │   │   └──   - fastapi: Framework dependency for HTTP exception handling and response formatting.
    │   │   ├── exceptions.py (Python)
    │   │   │   ├── Description: Defines custom exceptions and error handling utilities for the FastAPI application.
    │   │   │   ├── Developer Consideration: Custom exceptions should be registered in the FastAPI app's error handlers to ensure consistent error responses.
    │   │   │   ├── Maintenance Flag: Stable
    │   │   │   ├── Architectural Role: Utility
    │   │   │   ├── Critical Dependencies:
    │   │   │   ├──   - fastapi.HTTPException: Base exception class for HTTP errors, used to define custom exceptions.
    │   │   │   └──   - fastapi.status: Provides HTTP status codes for consistent error responses.
    │   │   └── security.py (Python)
    │   │       ├── Description: Handles password hashing, verification, and JWT token generation for authentication.
    │   │       ├── Developer Consideration: JWT token expiration and secret key are derived from the app's configuration; ensure these values are securely managed.
    │   │       ├── Maintenance Flag: Stable
    │   │       ├── Architectural Role: Other
    │   │       ├── Security Assessment: Ensure JWT secret key is sufficiently long and securely stored; consider rotating keys periodically.
    │   │       ├── Critical Dependencies:
    │   │       ├──   - jose: JWT encoding/decoding and error handling.
    │   │       ├──   - passlib.context.CryptContext: Secure password hashing and verification.
    │   │       └──   - app.core.config.settings: Provides JWT secret key and token expiration configuration.
    │   ├── features/
    │   │   ├── __pycache__/
    │   │   ├── auth/
    │   │   │   ├── __pycache__/
    │   │   │   ├── __init__.py (Python)
    │   │   │   ├── router.py (Python)
    │   │   │   │   ├── Description: FastAPI router handling authentication endpoints for user registration and login.
    │   │   │   │   ├── Developer Consideration: Authentication endpoints rely on JWT tokens for session management; ensure token expiration and secret key are securely configured.
    │   │   │   │   ├── Maintenance Flag: Stable
    │   │   │   │   ├── Architectural Role: API Route
    │   │   │   │   ├── Security Assessment: Ensure JWT tokens are securely signed and have appropriate expiration times to mitigate session hijacking risks.
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   ├──   - fastapi.APIRouter: Core FastAPI component for defining route handlers.
    │   │   │   │   ├──   - app.core.dependencies.DBSessionDep: Provides database session management for route handlers.
    │   │   │   │   ├──   - app.core.dependencies.CurrentUserDep: Provides current user context for authenticated routes.
    │   │   │   │   ├──   - app.features.auth.use_cases.register_user: Handles user registration logic.
    │   │   │   │   └──   - app.features.auth.use_cases.login_user: Handles user login logic.
    │   │   │   ├── schemas.py (Python)
    │   │   │   │   ├── Description: Defines Pydantic models for authentication-related data structures, including user registration and login schemas.
    │   │   │   │   ├── Developer Consideration: Schemas must align with both the database models and the API contract; changes here may require coordinated updates to routes and use cases.
    │   │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   │   ├── Architectural Role: Data Model
    │   │   │   │   ├── Security Assessment: EmailStr validation helps prevent malformed credentials, but additional rate-limiting and password strength checks should be implemented at the application layer.
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   ├──   - pydantic.BaseModel: Base class for defining data validation schemas.
    │   │   │   │   ├──   - pydantic.EmailStr: Email address validation for user credentials.
    │   │   │   │   └──   - app.features.users.schemas.UserRead: Reused user schema for consistent data representation.
    │   │   │   └── use_cases.py (Python)
    │   │   │       ├── Description: Implements authentication use cases including user registration, login, and token generation.
    │   │   │       ├── Developer Consideration: Password hashing and token generation rely on core security utilities; ensure these are properly configured and tested.
    │   │   │       ├── Maintenance Flag: Volatile
    │   │   │       ├── Architectural Role: Service
    │   │   │       ├── Refactoring Suggestions: Consider extracting token generation logic into a separate utility to improve separation of concerns.
    │   │   │       ├── Security Assessment: Ensure password hashing uses a strong algorithm and token expiration is appropriately short to mitigate credential compromise risks.
    │   │   │       ├── Critical Dependencies:
    │   │   │       ├──   - app.core.security: Provides password hashing, verification, and token generation utilities.
    │   │   │       └──   - app.features.users.repositories: Handles user data persistence and retrieval.
    │   │   ├── cart/
    │   │   │   ├── __pycache__/
    │   │   │   ├── __init__.py (Python)
    │   │   │   ├── models.py (Python)
    │   │   │   │   ├── Description: Defines SQLModel-based data models for the cart feature, including Cart and CartItem entities with their relationships.
    │   │   │   │   ├── Developer Consideration: Relationships between Cart and CartItem are bidirectional; changes to one model may require updates to the other.
    │   │   │   │   ├── Maintenance Flag: Stable
    │   │   │   │   ├── Architectural Role: Data Model
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   └──   - sqlmodel: Provides SQLAlchemy integration with Pydantic models for database schema definition.
    │   │   │   ├── repositories.py (Python)
    │   │   │   │   ├── Description: Repository layer for cart operations, handling database interactions for Cart and CartItem entities.
    │   │   │   │   ├── Developer Consideration: All database operations are async; ensure proper async/await usage to avoid connection leaks.
    │   │   │   │   ├── Maintenance Flag: Stable
    │   │   │   │   ├── Architectural Role: Persistence
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   └──   - sqlalchemy.ext.asyncio.AsyncSession: Async database session management for non-blocking operations.
    │   │   │   ├── router.py (Python)
    │   │   │   │   ├── Description: FastAPI router handling cart-related endpoints, including operations for retrieving, adding, updating, and removing cart items.
    │   │   │   │   ├── Developer Consideration: All cart operations are scoped to the authenticated user; ensure proper authentication middleware is in place to prevent unauthorized access.
    │   │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   │   ├── Architectural Role: API Route
    │   │   │   │   ├── Refactoring Suggestions: Consider consolidating the cart item operations into a single endpoint with a unified request/response model to reduce API surface area.
    │   │   │   │   ├── Security Assessment: Ensure proper validation of user input to prevent SQL injection or unauthorized cart modifications.
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   ├──   - fastapi.APIRouter: Core routing mechanism for defining API endpoints.
    │   │   │   │   ├──   - app.core.dependencies.CurrentUserDep: Provides authenticated user context for cart operations.
    │   │   │   │   └──   - app.core.dependencies.DBSessionDep: Manages database sessions for cart-related queries.
    │   │   │   └── schemas.py (Python)
    │   │   │       ├── Description: Defines Pydantic models for cart-related data structures, including schemas for cart items and cart operations.
    │   │   │       ├── Maintenance Flag: Volatile
    │   │   │       ├── Architectural Role: Data Model
    │   │   │       ├── Critical Dependencies:
    │   │   │       ├──   - pydantic.BaseModel: Base class for defining data schemas with validation.
    │   │   │       └──   - pydantic.Field: Utility for adding metadata and constraints to schema fields.
    │   │   ├── checkout/
    │   │   │   ├── __pycache__/
    │   │   │   ├── __init__.py (Python)
    │   │   │   ├── payment.py (Python)
    │   │   │   │   ├── Description: Handles payment processing logic for the checkout feature, including validation and transaction execution.
    │   │   │   │   ├── Developer Consideration: Payment processing is a critical path; ensure proper error handling and logging for all transaction states.
    │   │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   │   ├── Architectural Role: Service
    │   │   │   │   └── Security Assessment: Payment processing must be secured against replay attacks and ensure sensitive data is not logged or exposed.
    │   │   │   ├── router.py (Python)
    │   │   │   │   ├── Description: FastAPI router handling checkout-related endpoints, including order creation, retrieval, and detail views.
    │   │   │   │   ├── Developer Consideration: All endpoints require authentication and database session dependencies; ensure proper middleware and dependency injection are configured.
    │   │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   │   ├── Architectural Role: API Route
    │   │   │   │   ├── Refactoring Suggestions: Consider consolidating the order retrieval logic into a single endpoint with query parameters for filtering, rather than separate endpoints for user orders and order detail.
    │   │   │   │   ├── Security Assessment: Ensure proper authorization checks are in place to prevent users from accessing other users' order data through the order detail endpoint.
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   ├──   - fastapi.APIRouter: Core FastAPI component for defining route handlers and endpoints.
    │   │   │   │   ├──   - app.core.dependencies.CurrentUserDep: Provides authenticated user context for all checkout operations.
    │   │   │   │   └──   - app.core.dependencies.DBSessionDep: Manages database session lifecycle for transactional operations.
    │   │   │   └── use_cases.py (Python)
    │   │   │       ├── Description: Implements checkout-related use cases including order creation, payment processing, and order retrieval.
    │   │   │       ├── Developer Consideration: Payment processing is a critical path; ensure proper error handling and logging for all transaction states.
    │   │   │       ├── Maintenance Flag: Volatile
    │   │   │       ├── Architectural Role: Service
    │   │   │       ├── Refactoring Suggestions: Consider extracting payment processing into a separate service class to improve separation of concerns and testability.
    │   │   │       ├── Security Assessment: Ensure payment processing logic handles sensitive data securely and complies with PCI DSS requirements.
    │   │   │       ├── Critical Dependencies:
    │   │   │       ├──   - app.features.checkout.payment.process_payment: Handles payment processing logic, a critical component of the checkout flow.
    │   │   │       └──   - app.features.orders.repositories.create_order_from_cart: Creates an order from the user's cart, central to the checkout process.
    │   │   ├── orders/
    │   │   │   ├── __pycache__/
    │   │   │   ├── domain/
    │   │   │   │   ├── __pycache__/
    │   │   │   │   └── __init__.py (Python)
    │   │   │   │       ├── Description: Empty domain module for the orders feature, serving as a namespace placeholder for future domain-specific implementations.
    │   │   │   │       └── Architectural Role: Other
    │   │   │   ├── __init__.py (Python)
    │   │   │   ├── models.py (Python)
    │   │   │   │   ├── Description: Defines SQLModel-based data models for the orders feature, including Order and OrderItem entities with their relationships.
    │   │   │   │   ├── Developer Consideration: Relationships between Order and OrderItem are bidirectional; changes to one model may require updates to the other.
    │   │   │   │   ├── Maintenance Flag: Stable
    │   │   │   │   ├── Architectural Role: Data Model
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   ├──   - sqlmodel: Provides the base SQLModel class and field definitions for ORM and Pydantic integration.
    │   │   │   │   └──   - app.features.orders.domain.OrderStatus: Defines the status enumeration used in the Order model.
    │   │   │   ├── repositories.py (Python)
    │   │   │   │   ├── Description: Repository layer for order operations, handling database interactions for Order and OrderItem entities.
    │   │   │   │   ├── Developer Consideration: All database operations are async; ensure proper async/await usage to avoid connection leaks.
    │   │   │   │   ├── Maintenance Flag: Stable
    │   │   │   │   ├── Architectural Role: Persistence
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   ├──   - sqlalchemy.select: Used to construct database queries for order-related operations.
    │   │   │   │   └──   - sqlalchemy.ext.asyncio.AsyncSession: Provides async database session management for non-blocking operations.
    │   │   │   └── schemas.py (Python)
    │   │   │       ├── Description: Defines Pydantic models for order-related data structures, including schemas for order creation, retrieval, and status updates.
    │   │   │       ├── Developer Consideration: Schemas must align with both the database models and the API contract; changes here may require coordinated updates to routes and use cases.
    │   │   │       ├── Maintenance Flag: Volatile
    │   │   │       ├── Architectural Role: Data Model
    │   │   │       ├── Critical Dependencies:
    │   │   │       ├──   - pydantic.BaseModel: Core validation and serialization framework for API schemas.
    │   │   │       └──   - app.features.orders.domain.OrderStatus: Enumeration of valid order states; changes here may require schema updates.
    │   │   ├── users/
    │   │   │   ├── __pycache__/
    │   │   │   ├── domain/
    │   │   │   │   ├── __pycache__/
    │   │   │   │   └── __init__.py (Python)
    │   │   │   │       ├── Description: Empty domain module for the users feature, serving as a namespace placeholder for future domain-specific implementations.
    │   │   │   │       └── Architectural Role: Other
    │   │   │   ├── __init__.py (Python)
    │   │   │   ├── models.py (Python)
    │   │   │   │   ├── Description: Defines SQLModel-based data models for the users feature, including User entity with its relationships and role enumeration.
    │   │   │   │   ├── Developer Consideration: UserRole enumeration is imported from the domain module; changes to role definitions must be coordinated across both modules.
    │   │   │   │   ├── Maintenance Flag: Stable
    │   │   │   │   ├── Architectural Role: Data Model
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   └──   - sqlmodel: Provides SQLAlchemy integration with Pydantic for type-safe database models.
    │   │   │   ├── repositories.py (Python)
    │   │   │   │   ├── Description: Repository layer for user operations, handling database interactions for the User entity using SQLAlchemy's async session management.
    │   │   │   │   ├── Developer Consideration: All database operations are async; ensure proper async/await usage to avoid connection leaks.
    │   │   │   │   ├── Maintenance Flag: Stable
    │   │   │   │   ├── Architectural Role: Persistence
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   ├──   - sqlalchemy.select: Core query construction for retrieving User entities.
    │   │   │   │   └──   - sqlalchemy.ext.asyncio.AsyncSession: Async session management for database operations.
    │   │   │   └── schemas.py (Python)
    │   │   │       ├── Description: Defines Pydantic models for user-related data structures, including schemas for user registration, authentication, and profile updates.
    │   │   │       ├── Developer Consideration: Schemas must align with both the database models and the API contract; changes here may require coordinated updates to routes and use cases.
    │   │   │       ├── Maintenance Flag: Volatile
    │   │   │       ├── Architectural Role: Data Model
    │   │   │       ├── Critical Dependencies:
    │   │   │       ├──   - pydantic.BaseModel: Core schema validation and serialization framework.
    │   │   │       ├──   - pydantic.EmailStr: Email address validation with built-in format checking.
    │   │   │       └──   - app.features.users.domain.UserRole: Enumeration of user roles imported from the domain module.
    │   │   └── __init__.py (Python)
    │   ├── __init__.py (Python)
    │   └── main.py (Python)
    │       ├── Description: Entrypoint for the FastAPI application, configuring routes, middleware, and exception handlers.
    │       ├── Developer Consideration: All routes and middleware must be registered here; changes to the application structure require updates to this file.
    │       ├── Maintenance Flag: Stable
    │       ├── Architectural Role: Entrypoint
    │       ├── Critical Dependencies:
    │       ├──   - fastapi: Core framework for building the API and handling HTTP requests.
    │       ├──   - app.core.database: Database initialization and table creation.
    │       └──   - app.core.error_handlers: Centralized exception handling for consistent error responses.
    ├── tests/
    │   ├── __pycache__/
    │   ├── conftest.py (Python)
    │   │   ├── Description: Pytest configuration file providing fixtures for async database sessions, HTTP clients, and application settings.
    │   │   ├── Developer Consideration: Fixtures are shared across all tests; ensure proper isolation by using async fixtures and cleaning up resources after each test.
    │   │   ├── Maintenance Flag: Stable
    │   │   ├── Architectural Role: Test
    │   │   ├── Critical Dependencies:
    │   │   ├──   - httpx.ASGITransport: Provides async HTTP transport for testing FastAPI applications.
    │   │   ├──   - sqlalchemy.ext.asyncio.create_async_engine: Creates an async SQLAlchemy engine for database operations in tests.
    │   │   └──   - app.core.database.get_session: Provides async database sessions for testing database interactions.
    │   ├── test_auth.py (Python)
    │   │   ├── Description: Test suite for authentication-related endpoints, covering user registration, login, and token validation.
    │   │   ├── Developer Consideration: Tests rely on a clean database state; ensure proper fixture setup and teardown to avoid test pollution.
    │   │   ├── Maintenance Flag: Volatile
    │   │   ├── Architectural Role: Test
    │   │   ├── Refactoring Suggestions: Extract common test utilities (e.g., user creation, token generation) into shared fixtures to reduce duplication.
    │   │   ├── Critical Dependencies:
    │   │   └──   - httpx.AsyncClient: Async HTTP client for testing FastAPI endpoints.
    │   ├── test_cart.py (Python)
    │   │   ├── Description: Test suite for cart-related endpoints, covering operations for retrieving, adding, updating, and removing cart items.
    │   │   ├── Developer Consideration: Tests rely on a clean database state; ensure proper fixture setup and teardown to avoid test pollution.
    │   │   ├── Maintenance Flag: Volatile
    │   │   ├── Architectural Role: Test
    │   │   ├── Critical Dependencies:
    │   │   ├──   - pytest: Testing framework for writing and running test cases.
    │   │   └──   - httpx.AsyncClient: Async HTTP client for testing FastAPI endpoints.
    │   └── test_checkout.py (Python)
    │       ├── Description: Test suite for checkout-related endpoints, covering order creation, payment processing, and order retrieval.
    │       ├── Developer Consideration: Tests rely on a clean database state; ensure proper fixture setup and teardown to avoid test pollution.
    │       ├── Maintenance Flag: Volatile
    │       ├── Architectural Role: Test
    │       ├── Critical Dependencies:
    │       ├──   - pytest: Testing framework for writing and running test cases.
    │       └──   - httpx.AsyncClient: Async HTTP client for testing FastAPI endpoints.
    ├── Dockerfile (None)
    ├── alembic.ini (INI)
    ├── migration_output.txt (Text)
    ├── pyproject.toml (None)
    └── uv.lock (None)
├── docs/
    └── agent/
    │   ├── auth_flow.md (Markdown)
    │   ├── checkout_state.md (Markdown)
    │   ├── database_schema.md (Markdown)
    │   └── frontend_state.md (Markdown)
├── frontend/
    ├── dist/
    ├── node_modules/
    ├── public/
    │   ├── favicon.svg (Image)
    │   └── icons.svg (Image)
    ├── src/
    │   ├── assets/
    │   │   ├── hero.png (Image)
    │   │   ├── react.svg (Image)
    │   │   └── vite.svg (Image)
    │   ├── entities/
    │   │   ├── auth/
    │   │   │   ├── store.test.ts (TypeScript)
    │   │   │   │   ├── Description: Unit tests for the authentication store, verifying state management and behavior of auth-related actions.
    │   │   │   │   ├── Developer Consideration: Tests rely on a clean store state; ensure proper setup and teardown to avoid state pollution between test cases.
    │   │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   │   ├── Architectural Role: Test
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   └──   - vitest: Testing framework providing assertions, mocks, and test runner functionality.
    │   │   │   └── store.ts (TypeScript)
    │   │   │       ├── Description: Manages authentication state using Zustand, handling user login status, tokens, and session persistence.
    │   │   │       ├── Developer Consideration: State persistence relies on localStorage; ensure sensitive data is properly encrypted or avoided.
    │   │   │       ├── Maintenance Flag: Volatile
    │   │   │       ├── Architectural Role: Data Model
    │   │   │       ├── Refactoring Suggestions: Consider extracting token management logic into a separate utility for better separation of concerns.
    │   │   │       ├── Security Assessment: Storing authentication tokens in localStorage exposes them to XSS attacks; consider using httpOnly cookies instead.
    │   │   │       ├── Critical Dependencies:
    │   │   │       └──   - zustand: State management library providing the store implementation and reactivity.
    │   │   ├── cart/
    │   │   │   └── store.ts (TypeScript)
    │   │   │       ├── Description: Manages cart state using Zustand, handling operations for adding, updating, and removing cart items.
    │   │   │       ├── Developer Consideration: State persistence relies on localStorage; ensure sensitive data is properly encrypted or avoided.
    │   │   │       ├── Maintenance Flag: Volatile
    │   │   │       ├── Architectural Role: Data Model
    │   │   │       ├── Security Assessment: Ensure sensitive data in localStorage is encrypted to prevent unauthorized access.
    │   │   │       ├── Critical Dependencies:
    │   │   │       ├──   - zustand: State management library for handling cart state and actions.
    │   │   │       └──   - ../../shared/api/client: Provides API client for cart-related operations.
    │   │   └── orders/
    │   │   │   └── store.ts (TypeScript)
    │   │   │       ├── Description: Manages order state using Zustand, handling operations for retrieving and updating order information.
    │   │   │       ├── Developer Consideration: State persistence relies on localStorage; ensure sensitive data is properly encrypted or avoided.
    │   │   │       ├── Maintenance Flag: Volatile
    │   │   │       ├── Architectural Role: Data Model
    │   │   │       ├── Security Assessment: Ensure sensitive order data is not persisted in localStorage without encryption to prevent data exposure.
    │   │   │       ├── Critical Dependencies:
    │   │   │       ├──   - zustand: State management library for handling order state.
    │   │   │       └──   - ../../shared/api/client: Provides API client for fetching and updating order data.
    │   ├── features/
    │   │   └── auth/
    │   │   │   ├── LoginForm.test.tsx (TypeScript)
    │   │   │   │   ├── Description: Unit tests for the LoginForm component, verifying form behavior, validation, and interaction with the authentication store.
    │   │   │   │   ├── Developer Consideration: Tests rely on mocking the auth store and API client; ensure mocks accurately reflect production behavior to avoid false positives.
    │   │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   │   ├── Architectural Role: Test
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   ├──   - vitest: Testing framework for running and asserting component behavior.
    │   │   │   │   ├──   - ../../entities/auth/store: Mocked authentication store for simulating login state and actions.
    │   │   │   │   └──   - ../../shared/api/client: Mocked API client for simulating network requests and responses.
    │   │   │   ├── LoginForm.tsx (TypeScript)
    │   │   │   │   ├── Description: LoginForm component handling user authentication with email and password inputs, form validation, and submission to the authentication API.
    │   │   │   │   ├── Developer Consideration: Form state management relies on the auth store; ensure proper synchronization between form state and store state to prevent inconsistencies.
    │   │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   │   ├── Architectural Role: UI Component
    │   │   │   │   ├── Refactoring Suggestions: Consider extracting form validation logic into a separate utility function for better reusability and testability.
    │   │   │   │   ├── Security Assessment: Ensure sensitive data (e.g., passwords) is not logged or exposed in error messages to prevent security vulnerabilities.
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   ├──   - react: Core UI library for component rendering and state management.
    │   │   │   │   ├──   - ../../shared/api/client: API client for making authentication requests to the backend.
    │   │   │   │   └──   - ../../entities/auth/store: State management for authentication-related data and session persistence.
    │   │   │   ├── ProtectedRoute.test.tsx (TypeScript)
    │   │   │   │   ├── Description: Unit tests for the ProtectedRoute component, verifying its behavior in guarding routes based on authentication state.
    │   │   │   │   ├── Developer Consideration: Tests rely on mocking the auth store; ensure mocks accurately reflect production behavior to avoid false positives.
    │   │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   │   ├── Architectural Role: Test
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   ├──   - vitest: Testing framework used for writing and running unit tests.
    │   │   │   │   └──   - ../../entities/auth/store: Provides the authentication state used by ProtectedRoute to determine access.
    │   │   │   ├── ProtectedRoute.tsx (TypeScript)
    │   │   │   │   ├── Description: ProtectedRoute component guards access to routes based on the user's authentication state, redirecting unauthenticated users to the login page.
    │   │   │   │   ├── Developer Consideration: Relies on the auth store for authentication state; ensure the store is properly initialized and synchronized with the backend session.
    │   │   │   │   ├── Maintenance Flag: Stable
    │   │   │   │   ├── Architectural Role: UI Component
    │   │   │   │   ├── Security Assessment: Ensures authenticated access to protected routes; however, relies on client-side state which could be manipulated. Consider verifying session validity with the backend on each route access.
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   └──   - ../../entities/auth/store: Provides authentication state management for determining if a user is logged in.
    │   │   │   └── RegisterForm.tsx (TypeScript)
    │   │   │       ├── Description: RegisterForm component handling user registration with form inputs, validation, and submission to the authentication API.
    │   │   │       ├── Developer Consideration: Form state management relies on the auth store; ensure proper synchronization between form state and store state to prevent inconsistencies.
    │   │   │       ├── Maintenance Flag: Volatile
    │   │   │       ├── Architectural Role: UI Component
    │   │   │       ├── Security Assessment: Ensure sensitive data (e.g., passwords) is properly encrypted during transmission and not stored in plaintext in the component state.
    │   │   │       ├── Critical Dependencies:
    │   │   │       ├──   - react: Core library for building the component and managing state.
    │   │   │       ├──   - ../../shared/api/client: API client for submitting registration requests to the backend.
    │   │   │       └──   - ../../entities/auth/store: State management for authentication-related data and actions.
    │   ├── pages/
    │   │   ├── Cart.tsx (TypeScript)
    │   │   │   ├── Description: Cart page component displaying the user's shopping cart items and summary.
    │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   └── Architectural Role: UI Component
    │   │   ├── CartPage.tsx (TypeScript)
    │   │   │   ├── Description: Cart page component displaying the user's shopping cart items and summary.
    │   │   │   └── Architectural Role: UI Component
    │   │   ├── CheckoutPage.tsx (TypeScript)
    │   │   │   ├── Description: Checkout page component handling the finalization of cart items into an order, including payment processing and order confirmation.
    │   │   │   ├── Developer Consideration: Relies on both cart and order stores for state management; ensure proper synchronization between these stores to avoid inconsistencies.
    │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   ├── Architectural Role: UI Component
    │   │   │   ├── Refactoring Suggestions: Consider extracting payment processing logic into a separate hook or service for better reusability and testability.
    │   │   │   ├── Security Assessment: Ensure sensitive payment information is handled securely and not persisted in local storage or state.
    │   │   │   ├── Critical Dependencies:
    │   │   │   ├──   - ../entities/cart/store: Provides access to the current cart state for order creation.
    │   │   │   └──   - ../entities/orders/store: Manages the order creation and confirmation process.
    │   │   ├── CheckoutSuccess.tsx (TypeScript)
    │   │   │   ├── Description: Displays a success message and order confirmation details after a successful checkout.
    │   │   │   ├── Maintenance Flag: Stable
    │   │   │   └── Architectural Role: UI Component
    │   │   ├── Home.tsx (TypeScript)
    │   │   │   ├── Description: Home page component displaying the main landing view of the application.
    │   │   │   └── Architectural Role: UI Component
    │   │   ├── Login.tsx (TypeScript)
    │   │   │   ├── Description: Login page component that renders the authentication form and handles the login flow.
    │   │   │   ├── Developer Consideration: Relies on the LoginForm component for form rendering and submission; ensure proper synchronization between page state and form state.
    │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   ├── Architectural Role: UI Component
    │   │   │   ├── Security Assessment: Ensure proper handling of authentication tokens and secure storage to prevent token leakage or unauthorized access.
    │   │   │   ├── Critical Dependencies:
    │   │   │   └──   - ../features/auth/LoginForm: Handles the login form rendering, validation, and submission logic.
    │   │   ├── OrderDetail.tsx (TypeScript)
    │   │   │   ├── Description: Displays detailed information about a specific order, including items, status, and payment details.
    │   │   │   ├── Developer Consideration: Relies on the orders store for order data; ensure the store is properly initialized and synchronized with the backend.
    │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   ├── Architectural Role: UI Component
    │   │   │   ├── Critical Dependencies:
    │   │   │   └──   - ../entities/orders/store: Provides order data and state management for the component.
    │   │   ├── OrderHistory.tsx (TypeScript)
    │   │   │   ├── Description: Displays a user's order history by fetching and rendering their past orders from the orders store.
    │   │   │   ├── Developer Consideration: Relies on the orders store for order data; ensure the store is properly initialized and synchronized with the backend.
    │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   ├── Architectural Role: UI Component
    │   │   │   ├── Critical Dependencies:
    │   │   │   └──   - ../entities/orders/store: Provides the order data and state management for the order history view.
    │   │   ├── Products.tsx (TypeScript)
    │   │   │   ├── Description: Products page component displaying the available products for purchase.
    │   │   │   └── Architectural Role: UI Component
    │   │   └── Register.tsx (TypeScript)
    │   │       ├── Description: Register page component that renders the user registration form and handles the registration flow.
    │   │       ├── Developer Consideration: Relies on the RegisterForm component for form rendering and submission; ensure proper synchronization between page state and form state.
    │   │       ├── Maintenance Flag: Volatile
    │   │       ├── Architectural Role: UI Component
    │   │       ├── Critical Dependencies:
    │   │       └──   - ../features/auth/RegisterForm: Handles the form rendering and submission logic for user registration.
    │   ├── shared/
    │   │   ├── api/
    │   │   │   └── client.ts (TypeScript)
    │   │   │       ├── Description: Provides a configured Axios client instance for making HTTP requests to the backend API.
    │   │   │       ├── Developer Consideration: All API requests should use this client instance to ensure consistent configuration and error handling.
    │   │   │       ├── Maintenance Flag: Stable
    │   │   │       ├── Architectural Role: Service
    │   │   │       ├── Critical Dependencies:
    │   │   │       └──   - axios: HTTP client for making requests to the backend API.
    │   │   └── ui/
    │   │   │   └── Layout.tsx (TypeScript)
    │   │   │       ├── Description: Provides a consistent layout structure for application pages, including header, footer, and main content areas.
    │   │   │       ├── Maintenance Flag: Stable
    │   │   │       └── Architectural Role: UI Component
    │   ├── test/
    │   │   └── setup.ts (TypeScript)
    │   ├── widgets/
    │   │   └── cart/
    │   │   │   ├── CartSummary.tsx (TypeScript)
    │   │   │   │   ├── Description: Displays a summary of the user's cart, including item details, quantities, and total price.
    │   │   │   │   ├── Developer Consideration: Relies on the cart store for state management; ensure proper synchronization between the store and the component's rendering logic.
    │   │   │   │   ├── Maintenance Flag: Volatile
    │   │   │   │   ├── Architectural Role: UI Component
    │   │   │   │   ├── Critical Dependencies:
    │   │   │   │   └──   - ../../entities/cart/store: Provides the cart state and operations for managing cart items.
    │   │   │   └── QuantitySelector.tsx (TypeScript)
    │   │   │       ├── Description: Component for selecting and updating item quantities in the shopping cart.
    │   │   │       ├── Developer Consideration: Relies on the cart store for state management; ensure proper synchronization between the store and the component's rendering logic.
    │   │   │       ├── Maintenance Flag: Volatile
    │   │   │       └── Architectural Role: UI Component
    │   ├── App.css (CSS)
    │   ├── App.tsx (TypeScript)
    │   │   ├── Description: Main application component that defines the routing structure and layout for the frontend.
    │   │   ├── Developer Consideration: Protected routes rely on authentication state; ensure the auth store is properly initialized before rendering these routes.
    │   │   ├── Maintenance Flag: Stable
    │   │   ├── Architectural Role: Entrypoint
    │   │   ├── Security Assessment: Protected routes ensure unauthorized users cannot access sensitive pages; ensure all protected routes are properly configured.
    │   │   ├── Critical Dependencies:
    │   │   ├──   - ./features/auth/ProtectedRoute: Handles route protection based on authentication state.
    │   │   └──   - ./shared/ui/Layout: Provides consistent layout structure across all pages.
    │   ├── index.css (CSS)
    │   └── main.tsx (TypeScript)
    │       ├── Description: Entrypoint for the React application, rendering the root App component into the DOM.
    │       ├── Maintenance Flag: Stable
    │       ├── Architectural Role: Entrypoint
    │       ├── Critical Dependencies:
    │       └──   - react: Core library for building the React application's UI components.
    ├── .env.example (None)
    ├── .gitignore (None)
    ├── Dockerfile (None)
    ├── README.md (Markdown)
    ├── bun.lock (None)
    ├── eslint.config.js (JavaScript)
    ├── index.html (HTML)
    ├── package.json (JSON)
    ├── tsconfig.app.json (JSON)
    ├── tsconfig.json (JSON)
    ├── tsconfig.node.json (JSON)
    ├── vite.config.ts (TypeScript)
    │   └── Description: https://vite.dev/config/
    └── vitest.config.ts (TypeScript)
        ├── Description: Configuration file for Vitest, the testing framework used in the frontend application.
        ├── Maintenance Flag: Stable
        ├── Architectural Role: Tooling
        ├── Critical Dependencies:
        └──   - vitest/config: Core configuration module for Vitest, enabling test environment setup and customization.
├── .env.example (None)
├── .gitignore (None)
├── AGENTS.md (Markdown)
├── README.md (Markdown)
├── REPO_MAP.md (Markdown)
└── docker-compose.yml (YAML)
└────────────── 
```
