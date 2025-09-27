#!/usr/bin/env python3
"""
Database Viewer for DD and Sons Website
This script allows you to view and manage the database contents.
"""

import sqlite3
import json
from datetime import datetime

def connect_db():
    """Connect to the SQLite database"""
    return sqlite3.connect('instance/dd_sons.db')

def show_tables():
    """Show all tables in the database"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("📊 Database Tables:")
    print("=" * 50)
    for table in tables:
        print(f"• {table[0]}")
    
    conn.close()
    return [table[0] for table in tables]

def show_table_structure(table_name):
    """Show the structure of a specific table"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    
    print(f"\n📋 Table Structure: {table_name}")
    print("=" * 50)
    for col in columns:
        print(f"• {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
    
    conn.close()

def show_table_data(table_name, limit=10):
    """Show data from a specific table"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    total_rows = cursor.fetchone()[0]
    
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"\n📄 Table Data: {table_name} (Showing {len(rows)} of {total_rows} rows)")
    print("=" * 80)
    
    if rows:
        # Print column headers
        print(" | ".join(f"{col:15}" for col in columns))
        print("-" * 80)
        
        # Print data rows
        for row in rows:
            formatted_row = []
            for item in row:
                if item is None:
                    formatted_row.append("NULL")
                elif isinstance(item, str) and len(item) > 15:
                    formatted_row.append(item[:12] + "...")
                else:
                    formatted_row.append(str(item))
            print(" | ".join(f"{item:15}" for item in formatted_row))
    else:
        print("No data found in this table.")
    
    conn.close()

def show_users():
    """Show user accounts"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email, role, password,created_at FROM user;")
    users = cursor.fetchall()
    
    print("\n👥 User Accounts:")
    print("=" * 80)
    print(f"{'ID':<5} | {'Username':<15} | {'Email':<25} | {'Role':<10} | {'Created'}")
    print("-" * 80)
    
    for user in users:
        print(f"{user[0]:<5} | {user[1]:<15} | {user[2]:<25} | {user[3]:<10} | {user[4]}")
    
    conn.close()

def show_categories():
    """Show product categories"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, description, created_at FROM category;")
    categories = cursor.fetchall()
    
    print("\n📦 Product Categories:")
    print("=" * 80)
    print(f"{'ID':<5} | {'Name':<20} | {'Description':<30} | {'Created'}")
    print("-" * 80)
    
    for cat in categories:
        desc = cat[2][:27] + "..." if cat[2] and len(cat[2]) > 30 else cat[2] or "No description"
        print(f"{cat[0]:<5} | {cat[1]:<20} | {desc:<30} | {cat[3]}")
    
    conn.close()

def show_products():
    """Show products"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.id, p.name, c.name as category, p.price, p.availability, p.created_at 
        FROM product p 
        LEFT JOIN category c ON p.category_id = c.id
        ORDER BY p.created_at DESC
        LIMIT 20;
    """)
    products = cursor.fetchall()
    
    print("\n🛍️ Products (Latest 20):")
    print("=" * 100)
    print(f"{'ID':<5} | {'Name':<25} | {'Category':<15} | {'Price':<10} | {'Available':<10} | {'Created'}")
    print("-" * 100)
    
    for prod in products:
        name = prod[1][:22] + "..." if len(prod[1]) > 25 else prod[1]
        category = prod[2] or "No category"
        price = f"₹{prod[3]}" if prod[3] else "N/A"
        available = "Yes" if prod[4] else "No"
        print(f"{prod[0]:<5} | {name:<25} | {category:<15} | {price:<10} | {available:<10} | {prod[5]}")
    
    conn.close()

def show_analytics():
    """Show website analytics"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Page views
    cursor.execute("SELECT COUNT(*) FROM page_view;")
    total_views = cursor.fetchone()[0]
    
    # Unique visitors
    cursor.execute("SELECT COUNT(DISTINCT ip_address) FROM page_view;")
    unique_visitors = cursor.fetchone()[0]
    
    # Popular pages
    cursor.execute("""
        SELECT page_path, COUNT(*) as views 
        FROM page_view 
        GROUP BY page_path 
        ORDER BY views DESC 
        LIMIT 10;
    """)
    popular_pages = cursor.fetchall()
    
    print("\n📈 Website Analytics:")
    print("=" * 60)
    print(f"Total Page Views: {total_views}")
    print(f"Unique Visitors: {unique_visitors}")
    
    print("\n🔥 Popular Pages:")
    print("-" * 40)
    for page in popular_pages:
        print(f"• {page[0]}: {page[1]} views")
    
    conn.close()

def main():
    """Main function"""
    print("🗄️  DD and Sons Database Viewer")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Show all tables")
        print("2. Show table structure")
        print("3. Show table data")
        print("4. Show users")
        print("5. Show categories")
        print("6. Show products")
        print("7. Show analytics")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            show_tables()
        elif choice == '2':
            tables = show_tables()
            table_name = input("Enter table name: ").strip()
            if table_name in tables:
                show_table_structure(table_name)
            else:
                print("❌ Table not found!")
        elif choice == '3':
            tables = show_tables()
            table_name = input("Enter table name: ").strip()
            if table_name in tables:
                limit = input("Enter limit (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                show_table_data(table_name, limit)
            else:
                print("❌ Table not found!")
        elif choice == '4':
            show_users()
        elif choice == '5':
            show_categories()
        elif choice == '6':
            show_products()
        elif choice == '7':
            show_analytics()
        elif choice == '8':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
