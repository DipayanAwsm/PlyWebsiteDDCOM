#!/usr/bin/env python3
"""
DD and Sons Website - Configuration Manager
This script helps manage the application configuration.
"""

import json
import os
import secrets

def create_default_config():
    """Create a default configuration file"""
    default_config = {
        "FLASK": {
            "SECRET_KEY": secrets.token_hex(16),
            "DEBUG": True,
            "HOST": "127.0.0.1",
            "PORT": 5000
        },
        "DATABASE": {
            "URI": "sqlite:///dd_sons.db"
        },
        "UPLOAD": {
            "FOLDER": "static/uploads",
            "MAX_SIZE": 16777216  # 16MB in bytes
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
            "LONGITUDE": 77.2090
        }
    }
    
    with open('config.json', 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print("✅ Default configuration created in config.json")
    return default_config

def load_config():
    """Load configuration from file"""
    if not os.path.exists('config.json'):
        print("❌ config.json not found. Creating default configuration...")
        return create_default_config()
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✅ Configuration loaded from config.json")
        return config
    except Exception as e:
        print(f"❌ Error loading config.json: {e}")
        print("Creating default configuration...")
        return create_default_config()

def update_config(section, key, value):
    """Update a specific configuration value"""
    config = load_config()
    
    if section not in config:
        config[section] = {}
    
    config[section][key] = value
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Updated {section}.{key} = {value}")

def show_config():
    """Display current configuration"""
    config = load_config()
    print("\n📋 Current Configuration:")
    print("=" * 50)
    
    for section, values in config.items():
        print(f"\n🔧 {section}:")
        for key, value in values.items():
            if key == "SECRET_KEY" or key == "API_KEY":
                display_value = f"{value[:8]}..." if len(str(value)) > 8 else "***"
            else:
                display_value = value
            print(f"  {key}: {display_value}")

def interactive_setup():
    """Interactive configuration setup"""
    print("\n🚀 DD and Sons Website - Configuration Setup")
    print("=" * 50)
    
    config = load_config()
    
    # Flask settings
    print("\n📡 Flask Settings:")
    port = input(f"Port [{config['FLASK']['PORT']}]: ").strip()
    if port:
        config['FLASK']['PORT'] = int(port)
    
    host = input(f"Host [{config['FLASK']['HOST']}]: ").strip()
    if host:
        config['FLASK']['HOST'] = host
    
    debug = input(f"Debug mode (true/false) [{config['FLASK']['DEBUG']}]: ").strip().lower()
    if debug in ['true', 'false']:
        config['FLASK']['DEBUG'] = debug == 'true'
    
    # Admin settings
    print("\n👤 Admin Settings:")
    username = input(f"Admin username [{config['ADMIN']['DEFAULT_USERNAME']}]: ").strip()
    if username:
        config['ADMIN']['DEFAULT_USERNAME'] = username
    
    password = input(f"Admin password [{config['ADMIN']['DEFAULT_PASSWORD']}]: ").strip()
    if password:
        config['ADMIN']['DEFAULT_PASSWORD'] = password
    
    email = input(f"Admin email [{config['ADMIN']['DEFAULT_EMAIL']}]: ").strip()
    if email:
        config['ADMIN']['DEFAULT_EMAIL'] = email
    
    # Google Maps
    print("\n🗺️ Google Maps:")
    api_key = input(f"Google Maps API Key [{config['GOOGLE_MAPS']['API_KEY']}]: ").strip()
    if api_key:
        config['GOOGLE_MAPS']['API_KEY'] = api_key
    
    # Company info
    print("\n🏢 Company Information:")
    company_name = input(f"Company name [{config['COMPANY']['NAME']}]: ").strip()
    if company_name:
        config['COMPANY']['NAME'] = company_name
    
    phone = input(f"Phone [{config['COMPANY']['PHONE']}]: ").strip()
    if phone:
        config['COMPANY']['PHONE'] = phone
    
    email = input(f"Email [{config['COMPANY']['EMAIL']}]: ").strip()
    if email:
        config['COMPANY']['EMAIL'] = email
    
    address = input(f"Address [{config['COMPANY']['ADDRESS']}]: ").strip()
    if address:
        config['COMPANY']['ADDRESS'] = address
    
    # Save configuration
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Configuration saved successfully!")
    show_config()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'show':
            show_config()
        elif command == 'create':
            create_default_config()
        elif command == 'setup':
            interactive_setup()
        elif command == 'update' and len(sys.argv) >= 5:
            section = sys.argv[2]
            key = sys.argv[3]
            value = sys.argv[4]
            update_config(section, key, value)
        else:
            print("Usage:")
            print("  python config_manager.py show          - Show current configuration")
            print("  python config_manager.py create        - Create default configuration")
            print("  python config_manager.py setup         - Interactive setup")
            print("  python config_manager.py update <section> <key> <value> - Update specific setting")
    else:
        interactive_setup()

