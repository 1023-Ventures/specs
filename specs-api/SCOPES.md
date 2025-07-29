# 🔒 OAuth-Style Scopes Documentation

Your ECS Auth API now supports OAuth-style scopes for fine-grained authorization control!

## 🎯 What are Scopes?

Scopes are permissions that define what actions a user can perform. When logging in, users can request specific scopes, and only the approved scopes are embedded in their JWT token.

## 📋 Available Scopes

| Scope | Description | Access Level |
|-------|-------------|--------------|
| `read_profile` | Read user profile information | Basic users |
| `write_profile` | Modify user profile information | Basic users |
| `read_users` | Read other users' information | Advanced users |
| `admin` | Administrative access | Admin only |

## 🔑 How to Use Scopes

### 1. **Login with Requested Scopes**

```bash
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "password123",
    "scopes": ["read_profile", "write_profile", "read_users"]
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "scopes": ["read_profile", "write_profile"]
}
```

*Note: The response only includes approved scopes. Some requested scopes may be denied based on user permissions.*

### 2. **Get Available Scopes**

```bash
curl http://localhost:8000/api/v1/scopes
```

**Response:**
```json
{
  "read_profile": "Read user profile information",
  "write_profile": "Modify user profile information",
  "read_users": "Read other users' information",
  "admin": "Administrative access"
}
```

### 3. **Check Your Current Scopes**

```bash
curl http://localhost:8000/api/v1/me/scopes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "username": "john_doe",
  "scopes": ["read_profile", "write_profile"]
}
```

## 🛡️ Scope-Protected Endpoints

### **Profile Management**

| Endpoint | Method | Required Scope | Description |
|----------|---------|----------------|-------------|
| `/api/v1/profile` | GET | `read_profile` | Get user profile |
| `/api/v1/profile` | PUT | `write_profile` | Update user profile |

### **User Management**

| Endpoint | Method | Required Scope | Description |
|----------|---------|----------------|-------------|
| `/api/v1/users` | GET | `read_users` | List all users |

### **Administration**

| Endpoint | Method | Required Scope | Description |
|----------|---------|----------------|-------------|
| `/api/v1/admin` | GET | `admin` | Admin dashboard |

### **No Scope Required**

| Endpoint | Method | Auth Required | Description |
|----------|---------|---------------|-------------|
| `/api/v1/` | GET | No | Health check |
| `/api/v1/scopes` | GET | No | Available scopes |
| `/api/v1/register` | POST | No | User registration |
| `/api/v1/login` | POST | No | User login |
| `/api/v1/protected` | GET | Yes | Basic protected route |

## ⚠️ Error Responses

### **403 Forbidden - Insufficient Permissions**

```json
{
  "detail": "Insufficient permissions. Required scope: read_users"
}
```

### **401 Unauthorized - Invalid Token**

```json
{
  "detail": "Could not validate credentials"
}
```

## 🔧 Implementation Details

### **JWT Token Structure**

Your JWT tokens now include scopes in the payload:

```json
{
  "sub": "john_doe",
  "scopes": ["read_profile", "write_profile"],
  "exp": 1640995200
}
```

### **Scope Validation Logic**

1. **User requests scopes** during login
2. **System validates** requested scopes against user permissions
3. **Approved scopes** are embedded in JWT token
4. **Each protected endpoint** checks for required scopes
5. **Access denied** if user lacks required scope

### **Admin Scope Logic**

Currently, admin scope is only granted to users with username "admin". You can customize this logic in `database.py`:

```python
def validate_scopes(self, requested_scopes: list, user: dict) -> list:
    # Custom admin logic here
    if scope == "admin":
        if user.get("username") == "admin":  # Customize this condition
            valid_scopes.append(scope)
```

## 🚀 Testing Scopes

Run the comprehensive test suite:

```bash
uv run python tests/test_auth.py
```

This will test:
- ✅ Available scopes endpoint
- ✅ Login with requested scopes
- ✅ Scope validation in JWT tokens
- ✅ Protected endpoints with scope requirements
- ✅ Proper 403 responses for insufficient permissions

## 💡 Best Practices

1. **Principle of Least Privilege**: Request only the scopes you need
2. **Scope Granularity**: Use specific scopes rather than broad permissions
3. **Token Refresh**: Implement token refresh for long-running applications
4. **Scope Documentation**: Always document what each scope allows
5. **User Consent**: In production, show users what permissions they're granting

## 🔮 Future Enhancements

Possible additions to the scope system:
- User role-based scope assignment
- Scope hierarchies (admin includes all other scopes)
- Dynamic scope requests
- Scope-based rate limiting
- Audit logging for scope usage

---

🎉 **Your API now has enterprise-grade authorization with OAuth-style scopes!**
