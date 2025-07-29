#!/bin/bash

# Test runner script for ECS Auth API
echo "=== ECS Auth API Test Runner ==="

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
/Users/mattw/1023-dev/springthrough/ecs/.venv/bin/python tests/test_auth.py

# If pytest is available, run pytest tests
if command -v pytest &> /dev/null; then
    echo ""
    echo "=== Running Pytest Tests ==="
    /Users/mattw/1023-dev/springthrough/ecs/.venv/bin/python -m pytest tests/test_scope_management.py -v
else
    echo ""
    echo "ℹ️  Pytest not available - install with: uv add --group test pytest pytest-asyncio httpx"
fi

echo ""
echo "=== Test Run Complete ==="
