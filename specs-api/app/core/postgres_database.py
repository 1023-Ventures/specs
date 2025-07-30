import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class PostgreSQLDatabase:
    def __init__(self, connection_string: str = None):
        if connection_string is None:
            # Default connection for local development
            self.connection_string = (
                "host=localhost "
                "port=5432 "
                "dbname=specs_auth "
                "user=specs_user "
                "password=specs_password"
            )
        else:
            self.connection_string = connection_string
        
        # Initialize database with default admin user
        self.initialize_database()
    
    def get_connection(self):
        conn = psycopg2.connect(self.connection_string)
        conn.autocommit = False
        return conn
    
    def initialize_database(self):
        """Initialize the database with default admin user if it doesn't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create default admin user if it doesn't exist
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ('admin',))
            if cursor.fetchone()[0] == 0:
                admin_password = pwd_context.hash("admin123")
                cursor.execute("""
                    INSERT INTO users (username, email, hashed_password, role)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, ('admin', 'admin@example.com', admin_password, 'admin'))
                
                admin_id = cursor.fetchone()[0]
                
                # Grant all scopes to admin
                admin_scopes = ['read_profile', 'write_profile', 'read_users', 'admin']
                for scope in admin_scopes:
                    cursor.execute("""
                        INSERT INTO user_scopes (user_id, scope, granted_by)
                        VALUES (%s, %s, %s)
                    """, (admin_id, scope, 'system'))
            
            conn.commit()
            conn.close()
        except psycopg2.Error as e:
            # Silently handle initialization errors (e.g., tables don't exist yet)
            if conn:
                conn.rollback()
                conn.close()
            pass
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user with default scopes"""
        try:
            hashed_password = pwd_context.hash(password)
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password)
                VALUES (%s, %s, %s)
            """, (username, email, hashed_password))
            
            conn.commit()
            conn.close()
            return True
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def get_user(self, username: str) -> Optional[dict]:
        """Get user by username with their available scopes"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.hashed_password, u.is_active, u.role, u.created_at,
                   COALESCE(array_agg(us.scope) FILTER (WHERE us.scope IS NOT NULL), ARRAY[]::text[]) as available_scopes
            FROM users u
            LEFT JOIN user_scopes us ON u.id = us.user_id
            WHERE u.username = %s
            GROUP BY u.id, u.username, u.email, u.hashed_password, u.is_active, u.role, u.created_at
        """, (username,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user_dict = dict(row)
            user_dict["created_at"] = row["created_at"].strftime('%Y-%m-%d %H:%M:%S')
            return user_dict
        return None
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user with username and password"""
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            scopes: list = payload.get("scopes", [])
            if username is None:
                return None
            return {"username": username, "scopes": scopes}
        except JWTError:
            return None
    
    def get_available_scopes(self) -> dict:
        """Get all available scopes in the system"""
        return {
            "read_profile": "Read user profile information",
            "write_profile": "Modify user profile information", 
            "read_users": "Read other users' information",
            "write_users": "Modify other users' information",
            "admin": "Administrative access"
        }
    
    def validate_scopes(self, requested_scopes: list, user: dict) -> list:
        """Validate and filter scopes based on user's available scopes"""
        user_available_scopes = user.get("available_scopes", [])
        valid_scopes = []
        
        for scope in requested_scopes:
            if scope in user_available_scopes:
                valid_scopes.append(scope)
        
        return valid_scopes
    
    def get_user_available_scopes(self, user_id: int) -> list:
        """Get all scopes available to a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT scope FROM user_scopes WHERE user_id = %s
        """, (user_id,))
        
        scopes = [row[0] for row in cursor.fetchall()]
        conn.close()
        return scopes
    
    def grant_scope_to_user(self, user_id: int, scope: str, granted_by: str = "admin") -> bool:
        """Grant a scope to a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_scopes (user_id, scope, granted_by)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, scope) DO UPDATE SET
                granted_by = EXCLUDED.granted_by,
                granted_at = CURRENT_TIMESTAMP
            """, (user_id, scope, granted_by))
            
            conn.commit()
            conn.close()
            return True
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def revoke_scope_from_user(self, user_id: int, scope: str) -> bool:
        """Revoke a scope from a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM user_scopes WHERE user_id = %s AND scope = %s
            """, (user_id, scope))
            
            conn.commit()
            conn.close()
            return True
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def list_all_users_with_scopes(self) -> list:
        """List all users with their scopes (PostgreSQL version using STRING_AGG)"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.role, u.is_active,
                   STRING_AGG(us.scope, ',') as scopes
            FROM users u
            LEFT JOIN user_scopes us ON u.id = us.user_id
            GROUP BY u.id, u.username, u.email, u.role, u.is_active
            ORDER BY u.id
        """)
        
        users = cursor.fetchall()
        conn.close()
        
        # Convert to the expected format
        result = []
        for user in users:
            user_dict = dict(user)
            # Convert comma-separated scopes to list
            if user_dict['scopes']:
                user_dict['available_scopes'] = user_dict['scopes'].split(',')
            else:
                user_dict['available_scopes'] = []
            del user_dict['scopes']
            result.append(user_dict)
        
        return result
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT id, username, email, is_active, role, created_at
            FROM users WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    # Environment Variables methods
    def get_user_env_vars(self, user_id: int) -> list:
        """Get all environment variables for a user"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT name, value, created_at, updated_at 
            FROM user_environment_variables 
            WHERE user_id = %s
            ORDER BY name
        """, (user_id,))
        
        env_vars = []
        for row in cursor.fetchall():
            env_var = dict(row)
            env_var["created_at"] = row["created_at"].strftime('%Y-%m-%d %H:%M:%S')
            env_var["updated_at"] = row["updated_at"].strftime('%Y-%m-%d %H:%M:%S')
            env_vars.append(env_var)
        
        conn.close()
        return env_vars
    
    def get_user_env_var(self, user_id: int, name: str) -> Optional[dict]:
        """Get a specific environment variable for a user"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT name, value, created_at, updated_at 
            FROM user_environment_variables 
            WHERE user_id = %s AND name = %s
        """, (user_id, name))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            env_var = dict(row)
            env_var["created_at"] = row["created_at"].strftime('%Y-%m-%d %H:%M:%S')
            env_var["updated_at"] = row["updated_at"].strftime('%Y-%m-%d %H:%M:%S')
            return env_var
        return None
    
    def set_user_env_var(self, user_id: int, name: str, value: str) -> bool:
        """Set an environment variable for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_environment_variables (user_id, name, value)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, name) DO UPDATE SET
                value = EXCLUDED.value,
                updated_at = CURRENT_TIMESTAMP
            """, (user_id, name, value))
            
            conn.commit()
            conn.close()
            return True
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def delete_user_env_var(self, user_id: int, name: str) -> bool:
        """Delete an environment variable for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM user_environment_variables 
                WHERE user_id = %s AND name = %s
            """, (user_id, name))
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            return affected_rows > 0
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
                conn.close()
            return False

    def list_all_users_with_scopes(self) -> list:
        """List all users with their scopes (admin only)"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.role, u.is_active,
                   COALESCE(array_agg(us.scope) FILTER (WHERE us.scope IS NOT NULL), ARRAY[]::text[]) as available_scopes
            FROM users u
            LEFT JOIN user_scopes us ON u.id = us.user_id
            GROUP BY u.id, u.username, u.email, u.role, u.is_active
            ORDER BY u.id
        """)
        
        users = []
        for row in cursor.fetchall():
            user = dict(row)
            users.append(user)
        
        conn.close()
        return users

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.hashed_password, u.is_active, u.role, u.created_at,
                   COALESCE(array_agg(us.scope) FILTER (WHERE us.scope IS NOT NULL), ARRAY[]::text[]) as available_scopes
            FROM users u
            LEFT JOIN user_scopes us ON u.id = us.user_id
            WHERE u.id = %s
            GROUP BY u.id, u.username, u.email, u.hashed_password, u.is_active, u.role, u.created_at
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user_dict = dict(row)
            user_dict["created_at"] = row["created_at"].strftime('%Y-%m-%d %H:%M:%S')
            return user_dict
        return None
