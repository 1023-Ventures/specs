# ECS Auth API - Service Architecture

## 📁 Project Structure

```
ecs-api/
├── main.py              # FastAPI app entry point
├── auth_router.py       # HTTP endpoint routes/controllers
├── auth_service.py      # Business logic service layer
├── database.py          # Database operations and JWT handling
├── models.py            # Pydantic data models
├── test_auth.py         # API testing script
├── README_API.md        # API usage examples
└── auth.db              # SQLite database (auto-created)
```

## 🏗️ Architecture Overview

### **Layer Separation:**

1. **Router Layer** (`auth_router.py`)
   - Handles HTTP requests/responses
   - Route definitions and FastAPI dependencies
   - Input validation and response formatting

2. **Service Layer** (`auth_service.py`)
   - Contains business logic
   - Orchestrates database operations
   - Handles authentication logic and errors

3. **Data Layer** (`database.py`)
   - Direct database operations
   - User CRUD operations
   - JWT token creation and validation

4. **Model Layer** (`models.py`)
   - Pydantic data models
   - Request/response schemas
   - Data validation

## 🔄 Request Flow

```
HTTP Request → Router → Service → Database → Response
```

## ✅ Benefits of This Architecture

- **Separation of Concerns**: Each layer has a single responsibility
- **Testability**: Service logic can be tested independently
- **Maintainability**: Changes to business logic don't affect routing
- **Reusability**: Services can be used by multiple routers
- **Scalability**: Easy to add new features and endpoints

## 🚀 Usage

- **Start server**: `uv run python main.py` or press F5
- **Test API**: `uv run python test_auth.py`
- **View docs**: `http://localhost:8000/docs`
