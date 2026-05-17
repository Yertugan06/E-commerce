# Authentication Flow

## Overview

The auth system uses JWT (JSON Web Tokens) for stateless authentication. Passwords are hashed with bcrypt via passlib. Tokens are stored in the frontend's `localStorage` and sent via `Authorization: Bearer` header.

---

## Backend

### Registration Flow

1. Client sends `POST /auth/register` with `{ email, password }`
2. Backend checks if email already exists → `409 Conflict` if duplicate
3. Password is hashed via `passlib.context.CryptContext` (bcrypt)
4. User is created in the `users` table
5. JWT is generated with `sub = user.id` and 30-minute expiry
6. Response: `{ access_token, token_type: "bearer", user: { id, email, role, created_at } }`

### Login Flow

1. Client sends `POST /auth/login` with `{ email, password }`
2. Backend fetches user by email → `401 Unauthorized` if not found
3. Verifies password hash → `401 Unauthorized` if mismatch
4. JWT generated same as registration
5. Response matches registration response

### Token Verification (GET /auth/me)

1. Client sends `GET /auth/me` with `Authorization: Bearer <token>`
2. Backend decodes JWT using `python-jose` with `HS256` algorithm
3. Extracts `sub` claim (user ID), queries `users` table
4. Returns `UserRead` schema if valid
5. Returns `401` if token expired, malformed, or user deleted

### JWT Structure

```json
{
  "sub": "1",
  "exp": 1716000000
}
```

| Claim | Value | Description |
|-------|-------|-------------|
| `sub` | user ID (string) | Subject — identifies the user |
| `exp` | Unix timestamp | Expiration time |

### Key Files

| File | Purpose |
|------|---------|
| `app/core/security.py` | `create_access_token()`, `verify_password()`, `get_password_hash()` |
| `app/core/dependencies.py` | `get_current_user()` — FastAPI dependency that extracts & validates JWT |
| `app/features/auth/router.py` | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| `app/features/auth/use_cases.py` | Business logic for register/login |
| `app/features/auth/schemas.py` | Request/response Pydantic models |
| `app/features/users/repositories.py` | DB queries for user CRUD |
| `app/features/users/models.py` | SQLModel `User` table definition |

---

## Frontend

### Token Storage

- Token and user data are stored in `localStorage` under keys `token` and `user`
- Zustand `useAuthStore` hydrates from `localStorage` on initialization
- `login(token, user)` persists both and updates reactive state
- `logout()` clears both from `localStorage` and state

### API Client Interceptor

- `src/shared/api/client.ts` — Axios instance with:
  - `baseURL` from `VITE_API_URL` env var
  - Request interceptor: attaches `Authorization: Bearer <token>` from localStorage
  - Response interceptor: on `401`, clears localStorage and redirects to `/login`

### Protected Routes

- `src/features/auth/ProtectedRoute.tsx` checks `useAuthStore.token`
- If no token → `<Navigate to="/login" replace />`
- If token exists → renders `<Outlet />` for child routes
- Currently protected routes: `/products`, `/cart`

### Login Page

- `src/features/auth/LoginForm.tsx`
- Sends `POST /auth/login` with email/password
- On success: calls `useAuthStore.login(token, user)` → redirects to `/`
- On error: displays server error message

### Register Page

- `src/features/auth/RegisterForm.tsx`
- Sends `POST /auth/register` with email/password/confirm
- On success: calls `useAuthStore.login(token, user)` → redirects to `/`
- On error: displays server error message
- Client-side password confirmation check before submission

### Key Files

| File | Purpose |
|------|---------|
| `src/entities/auth/store.ts` | Zustand store: token, user, login(), logout() |
| `src/shared/api/client.ts` | Axios instance with auth interceptors |
| `src/features/auth/LoginForm.tsx` | Login form component |
| `src/features/auth/RegisterForm.tsx` | Registration form component |
| `src/features/auth/ProtectedRoute.tsx` | Route guard component |
| `src/App.tsx` | Route configuration with protected routes |
| `src/pages/Login.tsx` | Page wrapper for LoginForm |
| `src/pages/Register.tsx` | Page wrapper for RegisterForm |

---

## Security Considerations

- Passwords are hashed with bcrypt (never stored in plaintext)
- JWT secret key must be a strong random value in production
- Token expiry is 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- No refresh tokens in MVP — re-login required after expiry
- HTTPS required in production to prevent token interception
