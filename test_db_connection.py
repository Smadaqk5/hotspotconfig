#!/usr/bin/env python3
"""
Test script to verify database connection
"""
import os
import sys
import psycopg2
from urllib.parse import urlparse

def test_database_connection():
    """Test database connection with the provided DATABASE_URL"""
    
    # Get DATABASE_URL from environment or prompt user
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL environment variable or provide it manually")
        
        # Prompt user for DATABASE_URL
        database_url = input("\nEnter your DATABASE_URL: ").strip()
        
        if not database_url:
            print("❌ No DATABASE_URL provided. Exiting.")
            return False
    
    print(f"🔍 Testing connection to: {database_url[:50]}...")
    
    try:
        # Parse the URL to extract components
        parsed = urlparse(database_url)
        print(f"📊 Host: {parsed.hostname}")
        print(f"📊 Port: {parsed.port}")
        print(f"📊 Database: {parsed.path[1:]}")
        print(f"📊 User: {parsed.username}")
        
        # Test connection
        print("\n🔄 Attempting to connect...")
        conn = psycopg2.connect(database_url)
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print("✅ Connection successful!")
        print(f"📊 PostgreSQL version: {version}")
        
        # Test if we can create a simple table (optional)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("INSERT INTO test_connection DEFAULT VALUES;")
        cursor.execute("SELECT COUNT(*) FROM test_connection;")
        count = cursor.fetchone()[0]
        
        print(f"✅ Test table created and data inserted (count: {count})")
        
        # Clean up
        cursor.execute("DROP TABLE IF EXISTS test_connection;")
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database connection test completed successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if your DATABASE_URL is correct")
        print("2. Verify the password in Supabase dashboard")
        print("3. Make sure your Supabase project is active")
        print("4. Check if your IP is whitelisted (if applicable)")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_django_connection():
    """Test Django database connection"""
    print("\n🔄 Testing Django database connection...")
    
    try:
        # Set up Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
        
        import django
        django.setup()
        
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        # Test Django database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        print("✅ Django database connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Django database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Database Connection Test")
    print("=" * 50)
    
    # Test 1: Direct psycopg2 connection
    print("\n1️⃣ Testing direct psycopg2 connection...")
    success1 = test_database_connection()
    
    # Test 2: Django connection (if available)
    print("\n2️⃣ Testing Django database connection...")
    success2 = test_django_connection()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! Your database connection is working.")
    elif success1:
        print("⚠️  Direct connection works, but Django connection failed.")
        print("   This might be due to Django settings or missing dependencies.")
    else:
        print("❌ Database connection failed. Please check your DATABASE_URL.")
    
    print("\n💡 Next steps:")
    print("1. If tests pass, your DATABASE_URL is correct")
    print("2. Update your Heroku config vars with the working DATABASE_URL")
    print("3. Redeploy your Heroku app")
