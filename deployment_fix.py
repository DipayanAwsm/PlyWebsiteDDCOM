#!/usr/bin/env python3
"""
Deployment fix script for Render
"""

import os
import sys
import json

def create_render_config():
    """Create configuration for Render deployment"""
    
    print("🔧 Creating Render Configuration...")
    
    # Create render.yaml for proper deployment
    render_config = """services:
  - type: web
    name: dd-sons-website
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python run.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: FLASK_DEBUG
        value: false
      - key: SECRET_KEY
        value: your-production-secret-key-here
      - key: DATABASE_URL
        value: sqlite:///dd_sons.db
"""
    
    with open('render.yaml', 'w') as f:
        f.write(render_config)
    print("✅ Created render.yaml")
    
    # Create production config
    production_config = {
        "FLASK": {
            "SECRET_KEY": "production-secret-key-change-this",
            "DEBUG": False,
            "HOST": "0.0.0.0",
            "PORT": 10000
        },
        "DATABASE": {
            "URI": "sqlite:///dd_sons.db"
        },
        "UPLOAD": {
            "FOLDER": "static/uploads",
            "MAX_SIZE": 104857600
        },
        "GOOGLE_MAPS": {
            "API_KEY": "YOUR_GOOGLE_MAPS_API_KEY"
        },
        "ADMIN": {
            "DEFAULT_USERNAME": "admin",
            "DEFAULT_PASSWORD": "admin123",
            "DEFAULT_EMAIL": "admin@ddandsons.com"
        },
        "COMPANY": {
            "NAME": "DD and Sons",
            "PHONE": "+91-9876543210",
            "EMAIL": "info@ddandsons.com",
            "ADDRESS": "123 Industrial Area, City, State - 123456",
            "LATITUDE": 28.6139,
            "LONGITUDE": 77.209
        },
        "LOGGING": {
            "LEVEL": "INFO",
            "MAX_FILE_SIZE": 10485760,
            "BACKUP_COUNT": 10,
            "LOG_DIRECTORY": "logs"
        }
    }
    
    with open('config_production.json', 'w') as f:
        json.dump(production_config, f, indent=2)
    print("✅ Created config_production.json")
    
    # Create database initialization script
    init_script = '''#!/usr/bin/env python3
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
'''
    
    with open('init_production_db.py', 'w') as f:
        f.write(init_script)
    print("✅ Created init_production_db.py")
    
    # Update run.py for production
    run_script = '''#!/usr/bin/env python3
"""
Production runner for Render deployment
"""

import os
import sys
from app import app, config, init_db, logger

if __name__ == '__main__':
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    print("🚀 Starting DD and Sons Production Application...")
    print(f"📍 Host: {config['FLASK']['HOST']}")
    print(f"🔌 Port: {config['FLASK']['PORT']}")
    print(f"🐛 Debug: {config['FLASK']['DEBUG']}")
    print("=" * 50)
    
    try:
        # Initialize database
        init_db()
        print("✅ Database initialized successfully")
        
        # Run the Flask app
        print(f"🌐 Starting Flask server on {config['FLASK']['HOST']}:{config['FLASK']['PORT']}")
        
        app.run(
            debug=config['FLASK']['DEBUG'],
            host=config['FLASK']['HOST'],
            port=int(config['FLASK']['PORT']),
            use_reloader=False
        )
        
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        sys.exit(1)
'''
    
    with open('run_production.py', 'w') as f:
        f.write(run_script)
    print("✅ Created run_production.py")

def main():
    print("🔧 Creating Deployment Configuration...")
    print("=" * 50)
    
    create_render_config()
    
    print("\n📋 Next Steps for Render Deployment:")
    print("1. Update your Render service to use 'run_production.py' as start command")
    print("2. Set environment variables in Render dashboard:")
    print("   - FLASK_ENV=production")
    print("   - FLASK_DEBUG=false")
    print("   - SECRET_KEY=your-secure-secret-key")
    print("3. Run 'python init_production_db.py' after deployment to initialize database")
    print("4. Test admin access at: https://plywebsiteddcom.onrender.com/login-clean")
    
    print("\n🔐 Admin Credentials:")
    print("Username: admin")
    print("Password: admin123")

if __name__ == '__main__':
    main()
