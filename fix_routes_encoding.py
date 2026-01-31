#!/usr/bin/env python3
"""
Fix character encoding issues in Flask routes
"""

import os
import subprocess

def fix_flask_routes():
    print("🔧 Fixing Flask routes encoding issues...")
    
    # Read the file with proper encoding
    try:
        with open('api/index.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        content = None
        for encoding in encodings:
            try:
                with open('api/index.py', 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"✅ Successfully read file with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print("❌ Could not read file with any encoding")
            return False
    
    # Clean up any problematic characters
    content = content.replace('\x9d', '')  # Remove problematic character
    
    # Ensure proper Flask app initialization
    if "app = Flask(__name__)" in content and "template_folder" not in content:
        content = content.replace(
            "app = Flask(__name__)",
            "app = Flask(__name__, template_folder='templates')"
        )
        print("✅ Added template folder specification")
    
    # Write back with UTF-8 encoding
    with open('api/index.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed encoding issues in Flask routes")
    return True

def deploy_fix():
    print("🚀 Deploying fix...")
    
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'fix: Resolve character encoding issues in Flask routes'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("✅ Fix deployed successfully")
        return True
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    if fix_flask_routes():
        deploy_fix()
        print("\n⏳ Waiting for deployment to complete...")
        print("🔗 Check your app: https://voiceclean-ai.vercel.app")
    else:
        print("❌ Failed to fix routes")