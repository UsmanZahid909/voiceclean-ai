#!/usr/bin/env python3
"""
Quick test to verify the deployment and check if login/signup buttons are in the HTML
"""

import requests
import sys

def test_deployment():
    try:
        # Test the main page
        print("🔍 Testing main page...")
        response = requests.get("https://voiceclean-ai.vercel.app/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Main page is accessible")
            
            # Check for login/signup buttons in HTML
            html_content = response.text.lower()
            
            if 'sign in' in html_content and 'sign up' in html_content:
                print("✅ Login/Signup buttons found in HTML")
            else:
                print("❌ Login/Signup buttons NOT found in HTML")
                
            if '/login' in html_content and '/signup' in html_content:
                print("✅ Login/Signup links found in HTML")
            else:
                print("❌ Login/Signup links NOT found in HTML")
                
        else:
            print(f"❌ Main page returned status code: {response.status_code}")
            
        # Test login page
        print("\n🔍 Testing login page...")
        login_response = requests.get("https://voiceclean-ai.vercel.app/login", timeout=10)
        
        if login_response.status_code == 200:
            print("✅ Login page is accessible")
        else:
            print(f"❌ Login page returned status code: {login_response.status_code}")
            
        # Test signup page
        print("\n🔍 Testing signup page...")
        signup_response = requests.get("https://voiceclean-ai.vercel.app/signup", timeout=10)
        
        if signup_response.status_code == 200:
            print("✅ Signup page is accessible")
        else:
            print(f"❌ Signup page returned status code: {signup_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing deployment: {e}")

if __name__ == "__main__":
    test_deployment()