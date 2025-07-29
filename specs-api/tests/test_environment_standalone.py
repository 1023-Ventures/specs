#!/usr/bin/env python3
"""
Test script for the Environment Variables API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    """Get admin token for testing"""
    login_data = {
        "username": "admin",
        "password": "admin123",
        "scopes": ["admin"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"❌ Failed to get admin token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def cleanup_test_vars(token):
    """Clean up test environment variables"""
    headers = {"Authorization": f"Bearer {token}"}
    test_vars = ["TEST_VAR_1", "TEST_VAR_2", "TEST_UPDATE_VAR", "TEST_DELETE_VAR"]
    
    for var_name in test_vars:
        try:
            requests.delete(f"{BASE_URL}/environment-variables/{var_name}", headers=headers)
        except:
            pass  # Ignore errors during cleanup

def test_server():
    """Test if the server is running"""
    try:
        response = requests.get("http://localhost:8000/")
        print(f"✅ Server is running: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start it first.")
        return False

def test_get_empty_environment_variables(token):
    """Test getting environment variables when none exist"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Clean up first
    cleanup_test_vars(token)
    
    try:
        response = requests.get(f"{BASE_URL}/environment-variables/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Filter out any non-test variables
            test_variables = [var for var in data["variables"] if var["name"].startswith("TEST_")]
            
            if len(test_variables) == 0:
                print(f"✅ Empty environment variables list: {data}")
                return True
            else:
                print(f"⚠️ Expected empty list, got {len(test_variables)} test variables")
                return False
        else:
            print(f"❌ Failed to get environment variables: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get environment variables failed: {e}")
        return False

def test_create_environment_variable(token):
    """Test creating a new environment variable"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    env_var_data = {
        "name": "TEST_VAR_1",
        "value": "test_value_1"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/environment-variables/", 
                               json=env_var_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if (data["name"] == "TEST_VAR_1" and 
                data["value"] == "test_value_1" and 
                data["username"] == "admin"):
                print(f"✅ Environment variable created: {data}")
                return True
            else:
                print(f"⚠️ Unexpected response data: {data}")
                return False
        else:
            print(f"❌ Failed to create environment variable: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Create environment variable failed: {e}")
        return False

def test_get_specific_environment_variable(token):
    """Test getting a specific environment variable"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # First create the variable
    env_var_data = {
        "name": "TEST_VAR_2",
        "value": "test_value_2"
    }
    
    try:
        create_response = requests.post(f"{BASE_URL}/environment-variables/", 
                                      json=env_var_data, headers=headers)
        if create_response.status_code != 200:
            print(f"❌ Failed to create test variable: {create_response.status_code}")
            return False
        
        # Now get the specific variable
        response = requests.get(f"{BASE_URL}/environment-variables/TEST_VAR_2", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if (data["name"] == "TEST_VAR_2" and 
                data["value"] == "test_value_2" and
                "created_at" in data and "updated_at" in data):
                print(f"✅ Got specific environment variable: {data}")
                return True
            else:
                print(f"⚠️ Unexpected response data: {data}")
                return False
        else:
            print(f"❌ Failed to get specific environment variable: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get specific environment variable failed: {e}")
        return False

def test_get_all_environment_variables(token):
    """Test getting all environment variables"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Create a couple of test variables first
    test_vars = [
        {"name": "TEST_VAR_1", "value": "value_1"},
        {"name": "TEST_VAR_2", "value": "value_2"}
    ]
    
    try:
        for var in test_vars:
            requests.post(f"{BASE_URL}/environment-variables/", json=var, headers=headers)
        
        response = requests.get(f"{BASE_URL}/environment-variables/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Filter for test variables
            test_variables = [var for var in data["variables"] if var["name"].startswith("TEST_")]
            
            if len(test_variables) >= 2 and data["username"] == "admin":
                var_names = [var["name"] for var in test_variables]
                if "TEST_VAR_1" in var_names and "TEST_VAR_2" in var_names:
                    print(f"✅ Got all environment variables: {len(test_variables)} test variables found")
                    return True
                else:
                    print(f"⚠️ Missing expected test variables: {var_names}")
                    return False
            else:
                print(f"⚠️ Expected at least 2 test variables, got {len(test_variables)}")
                return False
        else:
            print(f"❌ Failed to get all environment variables: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get all environment variables failed: {e}")
        return False

def test_update_environment_variable(token):
    """Test updating an environment variable"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Create initial variable
    env_var_data = {
        "name": "TEST_UPDATE_VAR",
        "value": "initial_value"
    }
    
    try:
        create_response = requests.post(f"{BASE_URL}/environment-variables/", 
                                      json=env_var_data, headers=headers)
        if create_response.status_code != 200:
            print(f"❌ Failed to create test variable: {create_response.status_code}")
            return False
        
        # Update the variable using POST
        updated_data = {
            "name": "TEST_UPDATE_VAR",
            "value": "updated_value"
        }
        
        response = requests.post(f"{BASE_URL}/environment-variables/", 
                               json=updated_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["value"] == "updated_value":
                print(f"✅ Environment variable updated via POST: {data}")
                
                # Test PUT method too
                put_data = {
                    "name": "TEST_UPDATE_VAR",
                    "value": "put_updated_value"
                }
                
                put_response = requests.put(f"{BASE_URL}/environment-variables/TEST_UPDATE_VAR", 
                                          json=put_data, headers=headers)
                if put_response.status_code == 200 and put_response.json()["value"] == "put_updated_value":
                    print(f"✅ Environment variable updated via PUT: {put_response.json()}")
                    return True
                else:
                    print(f"❌ PUT update failed: {put_response.status_code} - {put_response.text}")
                    return False
            else:
                print(f"⚠️ Unexpected updated value: {data}")
                return False
        else:
            print(f"❌ Failed to update environment variable: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Update environment variable failed: {e}")
        return False

def test_delete_environment_variable(token):
    """Test deleting an environment variable"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Create a variable to delete
    env_var_data = {
        "name": "TEST_DELETE_VAR",
        "value": "to_be_deleted"
    }
    
    try:
        create_response = requests.post(f"{BASE_URL}/environment-variables/", 
                                      json=env_var_data, headers=headers)
        if create_response.status_code != 200:
            print(f"❌ Failed to create test variable: {create_response.status_code}")
            return False
        
        # Delete the variable
        response = requests.delete(f"{BASE_URL}/environment-variables/TEST_DELETE_VAR", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["name"] == "TEST_DELETE_VAR" and "deleted successfully" in data["message"]:
                print(f"✅ Environment variable deleted: {data}")
                
                # Verify it's deleted by trying to get it
                get_response = requests.get(f"{BASE_URL}/environment-variables/TEST_DELETE_VAR", headers=headers)
                if get_response.status_code == 404:
                    print("✅ Confirmed variable is deleted (404 when trying to get it)")
                    return True
                else:
                    print(f"⚠️ Variable should be deleted but still accessible: {get_response.status_code}")
                    return False
            else:
                print(f"⚠️ Unexpected delete response: {data}")
                return False
        else:
            print(f"❌ Failed to delete environment variable: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Delete environment variable failed: {e}")
        return False

def test_error_cases(token):
    """Test error cases"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        # Test getting non-existent variable
        response = requests.get(f"{BASE_URL}/environment-variables/NONEXISTENT_VAR", headers=headers)
        if response.status_code == 404:
            print("✅ Non-existent variable returns 404")
        else:
            print(f"⚠️ Expected 404 for non-existent variable, got {response.status_code}")
            return False
        
        # Test deleting non-existent variable
        response = requests.delete(f"{BASE_URL}/environment-variables/NONEXISTENT_VAR", headers=headers)
        if response.status_code == 404:
            print("✅ Deleting non-existent variable returns 404")
        else:
            print(f"⚠️ Expected 404 for deleting non-existent variable, got {response.status_code}")
            return False
        
        # Test PUT with mismatched names
        put_data = {"name": "DIFFERENT_NAME", "value": "some_value"}
        response = requests.put(f"{BASE_URL}/environment-variables/TEST_VAR_NAME", 
                              json=put_data, headers=headers)
        if response.status_code == 400:
            print("✅ PUT with mismatched names returns 400")
        else:
            print(f"⚠️ Expected 400 for mismatched names, got {response.status_code}")
            return False
        
        # Test unauthorized access
        response = requests.get(f"{BASE_URL}/environment-variables/")
        if response.status_code in [401, 403]:
            print("✅ Unauthorized access properly rejected")
        else:
            print(f"⚠️ Expected 401/403 for unauthorized access, got {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error cases test failed: {e}")
        return False

def main():
    """Run all environment variables tests"""
    print("=== Environment Variables API Tests ===")
    
    # Test server availability
    if not test_server():
        print("❌ Server not available. Exiting.")
        return
    
    # Get admin token
    print("\n1. Getting admin token...")
    token = get_admin_token()
    if not token:
        print("❌ Failed to get admin token. Exiting.")
        return
    
    print("✅ Got admin token")
    
    # Run tests
    tests = [
        ("Testing empty environment variables", test_get_empty_environment_variables),
        ("Testing create environment variable", test_create_environment_variable),
        ("Testing get specific environment variable", test_get_specific_environment_variable),
        ("Testing get all environment variables", test_get_all_environment_variables),
        ("Testing update environment variable", test_update_environment_variable),
        ("Testing delete environment variable", test_delete_environment_variable),
        ("Testing error cases", test_error_cases),
    ]
    
    passed = 0
    total = len(tests)
    
    for i, (description, test_func) in enumerate(tests, 2):
        print(f"\n{i}. {description}...")
        if test_func(token):
            passed += 1
        else:
            print(f"❌ Test failed: {description}")
    
    # Cleanup
    print(f"\n{len(tests) + 2}. Cleaning up test variables...")
    cleanup_test_vars(token)
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️ {total - passed} test(s) failed")
    
    print("\n💡 Environment Variables API Usage:")
    print("• Get all: GET /api/v1/environment-variables/")
    print("• Get specific: GET /api/v1/environment-variables/{name}")
    print("• Create/Update: POST /api/v1/environment-variables/")
    print("• Update specific: PUT /api/v1/environment-variables/{name}")
    print("• Delete: DELETE /api/v1/environment-variables/{name}")
    print("• All endpoints require Authorization: Bearer <token>")

if __name__ == "__main__":
    main()
