#!/bin/bash

# Test runner script for ECS Auth API
echo "=== ECS Auth API Test Runner ==="

# Change to the project root directory (one level up from tests/)
cd "$(dirname "$0")/.."

# Check if the server is running
if ! curl -f http://localhost:8000/ &>/dev/null; then
    echo "❌ Server is not running!"
    echo "Please start the server first:"
    echo "  uv run python main.py"
    exit 1
fi

echo "✅ Server is running"

# Run the manual integration tests
echo ""
echo "=== Running Integration Tests ==="
uv run python tests/test_auth.py

# Run the standalone environment tests
echo ""
echo "=== Running Environment Variables Tests ==="
uv run python tests/test_environment_standalone.py

# Run pytest tests if available
echo ""
echo "=== Running Pytest Tests ==="
if uv run pytest --version &>/dev/null; then
    echo "Running scope management tests..."
    uv run pytest tests/test_scope_management.py -v
    
    echo ""
    echo "Running environment variables pytest tests..."
    uv run pytest tests/test_environment_variables.py -v
else
    echo "ℹ️  Pytest not available - install with: uv sync --extra test"
fi

echo ""
echo "=== Test Run Complete ==="
