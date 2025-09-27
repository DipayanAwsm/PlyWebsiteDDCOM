#!/usr/bin/env python3
"""
Database Migration Script
Adds new fields for PDF catalog support
"""

import sqlite3
import os

def migrate_database():
    """Add new columns to existing database"""
    db_path = 'instance/dd_sons.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the application first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Checking database schema...")
        
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(product);")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current Product table columns: {columns}")
        
        # Add new columns if they don't exist
        new_columns = [
            ('pdf_catalog', 'VARCHAR(200)'),
            ('pdf_pages', 'INTEGER DEFAULT 0'),
            ('view_count', 'INTEGER DEFAULT 0')
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                print(f"➕ Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE product ADD COLUMN {column_name} {column_type};")
            else:
                print(f"✅ Column already exists: {column_name}")
        
        # Check if ProductView table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_view';")
        if not cursor.fetchone():
            print("➕ Creating ProductView table...")
            cursor.execute("""
                CREATE TABLE product_view (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    ip_address VARCHAR(45) NOT NULL,
                    user_agent TEXT,
                    page_number INTEGER DEFAULT 1,
                    view_type VARCHAR(20) DEFAULT 'product',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES product (id)
                );
            """)
        else:
            print("✅ ProductView table already exists")
        
        conn.commit()
        conn.close()
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🗄️  DD and Sons - Database Migration")
    print("=" * 50)
    migrate_database()

