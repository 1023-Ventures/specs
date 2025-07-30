# Database Setup Guide

## PostgreSQL Setup (Recommended)

### 1. Start PostgreSQL with Docker
```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Verify it's running
docker-compose ps
```

### 2. Set Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# The default PostgreSQL settings should work out of the box
export DATABASE_TYPE=postgresql
```

### 3. Install Dependencies
```bash
# Install PostgreSQL driver
uv add psycopg2-binary

# Or if you have the project dependencies already
uv sync
```

### 4. Run the Application
```bash
# The application will automatically use PostgreSQL
uv run main.py
```

### 5. Run Tests
```bash
# Tests will also use PostgreSQL
./tests/run_tests.sh
```

## SQLite Setup (Fallback)

If you prefer to stick with SQLite:

```bash
# Set environment variable
export DATABASE_TYPE=sqlite

# Or remove the DATABASE_TYPE variable entirely (SQLite is default)
uv run main.py
```

## Benefits of PostgreSQL

✅ **No Locking Issues**: Handles concurrent connections perfectly
✅ **Production Ready**: Same database you'd use in production
✅ **Better Performance**: Optimized for concurrent access
✅ **ACID Compliant**: Proper transaction handling
✅ **Scalable**: Can handle many simultaneous connections

## Database Management

### Connect to PostgreSQL
```bash
# Using Docker
docker exec -it specs_postgres psql -U specs_user -d specs_auth

# Or using psql directly
psql -h localhost -U specs_user -d specs_auth
```

### View Tables
```sql
\dt
SELECT * FROM users;
SELECT * FROM user_scopes;
SELECT * FROM user_environment_variables;
```

### Reset Database
```bash
# Stop and remove containers
docker-compose down -v

# Start fresh
docker-compose up -d postgres
```
