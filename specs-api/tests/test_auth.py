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

def test_login_with_scopes():
    """Test user login with requested scopes"""
    login_data = {
        "username": "testuser",
        "password": "testpassword123",
        "scopes": ["read_profile", "write_profile", "read_users"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login with scopes successful: {token_data}")
            return token_data["access_token"]
        else:
            print(f"❌ Login with scopes failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login with scopes error: {e}")
        return None

def test_available_scopes():
    """Test getting available scopes"""
    try:
        response = requests.get(f"{BASE_URL}/scopes")
        if response.status_code == 200:
            scopes = response.json()
            print(f"✅ Available scopes: {scopes}")
            return True
        else:
            print(f"❌ Failed to get scopes: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Scopes error: {e}")
        return False

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

def test_user_scopes(token):
    """Test getting user's current scopes"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/me/scopes", headers=headers)
        if response.status_code == 200:
            print(f"✅ User scopes: {response.json()}")
            return True
        else:
            print(f"❌ Failed to get user scopes: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ User scopes error: {e}")
        return False

def test_scope_protected_routes(token):
    """Test scope-protected routes"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test users endpoint (requires read_users scope)
    try:
        response = requests.get(f"{BASE_URL}/users", headers=headers)
        if response.status_code == 200:
            print(f"✅ Users endpoint accessed: {response.json()}")
        elif response.status_code == 403:
            print(f"⚠️ Users endpoint forbidden (expected): {response.json()}")
        else:
            print(f"❌ Users endpoint error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Users endpoint error: {e}")
    
    # Test profile update (requires write_profile scope)
    try:
        response = requests.put(f"{BASE_URL}/profile", headers=headers)
        if response.status_code == 200:
            print(f"✅ Profile update accessed: {response.json()}")
        elif response.status_code == 403:
            print(f"⚠️ Profile update forbidden (expected): {response.json()}")
        else:
            print(f"❌ Profile update error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Profile update error: {e}")
    
    # Test admin endpoint (requires admin scope)
    try:
        response = requests.get(f"{BASE_URL}/admin", headers=headers)
        if response.status_code == 200:
            print(f"✅ Admin endpoint accessed: {response.json()}")
        elif response.status_code == 403:
            print(f"⚠️ Admin endpoint forbidden (expected): {response.json()}")
        else:
            print(f"❌ Admin endpoint error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Admin endpoint error: {e}")

def test_admin_login():
    """Test admin login to get admin token"""
    login_data = {
        "username": "admin",
        "password": "admin123",
        "scopes": ["admin", "read_users", "write_users", "read_profile", "write_profile"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Admin login successful: {token_data}")
            return token_data["access_token"]
        else:
            print(f"❌ Admin login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return None

def test_get_user_scopes_by_id(admin_token, user_id):
    """Test getting a user's scopes by ID (admin only)"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}/scopes", headers=headers)
        if response.status_code == 200:
            print(f"✅ User {user_id} scopes retrieved: {response.json()}")
            return response.json()
        elif response.status_code == 403:
            print(f"❌ Insufficient permissions to get user scopes: {response.json()}")
        elif response.status_code == 404:
            print(f"❌ User {user_id} not found: {response.json()}")
        else:
            print(f"❌ Get user scopes error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"❌ Get user scopes error: {e}")
        return None

def test_grant_scope_to_user(admin_token, user_id, scope):
    """Test granting a scope to a user (admin only)"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/users/{user_id}/scopes/{scope}", headers=headers)
        if response.status_code == 200:
            print(f"✅ Scope '{scope}' granted to user {user_id}: {response.json()}")
            return True
        elif response.status_code == 403:
            print(f"❌ Insufficient permissions to grant scope: {response.json()}")
        elif response.status_code == 400:
            print(f"❌ Failed to grant scope: {response.json()}")
        else:
            print(f"❌ Grant scope error: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        print(f"❌ Grant scope error: {e}")
        return False

def test_revoke_scope_from_user(admin_token, user_id, scope):
    """Test revoking a scope from a user (admin only)"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/users/{user_id}/scopes/{scope}", headers=headers)
        if response.status_code == 200:
            print(f"✅ Scope '{scope}' revoked from user {user_id}: {response.json()}")
            return True
        elif response.status_code == 403:
            print(f"❌ Insufficient permissions to revoke scope: {response.json()}")
        elif response.status_code == 400:
            print(f"❌ Failed to revoke scope: {response.json()}")
        else:
            print(f"❌ Revoke scope error: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        print(f"❌ Revoke scope error: {e}")
        return False

def test_list_all_users_with_scopes(admin_token):
    """Test listing all users with their scopes (admin only)"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/users/scopes", headers=headers)
        if response.status_code == 200:
            users_data = response.json()
            print(f"✅ All users with scopes retrieved: {users_data}")
            return users_data
        elif response.status_code == 403:
            print(f"❌ Insufficient permissions to list users: {response.json()}")
        else:
            print(f"❌ List users error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"❌ List users error: {e}")
        return None

def test_non_admin_scope_management(user_token, user_id):
    """Test that non-admin users cannot manage scopes"""
    headers = {"Authorization": f"Bearer {user_token}"}
    
    print("Testing scope management restrictions for non-admin users...")
    
    # Try to get another user's scopes
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}/scopes", headers=headers)
        if response.status_code == 403:
            print("✅ Non-admin correctly forbidden from viewing user scopes")
        else:
            print(f"❌ Non-admin should not access user scopes: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing non-admin restrictions: {e}")
    
    # Try to grant a scope
    try:
        response = requests.post(f"{BASE_URL}/users/{user_id}/scopes/read_profile", headers=headers)
        if response.status_code == 403:
            print("✅ Non-admin correctly forbidden from granting scopes")
        else:
            print(f"❌ Non-admin should not grant scopes: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing grant restrictions: {e}")
    
    # Try to revoke a scope
    try:
        response = requests.delete(f"{BASE_URL}/users/{user_id}/scopes/read_profile", headers=headers)
        if response.status_code == 403:
            print("✅ Non-admin correctly forbidden from revoking scopes")
        else:
            print(f"❌ Non-admin should not revoke scopes: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing revoke restrictions: {e}")
    
    # Try to list all users
    try:
        response = requests.get(f"{BASE_URL}/users/scopes", headers=headers)
        if response.status_code == 403:
            print("✅ Non-admin correctly forbidden from listing all users")
        else:
            print(f"❌ Non-admin should not list all users: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing list restrictions: {e}")

def run_comprehensive_scope_management_tests():
    """Run comprehensive tests for the new scope management features"""
    print("\n=== SCOPE MANAGEMENT TESTS ===\n")
    
    # First, try to get admin token
    print("1. Testing admin login...")
    admin_token = test_admin_login()
    
    if not admin_token:
        print("❌ Cannot test scope management without admin access")
        return
    
    # Get regular user token
    print("\n2. Getting regular user token...")
    user_token = test_login()
    
    if not user_token:
        print("❌ Cannot get regular user token")
        return
    
    # List all users to get user IDs
    print("\n3. Listing all users with scopes...")
    users_data = test_list_all_users_with_scopes(admin_token)
    
    if not users_data or not users_data:
        print("❌ No users found")
        return
    
    # Find the test user
    test_user_id = None
    for user in users_data:
        if user["username"] == "testuser":
            test_user_id = user["id"]
            break
    
    if test_user_id is None:
        print("❌ Test user not found")
        return
    
    print(f"\n4. Testing scope management for user ID: {test_user_id}")
    
    # Get user's current scopes
    print("\n5. Getting user's current scopes...")
    user_scopes = test_get_user_scopes_by_id(admin_token, test_user_id)
    
    # Test granting a new scope
    print("\n6. Testing scope granting...")
    test_grant_scope_to_user(admin_token, test_user_id, "write_users")
    
    # Verify the scope was granted
    print("\n7. Verifying scope was granted...")
    updated_scopes = test_get_user_scopes_by_id(admin_token, test_user_id)
    
    # Test revoking a scope
    print("\n8. Testing scope revocation...")
    test_revoke_scope_from_user(admin_token, test_user_id, "write_users")
    
    # Verify the scope was revoked
    print("\n9. Verifying scope was revoked...")
    final_scopes = test_get_user_scopes_by_id(admin_token, test_user_id)
    
    # Test non-admin restrictions
    print("\n10. Testing non-admin restrictions...")
    test_non_admin_scope_management(user_token, test_user_id)
    
    print("\n=== SCOPE MANAGEMENT TESTS COMPLETE ===")

def test_scope_validation_in_login():
    """Test that users can only request scopes they have access to"""
    print("\n=== SCOPE VALIDATION TESTS ===\n")
    
    # Test requesting valid scopes
    print("1. Testing login with valid scopes...")
    login_data = {
        "username": "testuser",
        "password": "testpassword123",
        "scopes": ["read_profile"]  # User should have this by default
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login with valid scopes successful")
        else:
            print(f"❌ Login with valid scopes failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Login with valid scopes error: {e}")
    
    # Test requesting invalid scopes
    print("\n2. Testing login with invalid scopes...")
    login_data = {
        "username": "testuser",
        "password": "testpassword123",
        "scopes": ["admin", "super_secret_scope"]  # User shouldn't have these
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 403 or response.status_code == 400:
            print("✅ Login with invalid scopes correctly rejected")
        else:
            print(f"❌ Login with invalid scopes should be rejected: {response.status_code}")
    except Exception as e:
        print(f"❌ Login with invalid scopes error: {e}")
    
    print("\n=== SCOPE VALIDATION TESTS COMPLETE ===\n")

if __name__ == "__main__":
    print("=== ECS Auth API Test ===\n")
    
    # Test if server is running
    if not test_server():
        print("\nPlease start the server with: uv run python main.py")
        exit(1)
    
    print("\n1. Testing available scopes...")
    test_available_scopes()
    
    print("\n2. Testing user registration...")
    test_register()
    
    print("\n3. Testing basic login...")
    token = test_login()
    
    print("\n4. Testing login with scopes...")
    scoped_token = test_login_with_scopes()
    
    if token:
        print("\n5. Testing protected routes with basic token...")
        test_protected_route(token)
        test_protected_example(token)
    
    if scoped_token:
        print("\n6. Testing user scopes...")
        test_user_scopes(scoped_token)
        
        print("\n7. Testing scope-protected routes...")
        test_scope_protected_routes(scoped_token)
    
    # Run new comprehensive scope management tests
    run_comprehensive_scope_management_tests()
    
    # Run scope validation tests
    test_scope_validation_in_login()
    
    print("\n=== Test Complete ===")
    print("\n💡 Scope Usage Examples:")
    print("• Login with scopes: POST /api/v1/login with 'scopes' array")
    print("• Available scopes: GET /api/v1/scopes")
    print("• Your scopes: GET /api/v1/me/scopes")
    print("• User scopes (admin): GET /api/v1/users/{id}/scopes")
    print("• Grant scope (admin): POST /api/v1/users/{id}/scopes/{scope}")
    print("• Revoke scope (admin): DELETE /api/v1/users/{id}/scopes/{scope}")
    print("• List all users (admin): GET /api/v1/users/scopes")
    print("• Scope-protected routes return 403 if insufficient permissions")
