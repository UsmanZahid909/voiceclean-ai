#!/usr/bin/env python3
"""
Automatic setup for VoiceClean AI with Resemble Enhance
"""

import os
import requests
import json

def setup_huggingface_token():
    """Setup Hugging Face token automatically"""
    print("🤖 Setting up VoiceClean AI with Resemble Enhance")
    print("=" * 60)
    
    # Check if token already exists
    token = os.getenv('HF_API_TOKEN')
    if token and token != 'hf_your_token_here':
        print(f"✅ Hugging Face token already configured: {token[:10]}...")
        return test_api_connection(token)
    
    print("\n📋 To get FREE Hugging Face API access:")
    print("1. Go to: https://huggingface.co/join")
    print("2. Sign up (completely free)")
    print("3. Go to: https://huggingface.co/settings/tokens")
    print("4. Create new token with 'Read' access")
    print("5. Copy the token (starts with 'hf_')")
    
    print("\n🔧 Add to Vercel Environment Variables:")
    print("   Variable: HF_API_TOKEN")
    print("   Value: your_token_here")
    
    return False

def test_api_connection(token):
    """Test if the API connection works"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test Resemble AI API
        print("\n🧪 Testing Resemble AI API...")
        response = requests.get(
            "https://api-inference.huggingface.co/models/ResembleAI/resemble-enhance",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Resemble AI API: Working!")
            return True
        elif response.status_code == 503:
            print("⏳ Resemble AI API: Model loading (will work soon)")
            return True
        else:
            print(f"❌ Resemble AI API: Error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🎵 VoiceClean AI - Resemble Enhance Integration")
    print("=" * 60)
    
    # Setup token
    if setup_huggingface_token():
        print("\n🎉 Setup Complete!")
        print("✅ Your VoiceClean AI now uses Resemble Enhance")
        print("✅ Professional audio enhancement like Adobe Podcast")
        print("✅ Background noise removal")
        print("✅ Voice clarity enhancement")
        print("\n🚀 Deploy to Vercel and start enhancing audio!")
    else:
        print("\n⚠️  Setup incomplete - running in demo mode")
        print("💡 Add HF_API_TOKEN to enable AI enhancement")

if __name__ == "__main__":
    main()