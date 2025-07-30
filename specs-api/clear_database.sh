#!/bin/bash
# Simple script to clear PostgreSQL database tables

echo "🗃️  PostgreSQL Database Clear Script"
echo "=================================="

# Check if PostgreSQL container is running
if ! docker ps | grep -q specs_postgres; then
    echo "❌ PostgreSQL container 'specs_postgres' is not running"
    echo "Please start it with: docker-compose up -d postgres"
    exit 1
fi

echo "📊 Current table statistics:"
docker exec -it specs_postgres psql -U specs_user -d specs_auth -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows
FROM pg_stat_user_tables 
ORDER BY tablename;
"

echo ""
echo "📋 Tables to be cleared:"
docker exec -it specs_postgres psql -U specs_user -d specs_auth -c "
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
"

echo ""
read -p "⚠️  Are you sure you want to clear ALL data from these tables? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy]es?$ ]]; then
    echo "❌ Operation cancelled"
    exit 0
fi

echo ""
echo "🧹 Clearing all tables..."

# Clear all tables
docker exec -it specs_postgres psql -U specs_user -d specs_auth -c "
-- Disable foreign key checks
SET session_replication_role = replica;

-- Clear all tables
TRUNCATE TABLE user_environment_variables RESTART IDENTITY CASCADE;
TRUNCATE TABLE user_scopes RESTART IDENTITY CASCADE;
TRUNCATE TABLE users RESTART IDENTITY CASCADE;

-- Re-enable foreign key checks
SET session_replication_role = DEFAULT;

SELECT 'All tables cleared successfully!' as result;
"

echo ""
echo "🎉 Database tables cleared successfully!"
echo ""
echo "💡 To reinitialize with default data, restart your application or run:"
echo "   python clear_database.py reset"
