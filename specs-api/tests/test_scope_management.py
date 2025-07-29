#!/usr/bin/env python3
"""
Pytest-based tests for the ECS Auth API scope management functionality
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from main import app

# Test client for FastAPI
client = TestClient(app)

class TestScopeManagement:
    """Test class for scope management endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data before each test"""
        # Register a test user
        self.test_user_data = {
            "username": "test_scope_user",
            "email": "test_scope@example.com",
            "password": "testpassword123"
        }
        
        # Register the user (ignore if already exists)
        client.post("/api/v1/register", json=self.test_user_data)
        
        # Login as admin to get admin token
        admin_login = {
            "username": "admin",
            "password": "admin123",
            "scopes": ["admin", "read_users", "write_users"]
        }
        
        admin_response = client.post("/api/v1/login", json=admin_login)
        if admin_response.status_code == 200:
            self.admin_token = admin_response.json()["access_token"]
            self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        else:
            self.admin_token = None
            self.admin_headers = {}
        
        # Login as regular user
        user_login = {
            "username": self.test_user_data["username"],
            "password": self.test_user_data["password"],
            "scopes": ["read_profile"]
        }
        
        user_response = client.post("/api/v1/login", json=user_login)
        if user_response.status_code == 200:
            self.user_token = user_response.json()["access_token"]
            self.user_headers = {"Authorization": f"Bearer {self.user_token}"}
        else:
            self.user_token = None
            self.user_headers = {}
    
    def test_get_current_user_scopes(self):
        """Test getting current user's scopes"""
        if not self.user_token:
            pytest.skip("User token not available")
        
        response = client.get("/api/v1/me/scopes", headers=self.user_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "username" in data
        assert "available_scopes" in data
        assert isinstance(data["available_scopes"], list)
    
    def test_list_all_users_with_scopes_admin_only(self):
        """Test that only admins can list all users with scopes"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        # Test with admin token
        response = client.get("/api/v1/users/scopes", headers=self.admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "users" in data
        assert isinstance(data["users"], list)
        
        # Test with regular user token (should fail)
        if self.user_token:
            response = client.get("/api/v1/users/scopes", headers=self.user_headers)
            assert response.status_code == 403
    
    def test_get_user_scopes_by_id_admin_only(self):
        """Test getting specific user's scopes (admin only)"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        # First get list of users to find a user ID
        users_response = client.get("/api/v1/users/scopes", headers=self.admin_headers)
        assert users_response.status_code == 200
        
        users = users_response.json()["users"]
        if not users:
            pytest.skip("No users found")
        
        user_id = users[0]["id"]
        
        # Test with admin token
        response = client.get(f"/api/v1/users/{user_id}/scopes", headers=self.admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        assert "username" in data
        assert "available_scopes" in data
        
        # Test with regular user token (should fail)
        if self.user_token:
            response = client.get(f"/api/v1/users/{user_id}/scopes", headers=self.user_headers)
            assert response.status_code == 403
    
    def test_grant_scope_to_user_admin_only(self):
        """Test granting scopes to users (admin only)"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        # Get a user ID
        users_response = client.get("/api/v1/users/scopes", headers=self.admin_headers)
        assert users_response.status_code == 200
        
        users = users_response.json()["users"]
        test_user = None
        for user in users:
            if user["username"] == self.test_user_data["username"]:
                test_user = user
                break
        
        if not test_user:
            pytest.skip("Test user not found")
        
        user_id = test_user["id"]
        
        # Test granting a scope with admin token
        response = client.post(f"/api/v1/users/{user_id}/scopes/write_profile", headers=self.admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "write_profile" in data["message"]
        
        # Verify the scope was granted
        verify_response = client.get(f"/api/v1/users/{user_id}/scopes", headers=self.admin_headers)
        assert verify_response.status_code == 200
        user_scopes = verify_response.json()["available_scopes"]
        assert "write_profile" in user_scopes
        
        # Test with regular user token (should fail)
        if self.user_token:
            response = client.post(f"/api/v1/users/{user_id}/scopes/admin", headers=self.user_headers)
            assert response.status_code == 403
    
    def test_revoke_scope_from_user_admin_only(self):
        """Test revoking scopes from users (admin only)"""
        if not self.admin_token:
            pytest.skip("Admin token not available")
        
        # Get a user ID and ensure they have a scope to revoke
        users_response = client.get("/api/v1/users/scopes", headers=self.admin_headers)
        assert users_response.status_code == 200
        
        users = users_response.json()["users"]
        test_user = None
        for user in users:
            if user["username"] == self.test_user_data["username"]:
                test_user = user
                break
        
        if not test_user:
            pytest.skip("Test user not found")
        
        user_id = test_user["id"]
        
        # First grant a scope to revoke
        client.post(f"/api/v1/users/{user_id}/scopes/write_profile", headers=self.admin_headers)
        
        # Test revoking the scope with admin token
        response = client.delete(f"/api/v1/users/{user_id}/scopes/write_profile", headers=self.admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "write_profile" in data["message"]
        
        # Verify the scope was revoked
        verify_response = client.get(f"/api/v1/users/{user_id}/scopes", headers=self.admin_headers)
        assert verify_response.status_code == 200
        user_scopes = verify_response.json()["available_scopes"]
        assert "write_profile" not in user_scopes
        
        # Test with regular user token (should fail)
        if self.user_token:
            response = client.delete(f"/api/v1/users/{user_id}/scopes/read_profile", headers=self.user_headers)
            assert response.status_code == 403
    
    def test_scope_validation_in_login(self):
        """Test that users can only request scopes they have access to"""
        # Test login with valid scopes
        login_data = {
            "username": self.test_user_data["username"],
            "password": self.test_user_data["password"],
            "scopes": ["read_profile"]  # Default scope
        }
        
        response = client.post("/api/v1/login", json=login_data)
        assert response.status_code == 200
        
        # Test login with invalid scopes (should fail or filter out invalid scopes)
        login_data_invalid = {
            "username": self.test_user_data["username"],
            "password": self.test_user_data["password"],
            "scopes": ["admin", "super_secret_scope"]  # User shouldn't have these
        }
        
        response = client.post("/api/v1/login", json=login_data_invalid)
        # Should either fail or return only valid scopes
        assert response.status_code in [200, 400, 403]
        
        if response.status_code == 200:
            # If successful, check that invalid scopes were filtered out
            token_data = response.json()
            assert "scopes" in token_data
            # Admin scope should not be in the granted scopes
            assert "admin" not in token_data.get("scopes", [])
    
    def test_protected_endpoints_with_scopes(self):
        """Test that endpoints properly validate required scopes"""
        if not self.user_token:
            pytest.skip("User token not available")
        
        # Test endpoint that requires a scope the user doesn't have
        response = client.get("/api/v1/users", headers=self.user_headers)
        # Should fail because user doesn't have read_users scope
        assert response.status_code == 403
        
        # Grant the required scope and test again
        if self.admin_token:
            # Find user ID
            users_response = client.get("/api/v1/users/scopes", headers=self.admin_headers)
            if users_response.status_code == 200:
                users = users_response.json()["users"]
                test_user = None
                for user in users:
                    if user["username"] == self.test_user_data["username"]:
                        test_user = user
                        break
                
                if test_user:
                    user_id = test_user["id"]
                    # Grant read_users scope
                    client.post(f"/api/v1/users/{user_id}/scopes/read_users", headers=self.admin_headers)
                    
                    # Login again with the new scope
                    login_data = {
                        "username": self.test_user_data["username"],
                        "password": self.test_user_data["password"],
                        "scopes": ["read_users"]
                    }
                    
                    login_response = client.post("/api/v1/login", json=login_data)
                    if login_response.status_code == 200:
                        new_token = login_response.json()["access_token"]
                        new_headers = {"Authorization": f"Bearer {new_token}"}
                        
                        # Now the endpoint should work
                        response = client.get("/api/v1/users", headers=new_headers)
                        assert response.status_code == 200

class TestScopeIntegration:
    """Integration tests for the complete scope system"""
    
    def test_complete_user_lifecycle_with_scopes(self):
        """Test complete user lifecycle with scope management"""
        # 1. Register a new user
        user_data = {
            "username": "lifecycle_user",
            "email": "lifecycle@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code in [200, 400]  # 400 if user already exists
        
        # 2. Login as admin
        admin_login = {
            "username": "admin",
            "password": "admin123",
            "scopes": ["admin"]
        }
        
        admin_response = client.post("/api/v1/login", json=admin_login)
        if admin_response.status_code != 200:
            pytest.skip("Admin login failed")
        
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 3. Get user ID
        users_response = client.get("/api/v1/users/scopes", headers=admin_headers)
        assert users_response.status_code == 200
        
        users = users_response.json()["users"]
        test_user = None
        for user in users:
            if user["username"] == "lifecycle_user":
                test_user = user
                break
        
        if not test_user:
            pytest.skip("Test user not found")
        
        user_id = test_user["id"]
        
        # 4. Grant additional scopes
        scopes_to_grant = ["read_users", "write_profile"]
        for scope in scopes_to_grant:
            response = client.post(f"/api/v1/users/{user_id}/scopes/{scope}", headers=admin_headers)
            assert response.status_code == 200
        
        # 5. Verify scopes were granted
        user_scopes_response = client.get(f"/api/v1/users/{user_id}/scopes", headers=admin_headers)
        assert user_scopes_response.status_code == 200
        
        available_scopes = user_scopes_response.json()["available_scopes"]
        for scope in scopes_to_grant:
            assert scope in available_scopes
        
        # 6. Login as user with granted scopes
        user_login = {
            "username": "lifecycle_user",
            "password": "password123",
            "scopes": scopes_to_grant
        }
        
        user_response = client.post("/api/v1/login", json=user_login)
        assert user_response.status_code == 200
        
        user_token = user_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # 7. Test that user can access scope-protected endpoints
        response = client.get("/api/v1/users", headers=user_headers)
        assert response.status_code == 200  # Should work with read_users scope
        
        # 8. Revoke a scope
        response = client.delete(f"/api/v1/users/{user_id}/scopes/read_users", headers=admin_headers)
        assert response.status_code == 200
        
        # 9. Verify scope was revoked
        user_scopes_response = client.get(f"/api/v1/users/{user_id}/scopes", headers=admin_headers)
        updated_scopes = user_scopes_response.json()["available_scopes"]
        assert "read_users" not in updated_scopes
        assert "write_profile" in updated_scopes  # Should still have this one

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
