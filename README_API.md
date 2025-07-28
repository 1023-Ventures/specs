# ECS Auth API - Test Commands

## Server Status
curl http://localhost:8000/

## Register a new user
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser", 
    "email": "test@example.com", 
    "password": "password123"
  }'

## Login (get JWT token)
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser", 
    "password": "password123"
  }'

## Access protected profile (replace YOUR_TOKEN_HERE with actual token)
curl http://localhost:8000/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

## Access protected route (replace YOUR_TOKEN_HERE with actual token)
curl http://localhost:8000/protected \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

## Interactive Test (Python script)
# Run: uv run python test_auth.py
