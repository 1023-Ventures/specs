# ECS Auth API

A modern, clean architecture authentication API built with FastAPI, SQLite, and JWT tokens.

## 🚀 Features

- **JWT Authentication** - Secure token-based authentication
- **User Management** - Registration, login, and profile management
- **SQLite Database** - Lightweight, embedded database
- **Clean Architecture** - Well-organized, scalable code structure
- **API Versioning** - `/api/v1/` structure for future expansion
- **Password Security** - Bcrypt hashing for passwords
- **FastAPI** - Modern, fast web framework with automatic API docs

## 📁 Project Structure

```
ecs-api/
├── app/                    # Main application package
│   ├── api/               # API layer (HTTP endpoints)  
│   │   ├── api.py         # Router aggregator
│   │   └── v1/            # API version 1
│   │       └── auth.py    # Authentication endpoints
│   │
│   ├── services/          # Business logic services
│   │   └── auth_service.py # Authentication service
│   │
│   ├── core/              # Core functionality  
│   │   └── database.py    # Database & JWT operations
│   │
│   └── models/            # Data models
│       └── auth.py        # Authentication models
│
├── tests/                 # Test suite
│   └── test_auth.py       # API tests
│
├── main.py                # Application entry point
├── pyproject.toml         # Project dependencies
└── README.md              # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ecs-auth-api.git
   cd ecs-auth-api
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Run the server**
   ```bash
   uv run python main.py
   ```

4. **Test the API**
   ```bash
   uv run python tests/test_auth.py
   ```

## 🌐 API Endpoints

### Base URL: `http://localhost:8000`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Health check | No |
| GET | `/docs` | API documentation | No |
| POST | `/api/v1/register` | Register new user | No |
| POST | `/api/v1/login` | Login user | No |
| GET | `/api/v1/profile` | Get user profile | Yes |
| GET | `/api/v1/protected` | Protected route example | Yes |

## 📝 Usage Examples

### Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123"
  }'
```

### Access protected route
```bash
curl http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🧪 Testing

Run the test suite:
```bash
uv run python tests/test_auth.py
```

## 🏗️ Architecture

The project follows clean architecture principles:

- **API Layer** (`app/api/`): HTTP request/response handling
- **Service Layer** (`app/services/`): Business logic
- **Core Layer** (`app/core/`): Data access and utilities
- **Models** (`app/models/`): Data structures and validation

## 🔧 Development

### VS Code Setup
- Press `F5` to run/debug the server
- Built-in launch configurations available
- Automatic environment setup with uv

### Adding New Features
1. Add models in `app/models/`
2. Implement business logic in `app/services/`
3. Create API endpoints in `app/api/v1/`
4. Write tests in `tests/`

## 📋 Requirements

See `pyproject.toml` for full dependency list. Key dependencies:
- FastAPI
- Uvicorn (ASGI server)
- SQLite3 (built-in)
- python-jose (JWT)
- passlib (password hashing)
- bcrypt (encryption)

## 🔒 Security

- Passwords hashed with bcrypt
- JWT tokens with 30-minute expiry
- Bearer token authentication
- Input validation with Pydantic

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions or issues, please open a GitHub issue.
