#!/usr/bin/env python3
"""
Create a test user with a known password
"""

import sqlite3
import bcrypt
from datetime import datetime

def create_test_user():
    """Create a test user with password 'test123'"""
    conn = sqlite3.connect('instance/dd_sons.db')
    cursor = conn.cursor()
    
    # Test password
    test_password = "test123"
    password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Check if test user already exists
    cursor.execute("SELECT id FROM user WHERE username = 'testuser';")
    existing_user = cursor.fetchone()
    
    if existing_user:
        print("⚠️  Test user already exists. Updating password...")
        cursor.execute("""
            UPDATE user 
            SET password_hash = ?, updated_at = ?
            WHERE username = 'testuser'
        """, (password_hash, datetime.utcnow()))
    else:
        print("➕ Creating new test user...")
        cursor.execute("""
            INSERT INTO user (username, email, password_hash, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('testuser', 'test@ddandsons.com', password_hash, 'admin', datetime.utcnow(), datetime.utcnow()))
    
    conn.commit()
    conn.close()
    
    print("✅ Test user created/updated successfully!")
    print(f"👤 Username: testuser")
    print(f"🔑 Password: {test_password}")
    print(f"📧 Email: test@ddandsons.com")
    print(f"👑 Role: admin")
    print(f"🔐 Password Hash: {password_hash}")

if __name__ == "__main__":
    create_test_user()

