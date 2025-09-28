#!/usr/bin/env python3
"""
Fix database schema issues
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotspot_config.settings')
django.setup()

from django.db import connection

def fix_database_schema():
    """Fix all database schema issues"""
    try:
        with connection.cursor() as cursor:
            print("🔧 Fixing database schema...")
            
            # 1. Ensure user_type column exists
            cursor.execute("""
                SELECT COUNT(*) FROM pragma_table_info('accounts_user') 
                WHERE name = 'user_type'
            """)
            if cursor.fetchone()[0] == 0:
                print("Adding user_type column...")
                cursor.execute("""
                    ALTER TABLE accounts_user 
                    ADD COLUMN user_type VARCHAR(20) DEFAULT 'end_user'
                """)
                print("✅ user_type column added")
            else:
                print("✅ user_type column already exists")
            
            # 2. Check if tickets table exists and has required columns
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='tickets_ticket'
            """)
            if not cursor.fetchone():
                print("Creating tickets_ticket table...")
                cursor.execute("""
                    CREATE TABLE tickets_ticket (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        provider_id INTEGER NOT NULL,
                        code VARCHAR(20) UNIQUE NOT NULL,
                        username VARCHAR(50) NOT NULL,
                        password VARCHAR(50) NOT NULL,
                        plan_type VARCHAR(10) DEFAULT 'time',
                        duration_hours INTEGER,
                        data_limit_mb INTEGER,
                        price DECIMAL(10,2) NOT NULL,
                        currency VARCHAR(3) DEFAULT 'KES',
                        status VARCHAR(20) DEFAULT 'active',
                        expires_at DATETIME,
                        used_at DATETIME,
                        device_mac VARCHAR(17),
                        device_ip VARCHAR(45),
                        session_start DATETIME,
                        session_end DATETIME,
                        data_used_mb INTEGER DEFAULT 0,
                        payment_id INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (provider_id) REFERENCES accounts_provider(id),
                        FOREIGN KEY (payment_id) REFERENCES payments_payment(id)
                    )
                """)
                print("✅ tickets_ticket table created")
            else:
                print("✅ tickets_ticket table already exists")
            
            # 3. Check if ticket_types table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='tickets_tickettype'
            """)
            if not cursor.fetchone():
                print("Creating tickets_tickettype table...")
                cursor.execute("""
                    CREATE TABLE tickets_tickettype (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        provider_id INTEGER NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        type VARCHAR(10) DEFAULT 'time',
                        duration_hours INTEGER,
                        data_limit_mb INTEGER,
                        price DECIMAL(10,2) NOT NULL,
                        currency VARCHAR(3) DEFAULT 'KES',
                        download_speed_mbps INTEGER DEFAULT 5,
                        upload_speed_mbps INTEGER DEFAULT 2,
                        is_active BOOLEAN DEFAULT 1,
                        is_featured BOOLEAN DEFAULT 0,
                        description TEXT,
                        icon VARCHAR(50) DEFAULT 'fas fa-wifi',
                        color VARCHAR(7) DEFAULT '#3B82F6',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (provider_id) REFERENCES accounts_provider(id)
                    )
                """)
                print("✅ tickets_tickettype table created")
            else:
                print("✅ tickets_tickettype table already exists")
            
            # 4. Check if payments table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='payments_payment'
            """)
            if not cursor.fetchone():
                print("Creating payments_payment table...")
                cursor.execute("""
                    CREATE TABLE payments_payment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        provider_id INTEGER,
                        type VARCHAR(50) NOT NULL,
                        provider_payload TEXT,
                        amount DECIMAL(10,2) NOT NULL,
                        currency VARCHAR(3) DEFAULT 'KES',
                        external_txn_id VARCHAR(100),
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (provider_id) REFERENCES accounts_provider(id)
                    )
                """)
                print("✅ payments_payment table created")
            else:
                print("✅ payments_payment table already exists")
            
            print("🎉 Database schema fixed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing database schema: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing database schema...")
    if fix_database_schema():
        print("🎉 Database schema fixed successfully!")
    else:
        print("❌ Failed to fix database schema!")
