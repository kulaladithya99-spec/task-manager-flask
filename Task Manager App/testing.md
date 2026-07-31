# Testing

This project uses **pytest** to test routes, authentication, form validation, and data integrity.

## What This Covers

- Session-based authentication (Flask-Login)
- Token-based authentication (JWT)
- Form validation (Flask-WTF)
- CRUD operations on tasks
- Cross-user data access protection (ownership checks)

## Setup

Install test dependencies (already included in `requirements.txt`):

```bash
pip install pytest
```

Run the full test suite:

```bash
pytest
```

## Test Architecture

### Isolated Test Database

Tests run against an **in-memory SQLite database** (`sqlite:///:memory:`), completely separate from the real production database (`taskmanager.db`). This is configured via a `test_config` dictionary passed directly into the `create_app()` factory function, applied **before** `db.init_app(app)` runs.

```python
def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    ...
    if test_config:
        app.config.update(test_config)

    db.init_app(app)  # only initializes AFTER test_config is applied
    ...
```

### Fixture (`conftest.py`)

A shared `client` fixture spins up the app with test configuration and creates all tables fresh for every test run:

```python
@pytest.fixture
def client():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    }
    app = create_app(test_config=test_config)

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
```

## Test Coverage

| Test | What It Verifies |
|---|---|
| `test_login_page_loads` | Login route returns 200 |
| `test_login_with_valid_credentials` | Full session-based login flow succeeds |
| `test_add_task_requires_login` | Unauthenticated users are redirected (302), not allowed through |
| `test_add_task_empty_title_fails` | Flask-WTF validation blocks empty required fields |
| `test_jwt_login_and_protected_route` | JWT login issues a token; token grants access to a protected API route |
| `test_edit_task_success` | Editing a task updates the actual database row, not just the HTTP response |
| `test_edit_task_wrong_user_blocked` | A logged-in user cannot access or edit another user's task (returns 404) |

## Route-Testing Checklist

When adding a new test for any route, this project follows a consistent framework:

1. **Happy path** — does it work with valid input?
2. **Authentication** — is an unauthenticated request blocked correctly?
3. **Ownership** — can a different logged-in user access data that isn't theirs?
4. **Bad input** — are validation errors triggered correctly (empty fields, bad formats)?
5. **Non-existent resource** — does requesting a missing ID return 404, not crash?
6. **Database side effects** — does the underlying data actually change, not just the response code?

## Problem Encountered & Fixed: Test Data Leaking Into Production Database

**The bug:** Initially, the test fixture set `app.config['SQLALCHEMY_DATABASE_URI']` *after* calling `create_app()`. Since `create_app()` already calls `db.init_app(app)` internally, the database engine was bound to the **real** `DATABASE_URL` before the test config ever took effect. As a result, early test runs silently inserted fake user records directly into the production SQLite database.

**How it was caught:** A second test run failed with:
```
sqlite3.IntegrityError: UNIQUE constraint failed: user.email
```
This happened because the "test" user from the first run had already been written to the real database — not a temporary one.

**The fix:** `create_app()` was updated to accept an optional `test_config` parameter, applied **before** `db.init_app(app)` is called, ensuring the database engine is correctly bound to the in-memory test database from the start.

**Lesson:** Test isolation is not automatic — it depends on *when* configuration is applied relative to when extensions (like SQLAlchemy) initialize. A misconfigured test can silently corrupt real data without any obvious error until much later.

## Notes on Authentication Testing

This project supports two independent authentication mechanisms, tested differently:

- **Session-based (Flask-Login):** A test must first `POST /auth/login` to establish a session cookie. That cookie is automatically carried on subsequent requests made with the same test `client` object.
- **Token-based (JWT):** No session is involved. A test calls `POST /api/login` to receive a signed token, then manually attaches it as an `Authorization: Bearer <token>` header on each subsequent request. Each request is independently authenticated — nothing is "remembered" between calls.