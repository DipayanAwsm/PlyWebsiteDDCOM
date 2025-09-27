#!/usr/bin/env python3
"""
Database initialization script for production
"""

import os
import sys
from app import app, db, User, bcrypt, Category, ContactInfo

def init_production_db():
    """Initialize database for production deployment"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            # Create admin user
            admin_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin_user = User(
                username='admin',
                email='admin@ddandsons.com',
                password_hash=admin_password,
                role='admin'
            )
            db.session.add(admin_user)
            print("✅ Admin user created")
        else:
            print("✅ Admin user already exists")
        
        # Create default categories if they don't exist
        categories = [
            {'name': 'Various Kinds of Plywood', 'description': 'High-quality plywood in various grades and sizes'},
            {'name': 'Sunmica', 'description': 'Premium laminates and sunmica sheets'},
            {'name': 'Plywood Doors', 'description': 'Durable and stylish plywood doors'},
            {'name': 'Plastic Doors', 'description': 'Modern plastic doors'},
            {'name': 'Bit for Finishing', 'description': 'Essential finishing materials and accessories'}
        ]
        
        for cat_data in categories:
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
                print(f"✅ Created category: {cat_data['name']}")
        
        # Create default contact info
        contact_info = ContactInfo.query.first()
        if not contact_info:
            contact_info = ContactInfo(
                company_name='DD and Sons',
                phone='+91-9876543210',
                email='info@ddandsons.com',
                address='123 Industrial Area, City, State - 123456',
                latitude=28.6139,
                longitude=77.209
            )
            db.session.add(contact_info)
            print("✅ Default contact info created")
        
        db.session.commit()
        print("✅ Database initialization completed")

if __name__ == '__main__':
    init_production_db()
