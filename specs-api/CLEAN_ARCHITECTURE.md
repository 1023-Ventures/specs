# ECS Auth API - Clean Architecture

## 📁 Organized Project Structure

```
ecs-api/
├── main.py                 # Legacy main file (keep for backward compatibility)
├── main_new.py            # New organized main file
├── pyproject.toml         # Project configuration
├── uv.lock               # Lock file
├── README_API.md         # API documentation
├── ARCHITECTURE.md       # Architecture documentation
├── auth.db               # SQLite database (auto-created)
│
├── app/                  # Main application package
│   ├── __init__.py
│   │
│   ├── api/              # API layer
│   │   ├── __init__.py
│   │   ├── api.py        # Main API router aggregator
│   │   └── v1/           # API version 1
│   │       ├── __init__.py
│   │       └── auth.py   # Authentication endpoints
│   │
│   ├── core/             # Core functionality
│   │   ├── __init__.py
│   │   └── database.py   # Database operations & JWT
│   │
│   ├── models/           # Data models
│   │   ├── __init__.py
│   │   └── auth.py       # Authentication models
│   │
│   └── services/         # Business logic services
│       ├── __init__.py
│       └── auth_service.py # Authentication service
│
└── tests/                # Test suite
    ├── __init__.py
    └── test_auth.py      # Authentication tests
```

## 🏗️ Architecture Layers

### **1. API Layer** (`app/api/`)
- **Purpose**: HTTP request/response handling
- **Responsibilities**:
  - Route definitions
  - Request validation
  - Response formatting
  - Dependency injection

### **2. Service Layer** (`app/services/`)
- **Purpose**: Business logic implementation
- **Responsibilities**:
  - Authentication workflows
  - Data validation and processing
  - Error handling
  - Orchestrating database operations

### **3. Core Layer** (`app/core/`)
- **Purpose**: Foundation components
- **Responsibilities**:
  - Database operations
  - JWT token management
  - Configuration
  - Utilities

### **4. Models Layer** (`app/models/`)
- **Purpose**: Data structures and validation
- **Responsibilities**:
  - Pydantic models
  - Request/response schemas
  - Data validation rules

## 🔄 Request Flow

```
HTTP Request → API Router → Service Layer → Core Layer → Database
                    ↓           ↓             ↓
              Response ← Business Logic ← Data Access
```

## ✅ Architecture Benefits

- **🎯 Separation of Concerns**: Each layer has a single responsibility
- **🧪 Testability**: Easy to unit test individual layers
- **🔧 Maintainability**: Changes are isolated to specific layers
- **📈 Scalability**: Easy to add new features and endpoints
- **🔄 Reusability**: Services can be shared across different endpoints
- **📚 Organization**: Clear structure makes code navigation intuitive

## 🚀 API Versioning

- **Current**: `/api/v1/` endpoints
- **Future**: Easy to add `/api/v2/` without breaking existing clients
- **Backward Compatibility**: Legacy endpoints still work

## 📋 Usage

### **Development**:
```bash
# Using new organized structure
uv run python main_new.py

# Or legacy structure (backward compatible)
uv run python main.py
```

### **Testing**:
```bash
# Run tests
uv run python tests/test_auth.py
```

### **API Documentation**:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎯 Next Steps

With this clean architecture, you can easily:
- Add new API versions
- Implement additional services (e.g., user management, permissions)
- Add comprehensive testing
- Implement caching layers
- Add monitoring and logging
- Scale individual components
