#!/usr/bin/env python3
"""
Show all columns and data in the users table
"""

import sqlite3

def show_user_columns():
    """Show all columns and data in the users table"""
    conn = sqlite3.connect('instance/dd_sons.db')
    cursor = conn.cursor()
    
    # Get table structure
    cursor.execute("PRAGMA table_info(user);")
    columns = cursor.fetchall()
    
    print("📋 User Table Structure:")
    print("=" * 80)
    print(f"{'Column ID':<10} | {'Column Name':<20} | {'Data Type':<15} | {'Not Null':<10} | {'Default Value'}")
    print("-" * 80)
    
    for col in columns:
        col_id, col_name, data_type, not_null, default_val, pk = col
        not_null_str = "Yes" if not_null else "No"
        default_str = str(default_val) if default_val is not None else "None"
        print(f"{col_id:<10} | {col_name:<20} | {data_type:<15} | {not_null_str:<10} | {default_str}")
    
    print("\n" + "=" * 80)
    
    # Get all user data
    cursor.execute("SELECT * FROM user;")
    users = cursor.fetchall()
    
    # Get column names for display
    column_names = [col[1] for col in columns]
    
    print(f"\n👥 All User Data ({len(users)} users):")
    print("=" * 120)
    
    if users:
        # Print column headers
        header = " | ".join(f"{name:15}" for name in column_names)
        print(header)
        print("-" * 120)
        
        # Print data rows
        for user in users:
            formatted_row = []
            for i, item in enumerate(user):
                if item is None:
                    formatted_row.append("NULL")
                elif column_names[i] == 'password_hash' and len(str(item)) > 15:
                    formatted_row.append(str(item)[:12] + "...")
                elif isinstance(item, str) and len(item) > 15:
                    formatted_row.append(item[:12] + "...")
                else:
                    formatted_row.append(str(item))
            
            row = " | ".join(f"{item:15}" for item in formatted_row)
            print(row)
    else:
        print("No users found in the database.")
    
    conn.close()
    
    print(f"\n🔑 Column Details:")
    print("-" * 50)
    for col in columns:
        col_id, col_name, data_type, not_null, default_val, pk = col
        print(f"• {col_name}: {data_type} {'(Primary Key)' if pk else ''} {'(Required)' if not_null else '(Optional)'}")

if __name__ == "__main__":
    show_user_columns()

