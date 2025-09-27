#!/usr/bin/env python3
"""
Test server connectivity and login functionality
"""

import requests
import json

def test_server():
    """Test if the server is running and accessible"""
    base_url = "http://127.0.0.1:8080"
    
    print("🔍 Testing DD and Sons Server")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Server is running - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        print("   Make sure to start the server with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False
    
    # Test 2: Check login page
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        print(f"✅ Login page accessible - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Login page error: {e}")
        return False
    
    # Test 3: Test login form submission
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        print("🔄 Testing login form submission...")
        response = requests.post(f"{base_url}/login", data=login_data, timeout=5, allow_redirects=False)
        
        print(f"✅ Login form submitted - Status: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ Login successful (redirect to dashboard)")
            print(f"   Redirect location: {response.headers.get('Location', 'Not specified')}")
        elif response.status_code == 200:
            print("⚠️  Login failed (staying on login page)")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Login form submission error: {e}")
        return False
    
    # Test 4: Check simple login page
    try:
        response = requests.get(f"{base_url}/login-simple", timeout=5)
        print(f"✅ Simple login page accessible - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Simple login page error: {e}")
    
    print("\n🎯 Summary:")
    print("If all tests pass, the server is working correctly.")
    print("If login form submission fails, check the server logs for errors.")
    
    return True

if __name__ == "__main__":
    test_server()

