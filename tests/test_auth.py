#!/usr/bin/env python3
"""
Test script for the ECS Auth API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_server():
    """Test if the server is running"""
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/")
        print(f"✅ Server is running: {response.json()}")
        
        # Test API health endpoint
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ API endpoint is running: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start it first.")
        return False

def test_register():
    """Test user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=user_data)
        if response.status_code == 200:
            print(f"✅ User registered: {response.json()}")
            return True
        else:
            print(f"⚠️ Registration response: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

def test_login():
    """Test user login"""
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login successful: {token_data}")
            return token_data["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_protected_route(token):
    """Test protected route with token"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/profile", headers=headers)
        if response.status_code == 200:
            print(f"✅ Profile accessed: {response.json()}")
            return True
        else:
            print(f"❌ Profile access failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Profile access error: {e}")
        return False

def test_protected_example(token):
    """Test example protected route"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/protected", headers=headers)
        if response.status_code == 200:
            print(f"✅ Protected route accessed: {response.json()}")
            return True
        else:
            print(f"❌ Protected route failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Protected route error: {e}")
        return False

if __name__ == "__main__":
    print("=== ECS Auth API Test ===\n")
    
    # Test if server is running
    if not test_server():
        print("\nPlease start the server with: uv run python main.py")
        exit(1)
    
    print("\n1. Testing user registration...")
    test_register()
    
    print("\n2. Testing user login...")
    token = test_login()
    
    if token:
        print("\n3. Testing protected routes...")
        test_protected_route(token)
        test_protected_example(token)
    
    print("\n=== Test Complete ===")
