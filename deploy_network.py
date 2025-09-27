#!/usr/bin/env python3
"""
Network Deployment Script for DD and Sons Website
This script helps deploy the website on your local WiFi network
"""

import subprocess
import socket
import json
import os
import qrcode
from PIL import Image
import webbrowser

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "192.168.0.102"  # Fallback IP

def create_qr_code(url, filename):
    """Create QR code for the website URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"✅ QR code saved as: {filename}")

def update_config_for_network():
    """Update configuration for network deployment"""
    config_file = 'config.json'
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Update host to bind to all interfaces
        config['FLASK']['HOST'] = '0.0.0.0'
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration updated for network access")
    else:
        print("❌ config.json not found")

def check_firewall():
    """Check and provide firewall instructions"""
    print("\n🔥 Firewall Configuration:")
    print("=" * 50)
    print("To allow network access, you may need to:")
    print("1. Open System Preferences → Security & Privacy → Firewall")
    print("2. Click 'Firewall Options'")
    print("3. Add Python to allowed applications")
    print("4. Or temporarily disable firewall for testing")

def main():
    """Main deployment function"""
    print("🌐 DD and Sons - Network Deployment")
    print("=" * 50)
    
    # Get local IP
    local_ip = get_local_ip()
    port = 8080
    website_url = f"http://{local_ip}:{port}"
    
    print(f"📍 Your Local IP: {local_ip}")
    print(f"🌐 Website URL: {website_url}")
    print(f"🔌 Port: {port}")
    
    # Update configuration
    update_config_for_network()
    
    # Create QR codes
    print(f"\n📱 Creating QR Codes...")
    create_qr_code(website_url, "website_qr.png")
    create_qr_code(f"{website_url}/login", "login_qr.png")
    create_qr_code(f"{website_url}/contact", "contact_qr.png")
    
    # Display access information
    print(f"\n🎯 Network Access Information:")
    print("=" * 50)
    print(f"📱 Main Website: {website_url}")
    print(f"🔐 Admin Login: {website_url}/login")
    print(f"📞 Contact Page: {website_url}/contact")
    print(f"📊 Dashboard: {website_url}/dashboard")
    
    print(f"\n👥 For Other Devices on Your WiFi:")
    print("-" * 30)
    print("• Open any web browser")
    print(f"• Go to: {website_url}")
    print("• Or scan the QR code with your phone")
    
    print(f"\n🔑 Admin Credentials:")
    print("-" * 20)
    print("Username: admin")
    print("Password: admin123")
    
    # Check firewall
    check_firewall()
    
    print(f"\n🚀 To Start the Server:")
    print("-" * 25)
    print("python app.py")
    print(f"\nThen access from any device: {website_url}")
    
    # Ask if user wants to open browser
    try:
        response = input(f"\n🌐 Open website in browser? (y/n): ").lower()
        if response == 'y':
            webbrowser.open(website_url)
    except:
        pass

if __name__ == "__main__":
    main()

