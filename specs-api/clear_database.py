#!/usr/bin/env python3
"""
Script to clear all tables in the PostgreSQL database
This is useful for resetting the database during development and testing.
"""
import os
import sys
from app.core.database_factory import get_database
from app.core.postgres_database import PostgreSQLDatabase

def clear_postgres_tables():
    """Clear all tables in the PostgreSQL database"""
    try:
        # Get PostgreSQL database instance
        db = get_database()
        
        if not isinstance(db, PostgreSQLDatabase):
            print("❌ This script only works with PostgreSQL database")
            print(f"Current database type: {type(db).__name__}")
            return False
        
        print("🗃️  Connecting to PostgreSQL database...")
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        tables = cursor.fetchall()
        
        if not tables:
            print("ℹ️  No tables found in the database")
            conn.close()
            return True
        
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Confirm before proceeding
        response = input("\n⚠️  Are you sure you want to clear ALL data from these tables? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Operation cancelled")
            conn.close()
            return False
        
        print("\n🧹 Clearing tables...")
        
        # Disable foreign key checks temporarily
        cursor.execute("SET session_replication_role = replica;")
        
        # Clear each table
        cleared_count = 0
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
                print(f"   ✅ Cleared table: {table_name}")
                cleared_count += 1
            except Exception as e:
                print(f"   ❌ Failed to clear table {table_name}: {e}")
        
        # Re-enable foreign key checks
        cursor.execute("SET session_replication_role = DEFAULT;")
        
        # Commit the changes
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Successfully cleared {cleared_count}/{len(tables)} tables")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        import traceback
        traceback.print_exc()
        return False

def clear_and_reinitialize():
    """Clear tables and reinitialize with default data"""
    print("🔄 Clearing database and reinitializing...")
    
    if not clear_postgres_tables():
        return False
    
    try:
        # Get database instance and reinitialize
        db = get_database()
        
        print("🏗️  Reinitializing database with default data...")
        
        # The database initialization should happen automatically
        # when we create a new database instance, but let's make sure
        # by creating a test connection
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check if admin user exists, if not the init should have run
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin';")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("❌ Database initialization may have failed - no admin user found")
            conn.close()
            return False
        
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_scopes;")
        scope_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Database reinitialized successfully")
        print(f"   - Users: {user_count}")
        print(f"   - Scopes: {scope_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reinitializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_table_stats():
    """Show statistics about current table contents"""
    try:
        db = get_database()
        
        if not isinstance(db, PostgreSQLDatabase):
            print("❌ This script only works with PostgreSQL database")
            return False
        
        print("📊 Current database statistics:")
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get table statistics
        tables_info = [
            ('users', 'Users'),
            ('user_scopes', 'User Scopes'),
            ('user_environment_variables', 'Environment Variables')
        ]
        
        for table_name, display_name in tables_info:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"   - {display_name}: {count} records")
            except Exception as e:
                print(f"   - {display_name}: Error ({e})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error getting table statistics: {e}")
        return False

def main():
    """Main function with command line options"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clear":
            clear_postgres_tables()
        elif command == "reset":
            clear_and_reinitialize()
        elif command == "stats":
            show_table_stats()
        elif command == "help":
            print_help()
        else:
            print(f"❌ Unknown command: {command}")
            print_help()
    else:
        print_help()

def print_help():
    """Print help information"""
    print("🗃️  PostgreSQL Database Management Script")
    print("\nUsage:")
    print("  python clear_database.py <command>")
    print("\nCommands:")
    print("  clear  - Clear all data from tables (keeps structure)")
    print("  reset  - Clear all data and reinitialize with defaults")
    print("  stats  - Show current table statistics")
    print("  help   - Show this help message")
    print("\nExamples:")
    print("  python clear_database.py stats")
    print("  python clear_database.py clear")
    print("  python clear_database.py reset")
    print("\n⚠️  Warning: 'clear' and 'reset' commands will permanently delete all data!")

if __name__ == "__main__":
    main()
