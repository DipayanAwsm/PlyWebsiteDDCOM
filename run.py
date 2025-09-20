#!/usr/bin/env python3
"""
DD and Sons Website - Production Runner
This script runs the Flask application in production mode.
"""

import os
from app import app, init_db

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False for production
    )
