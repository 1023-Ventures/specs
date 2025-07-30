-- Initialize PostgreSQL database with tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_scopes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    scope VARCHAR(255) NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by VARCHAR(255) DEFAULT 'system',
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE(user_id, scope)
);

CREATE TABLE IF NOT EXISTS user_environment_variables (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE(user_id, name)
);

-- Create default admin user
INSERT INTO users (username, email, hashed_password, role) 
VALUES ('admin', 'admin@example.com', '$2b$12$SvIkmEk6W1UogNNP5ir3kudZBt4objGguyj9V2q0QA0ZQwyrdOKCe', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Grant admin scopes
INSERT INTO user_scopes (user_id, scope, granted_by) 
SELECT u.id, scope, 'system'
FROM users u, (VALUES ('admin'), ('read_profile'), ('read_users'), ('write_profile')) AS scopes(scope)
WHERE u.username = 'admin'
ON CONFLICT (user_id, scope) DO NOTHING;
