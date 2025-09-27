#!/usr/bin/env python3
"""
DD and Sons Website - Production Runner
This script runs the Flask application in production mode.
"""

import os
import json
from app import app, init_db, config

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Override config for production
    production_config = config.copy()
    production_config['FLASK']['DEBUG'] = False
    production_config['FLASK']['HOST'] = '0.0.0.0'
    
    # Get port from environment variable or use config
    port = int(os.environ.get('PORT', production_config['FLASK']['PORT']))
    production_config['FLASK']['PORT'] = port
    
    print(f"Starting DD and Sons website on {production_config['FLASK']['HOST']}:{port}")
    print(f"Debug mode: {production_config['FLASK']['DEBUG']}")
    
    # Run the application
    app.run(
        host=production_config['FLASK']['HOST'],
        port=production_config['FLASK']['PORT'],
        debug=production_config['FLASK']['DEBUG']
    )
