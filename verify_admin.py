#!/usr/bin/env python3
"""
Verify admin user credentials
"""

import sqlite3
import bcrypt

def verify_admin():
    """Verify admin user exists and show credentials"""
    conn = sqlite3.connect('instance/dd_sons.db')
    cursor = conn.cursor()
    
    # Get admin user
    cursor.execute("SELECT id, username, email, password_hash, role, created_at FROM user WHERE username = 'admin';")
    admin_user = cursor.fetchone()
    
    if admin_user:
        user_id, username, email, password_hash, role, created_at = admin_user
        print("✅ Admin User Found!")
        print("=" * 50)
        print(f"ID: {user_id}")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Role: {role}")
        print(f"Created: {created_at}")
        print(f"Password Hash: {password_hash[:20]}...")
        
        # Test password
        test_password = "admin123"
        is_valid = bcrypt.checkpw(test_password.encode('utf-8'), password_hash.encode('utf-8'))
        print(f"\n🔐 Password Test:")
        print(f"Testing: '{test_password}'")
        print(f"Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        if is_valid:
            print(f"\n🎯 Login Instructions:")
            print(f"1. Go to: http://192.168.0.102:8080/login")
            print(f"2. Username: {username}")
            print(f"3. Password: {test_password}")
        else:
            print(f"\n❌ Password mismatch! The stored password is not 'admin123'")
            
    else:
        print("❌ No admin user found!")
        print("Creating admin user...")
        
        # Create admin user
        password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("""
            INSERT INTO user (username, email, password_hash, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        """, ('admin', 'admin@ddandsons.com', password_hash, 'admin'))
        
        conn.commit()
        print("✅ Admin user created!")
        print(f"Username: admin")
        print(f"Password: admin123")
    
    conn.close()

if __name__ == "__main__":
    verify_admin()

