#!/usr/bin/env python3
"""
Simple Flask runner script to avoid Streamlit conflicts
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
from app import app, config, init_db, logger

if __name__ == '__main__':
    print("🚀 Starting DD and Sons Flask Application...")
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
        print("🔗 Access your website at:")
        print(f"   http://{config['FLASK']['HOST']}:{config['FLASK']['PORT']}")
        print(f"   http://localhost:{config['FLASK']['PORT']}")
        print("=" * 50)
        
        app.run(
            debug=config['FLASK']['DEBUG'],
            host=config['FLASK']['HOST'],
            port=config['FLASK']['PORT'],
            use_reloader=False  # Disable reloader to avoid conflicts
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        sys.exit(1)
