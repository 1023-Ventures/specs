import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Database:
    def __init__(self, db_path: str = "auth.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize the database with users and user_scopes tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_scopes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                scope TEXT NOT NULL,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                granted_by TEXT DEFAULT 'system',
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, scope)
            )
        """)
        
        # Create default admin user if it doesn't exist
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            admin_password = self.hash_password("admin123")
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password, role)
                VALUES ('admin', 'admin@example.com', ?, 'admin')
            """, (admin_password,))
            
            admin_id = cursor.lastrowid
            # Grant all scopes to admin
            admin_scopes = ['read_profile', 'write_profile', 'read_users', 'admin']
            for scope in admin_scopes:
                cursor.execute("""
                    INSERT INTO user_scopes (user_id, scope, granted_by)
                    VALUES (?, ?, 'system')
                """, (admin_id, scope))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user with default scopes"""
        try:
            hashed_password = pwd_context.hash(password)
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password)
                VALUES (?, ?, ?)
            """, (username, email, hashed_password))
            
            user_id = cursor.lastrowid
            
            # Grant default scopes to new users
            default_scopes = ['read_profile', 'write_profile']
            for scope in default_scopes:
                cursor.execute("""
                    INSERT INTO user_scopes (user_id, scope, granted_by)
                    VALUES (?, ?, 'system')
                """, (user_id, scope))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, username: str) -> Optional[dict]:
        """Get user by username with their available scopes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("""
            SELECT id, username, email, hashed_password, is_active, role, created_at
            FROM users WHERE username = ?
        """, (username,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        user = {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "hashed_password": row[3],
            "is_active": bool(row[4]),
            "role": row[5],
            "created_at": row[6]
        }
        
        # Get user's available scopes
        cursor.execute("""
            SELECT scope FROM user_scopes WHERE user_id = ?
        """, (user["id"],))
        
        scopes = [row[0] for row in cursor.fetchall()]
        user["available_scopes"] = scopes
        
        conn.close()
        return user
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user"""
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token with scopes"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return user data with scopes"""
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
            SELECT scope FROM user_scopes WHERE user_id = ?
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
                INSERT OR IGNORE INTO user_scopes (user_id, scope, granted_by)
                VALUES (?, ?, ?)
            """, (user_id, scope, granted_by))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False
    
    def revoke_scope_from_user(self, user_id: int, scope: str) -> bool:
        """Revoke a scope from a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM user_scopes WHERE user_id = ? AND scope = ?
            """, (user_id, scope))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False
