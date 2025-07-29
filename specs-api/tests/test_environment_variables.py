import pytest
import requests
import json
from datetime import datetime


class TestEnvironmentVariables:
    """Test suite for Environment Variables API endpoints"""
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    @classmethod
    def setup_class(cls):
        """Setup test data - login and get token"""
        # Login as admin to get token
        login_data = {
            "username": "admin",
            "password": "admin123",
            "scopes": ["admin"]
        }
        
        response = requests.post(f"{cls.BASE_URL}/login", json=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        cls.token = token_data["access_token"]
        cls.headers = {
            "Authorization": f"Bearer {cls.token}",
            "Content-Type": "application/json"
        }
        
        # Clean up any existing test environment variables
        cls.cleanup_test_vars()
    
    @classmethod
    def cleanup_test_vars(cls):
        """Clean up test environment variables"""
        test_vars = ["TEST_VAR_1", "TEST_VAR_2", "TEST_UPDATE_VAR", "TEST_DELETE_VAR"]
        
        for var_name in test_vars:
            try:
                requests.delete(f"{cls.BASE_URL}/environment-variables/{var_name}", headers=cls.headers)
            except:
                pass  # Ignore errors during cleanup
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after all tests"""
        cls.cleanup_test_vars()
    
    def test_get_empty_environment_variables(self):
        """Test getting environment variables when none exist"""
        # Clean up first
        self.cleanup_test_vars()
        
        response = requests.get(f"{self.BASE_URL}/environment-variables/", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Filter out any non-test variables
        test_variables = [var for var in data["variables"] if var["name"].startswith("TEST_")]
        
        assert len(test_variables) == 0
        assert "username" in data
        assert data["username"] == "admin"
    
    def test_create_environment_variable(self):
        """Test creating a new environment variable"""
        env_var_data = {
            "name": "TEST_VAR_1",
            "value": "test_value_1"
        }
        
        response = requests.post(f"{self.BASE_URL}/environment-variables/", 
                               json=env_var_data, headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Environment variable 'TEST_VAR_1' set successfully"
        assert data["name"] == "TEST_VAR_1"
        assert data["value"] == "test_value_1"
        assert data["username"] == "admin"
    
    def test_get_specific_environment_variable(self):
        """Test getting a specific environment variable"""
        # First create the variable
        env_var_data = {
            "name": "TEST_VAR_2",
            "value": "test_value_2"
        }
        
        create_response = requests.post(f"{self.BASE_URL}/environment-variables/", 
                                      json=env_var_data, headers=self.headers)
        assert create_response.status_code == 200
        
        # Now get the specific variable
        response = requests.get(f"{self.BASE_URL}/environment-variables/TEST_VAR_2", 
                              headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "TEST_VAR_2"
        assert data["value"] == "test_value_2"
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_get_all_environment_variables(self):
        """Test getting all environment variables"""
        # Create a couple of test variables first
        test_vars = [
            {"name": "TEST_VAR_1", "value": "value_1"},
            {"name": "TEST_VAR_2", "value": "value_2"}
        ]
        
        for var in test_vars:
            requests.post(f"{self.BASE_URL}/environment-variables/", 
                         json=var, headers=self.headers)
        
        response = requests.get(f"{self.BASE_URL}/environment-variables/", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Filter for test variables
        test_variables = [var for var in data["variables"] if var["name"].startswith("TEST_")]
        
        assert len(test_variables) >= 2
        assert data["total_count"] >= 2
        assert data["username"] == "admin"
        
        # Check that our test variables are in the response
        var_names = [var["name"] for var in test_variables]
        assert "TEST_VAR_1" in var_names
        assert "TEST_VAR_2" in var_names
    
    def test_update_environment_variable_with_post(self):
        """Test updating an existing environment variable using POST"""
        # Create initial variable
        env_var_data = {
            "name": "TEST_UPDATE_VAR",
            "value": "initial_value"
        }
        
        create_response = requests.post(f"{self.BASE_URL}/environment-variables/", 
                                      json=env_var_data, headers=self.headers)
        assert create_response.status_code == 200
        
        # Update the variable
        updated_data = {
            "name": "TEST_UPDATE_VAR",
            "value": "updated_value"
        }
        
        response = requests.post(f"{self.BASE_URL}/environment-variables/", 
                               json=updated_data, headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Environment variable 'TEST_UPDATE_VAR' set successfully"
        assert data["name"] == "TEST_UPDATE_VAR"
        assert data["value"] == "updated_value"
        
        # Verify the update by getting the variable
        get_response = requests.get(f"{self.BASE_URL}/environment-variables/TEST_UPDATE_VAR", 
                                   headers=self.headers)
        assert get_response.status_code == 200
        assert get_response.json()["value"] == "updated_value"
    
    def test_update_environment_variable_with_put(self):
        """Test updating an environment variable using PUT"""
        # Create initial variable
        env_var_data = {
            "name": "TEST_UPDATE_VAR",
            "value": "initial_value"
        }
        
        create_response = requests.post(f"{self.BASE_URL}/environment-variables/", 
                                      json=env_var_data, headers=self.headers)
        assert create_response.status_code == 200
        
        # Update using PUT
        updated_data = {
            "name": "TEST_UPDATE_VAR",
            "value": "put_updated_value"
        }
        
        response = requests.put(f"{self.BASE_URL}/environment-variables/TEST_UPDATE_VAR", 
                              json=updated_data, headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Environment variable 'TEST_UPDATE_VAR' set successfully"
        assert data["value"] == "put_updated_value"
    
    def test_put_with_mismatched_names(self):
        """Test PUT with mismatched names in URL and body"""
        updated_data = {
            "name": "DIFFERENT_NAME",
            "value": "some_value"
        }
        
        response = requests.put(f"{self.BASE_URL}/environment-variables/TEST_VAR_NAME", 
                              json=updated_data, headers=self.headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "name in URL must match name in request body" in data["detail"]
    
    def test_delete_environment_variable(self):
        """Test deleting an environment variable"""
        # Create a variable to delete
        env_var_data = {
            "name": "TEST_DELETE_VAR",
            "value": "to_be_deleted"
        }
        
        create_response = requests.post(f"{self.BASE_URL}/environment-variables/", 
                                      json=env_var_data, headers=self.headers)
        assert create_response.status_code == 200
        
        # Delete the variable
        response = requests.delete(f"{self.BASE_URL}/environment-variables/TEST_DELETE_VAR", 
                                 headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Environment variable 'TEST_DELETE_VAR' deleted successfully"
        assert data["name"] == "TEST_DELETE_VAR"
        assert data["username"] == "admin"
        
        # Verify it's deleted by trying to get it
        get_response = requests.get(f"{self.BASE_URL}/environment-variables/TEST_DELETE_VAR", 
                                   headers=self.headers)
        assert get_response.status_code == 404
        assert "not found" in get_response.json()["detail"]
    
    def test_get_nonexistent_environment_variable(self):
        """Test getting a non-existent environment variable"""
        response = requests.get(f"{self.BASE_URL}/environment-variables/NONEXISTENT_VAR", 
                              headers=self.headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "Environment variable 'NONEXISTENT_VAR' not found" in data["detail"]
    
    def test_delete_nonexistent_environment_variable(self):
        """Test deleting a non-existent environment variable"""
        response = requests.delete(f"{self.BASE_URL}/environment-variables/NONEXISTENT_VAR", 
                                 headers=self.headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "Environment variable 'NONEXISTENT_VAR' not found" in data["detail"]
    
    def test_unauthorized_access(self):
        """Test accessing environment variables without authorization"""
        # Test without Authorization header
        response = requests.get(f"{self.BASE_URL}/environment-variables/")
        
        assert response.status_code == 403  # or 401 depending on implementation
    
    def test_invalid_token(self):
        """Test accessing environment variables with invalid token"""
        invalid_headers = {
            "Authorization": "Bearer invalid_token_here",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{self.BASE_URL}/environment-variables/", headers=invalid_headers)
        
        assert response.status_code == 401
    
    def test_environment_variable_name_validation(self):
        """Test creating environment variables with various name formats"""
        test_cases = [
            {"name": "VALID_NAME", "value": "value1", "should_succeed": True},
            {"name": "valid_name_123", "value": "value2", "should_succeed": True},
            {"name": "MixedCase_Name", "value": "value3", "should_succeed": True},
        ]
        
        for case in test_cases:
            response = requests.post(f"{self.BASE_URL}/environment-variables/", 
                                   json={"name": case["name"], "value": case["value"]}, 
                                   headers=self.headers)
            
            if case["should_succeed"]:
                assert response.status_code == 200
                # Clean up
                requests.delete(f"{self.BASE_URL}/environment-variables/{case['name']}", 
                              headers=self.headers)
            else:
                assert response.status_code != 200
    
    def test_environment_variable_value_types(self):
        """Test creating environment variables with different value types"""
        test_cases = [
            {"name": "STRING_VAR", "value": "string_value"},
            {"name": "NUMBER_VAR", "value": "12345"},
            {"name": "JSON_VAR", "value": '{"key": "value"}'},
            {"name": "URL_VAR", "value": "https://example.com/api"},
            {"name": "EMPTY_VAR", "value": ""},
        ]
        
        for case in test_cases:
            response = requests.post(f"{self.BASE_URL}/environment-variables/", 
                                   json=case, headers=self.headers)
            
            assert response.status_code == 200
            
            # Verify by getting the variable
            get_response = requests.get(f"{self.BASE_URL}/environment-variables/{case['name']}", 
                                       headers=self.headers)
            assert get_response.status_code == 200
            assert get_response.json()["value"] == case["value"]
            
            # Clean up
            requests.delete(f"{self.BASE_URL}/environment-variables/{case['name']}", 
                          headers=self.headers)
