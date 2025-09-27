#!/usr/bin/env python3
"""
Show user accounts and passwords from the database
"""

import sqlite3

def show_users():
    """Show user accounts with passwords"""
    conn = sqlite3.connect('instance/dd_sons.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email, password, role, created_at FROM user;")
    users = cursor.fetchall()
    
    print("👥 User Accounts with Passwords:")
    print("=" * 100)
    print(f"{'ID':<5} | {'Username':<15} | {'Email':<25} | {'Password (Hashed)':<50} | {'Role':<10} | {'Created'}")
    print("-" * 100)
    
    for user in users:
        # Truncate password hash for display
        password_display = user[3][:47] + "..." if len(user[3]) > 50 else user[3]
        print(f"{user[0]:<5} | {user[1]:<15} | {user[2]:<25} | {password_display:<50} | {user[4]:<10} | {user[5]}")
    
    conn.close()
    
    print("\n🔑 Password Information:")
    print("-" * 50)
    print("• Passwords are hashed using bcrypt for security")
    print("• Default admin password: 'admin123'")
    print("• To verify a password, use bcrypt.checkpw(password, hash)")

if __name__ == "__main__":
    show_users()

