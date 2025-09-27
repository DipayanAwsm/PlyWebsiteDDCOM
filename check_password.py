#!/usr/bin/env python3
"""
Check password hash and verify if a password matches
"""

import sqlite3
import bcrypt

def check_password():
    """Check the stored password hash and verify a password"""
    conn = sqlite3.connect('instance/dd_sons.db')
    cursor = conn.cursor()
    
    # Get the admin user's password hash
    cursor.execute("SELECT username, password_hash FROM user WHERE username = 'admin';")
    user = cursor.fetchone()
    
    if user:
        username, password_hash = user
        print(f"👤 User: {username}")
        print(f"🔐 Stored Hash: {password_hash}")
        print(f"📏 Hash Length: {len(password_hash)} characters")
        
        # Test if "admin123" matches the hash
        test_password = "admin123"
        is_valid = bcrypt.checkpw(test_password.encode('utf-8'), password_hash.encode('utf-8'))
        
        print(f"\n🧪 Testing password: '{test_password}'")
        print(f"✅ Password matches: {is_valid}")
        
        if is_valid:
            print("🎉 SUCCESS: The password 'admin123' is correct!")
        else:
            print("❌ FAILED: The password 'admin123' does not match the hash")
            
        # Show what the hash looks like
        print(f"\n📋 Hash Details:")
        print(f"• Starts with: {password_hash[:10]}...")
        print(f"• Ends with: ...{password_hash[-10:]}")
        print(f"• Contains salt: {'Yes' if '$' in password_hash else 'No'}")
        
    else:
        print("❌ No admin user found in database")
    
    conn.close()

def show_all_users():
    """Show all users and their password hashes"""
    conn = sqlite3.connect('instance/dd_sons.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email, password_hash, role FROM user;")
    users = cursor.fetchall()
    
    print("\n👥 All Users in Database:")
    print("=" * 100)
    print(f"{'ID':<5} | {'Username':<15} | {'Email':<25} | {'Role':<10} | {'Hash Preview'}")
    print("-" * 100)
    
    for user in users:
        user_id, username, email, password_hash, role = user
        hash_preview = password_hash[:20] + "..." if len(password_hash) > 20 else password_hash
        print(f"{user_id:<5} | {username:<15} | {email:<25} | {role:<10} | {hash_preview}")
    
    conn.close()

if __name__ == "__main__":
    print("🔍 Password Hash Checker")
    print("=" * 50)
    check_password()
    show_all_users()
    
    print(f"\n💡 Important Notes:")
    print("-" * 50)
    print("• Passwords are hashed with bcrypt for security")
    print("• You cannot 'unhash' or decrypt the password")
    print("• The original password is never stored")
    print("• Default admin password is: admin123")
    print("• To change password, use the web interface or create a new user")

