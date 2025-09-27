#!/usr/bin/env python3
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
