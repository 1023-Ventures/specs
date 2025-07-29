# Testing the ECS Auth API

This document describes the testing setup for the ECS Auth API, particularly focusing on the new scope management functionality.

## Test Files

### 1. `tests/test_auth.py` - Integration Tests
A comprehensive integration test suite that tests the API by making actual HTTP requests to a running server.

**Features tested:**
- User registration and login
- Basic authentication
- Scope-based authentication  
- Protected routes with scope validation
- **NEW: Comprehensive scope management**
  - Admin login and token validation
  - Getting user scopes by ID (admin only)
  - Granting scopes to users (admin only)
  - Revoking scopes from users (admin only)
  - Listing all users with scopes (admin only)
  - Non-admin access restrictions
  - Scope validation during login

### 2. `tests/test_scope_management.py` - Pytest Unit Tests
Modern pytest-based tests using FastAPI's TestClient for faster, isolated testing.

**Test classes:**
- `TestScopeManagement`: Core scope management functionality
- `TestScopeIntegration`: End-to-end integration scenarios

### 3. `run_tests.sh` - Test Runner Script
A shell script that runs all tests in sequence and provides status feedback.

## Running Tests

### Prerequisites
1. **Start the server** first:
   ```bash
   uv run python main.py
   ```

2. **Install test dependencies** (optional, for pytest):
   ```bash
   uv add --group test pytest pytest-asyncio httpx
   ```

### Running All Tests
```bash
./run_tests.sh
```

### Running Individual Test Suites

**Integration tests (manual HTTP requests):**
```bash
/Users/mattw/1023-dev/springthrough/ecs/.venv/bin/python tests/test_auth.py
```

**Pytest tests (requires test dependencies):**
```bash
/Users/mattw/1023-dev/springthrough/ecs/.venv/bin/python -m pytest tests/test_scope_management.py -v
```

## New Scope Management API Endpoints Tested

The tests validate these new endpoints:

### User Scope Information
- `GET /api/v1/me/scopes` - Get current user's scopes
- `GET /api/v1/users/{id}/scopes` - Get specific user's scopes (admin only)

### Admin Scope Management  
- `POST /api/v1/users/{id}/scopes/{scope}` - Grant scope to user (admin only)
- `DELETE /api/v1/users/{id}/scopes/{scope}` - Revoke scope from user (admin only)
- `GET /api/v1/users/scopes` - List all users with their scopes (admin only)

### Scope Validation
- Login with scope requests validates user permissions
- Protected endpoints enforce scope requirements
- Non-admin users cannot manage scopes

## Test Scenarios Covered

### Basic Functionality
✅ Server connectivity and health checks  
✅ User registration and login  
✅ Token-based authentication  
✅ Protected route access  

### Scope System
✅ Available scopes listing  
✅ User scope information retrieval  
✅ Scope-based route protection  
✅ Login with requested scopes  

### **NEW: Scope Management (Admin Features)**
✅ Admin authentication with full scopes  
✅ Viewing user scope assignments  
✅ Granting new scopes to users  
✅ Revoking scopes from users  
✅ Comprehensive user and scope listing  
✅ Access control validation (non-admin restrictions)  
✅ Scope validation during login process  

### Integration Scenarios
✅ Complete user lifecycle with scope changes  
✅ Cross-user scope management operations  
✅ Permission validation across endpoints  
✅ Token refresh with updated scopes  

## Test Output Examples

### Successful Admin Scope Grant
```
✅ Scope 'write_users' granted to user 2: {'message': "Scope 'write_users' granted to user 2"}
```

### Non-Admin Access Restriction
```
✅ Non-admin correctly forbidden from granting scopes
```

### Scope Validation in Login
```
✅ Login with valid scopes successful
✅ Login with invalid scopes correctly rejected
```

## Database State After Tests

The tests create and modify the following data:
- Test users with various scope assignments
- Admin user with full permissions
- Scope grant/revoke history
- User permission matrices

All test data is persistent and will remain in the SQLite database after test runs.

## Troubleshooting

### Server Not Running
```
❌ Server is not running!
Please start the server first: uv run python main.py
```

### Admin Login Failed
If admin tests fail, ensure the default admin user exists:
- Username: `admin`
- Password: `admin123`
- Default scopes: `admin`, `read_users`, `write_users`, etc.

### Scope Permission Errors
If scope tests fail unexpectedly, check:
1. Database schema is up to date
2. Default admin user has all required scopes
3. User being tested exists in the database

### Test Dependencies Missing
For pytest tests, install dependencies:
```bash
uv add --group test pytest pytest-asyncio httpx
```
