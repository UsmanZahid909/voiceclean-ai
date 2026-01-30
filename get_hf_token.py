#!/usr/bin/env python3
"""
Quick script to help get Hugging Face API token
"""

import webbrowser
import time

def get_huggingface_token():
    print("🤖 Setting up Hugging Face API for VoiceClean AI")
    print("=" * 50)
    
    print("\n📋 Steps to get your FREE API token:")
    print("1. Sign up at Hugging Face (completely free)")
    print("2. Get your API token")
    print("3. Add it to Vercel environment variables")
    
    print("\n🌐 Opening Hugging Face signup page...")
    try:
        webbrowser.open("https://huggingface.co/join")
        time.sleep(2)
        webbrowser.open("https://huggingface.co/settings/tokens")
    except:
        print("Please manually open: https://huggingface.co/join")
        print("Then go to: https://huggingface.co/settings/tokens")
    
    print("\n📝 Instructions:")
    print("1. Create account at: https://huggingface.co/join")
    print("2. Go to: https://huggingface.co/settings/tokens")
    print("3. Click 'New token'")
    print("4. Name: 'VoiceClean AI'")
    print("5. Type: 'Read'")
    print("6. Copy the token (starts with 'hf_')")
    
    print("\n🔧 Add to Vercel:")
    print("1. Go to: https://vercel.com/dashboard")
    print("2. Click your 'voiceclean-ai' project")
    print("3. Settings → Environment Variables")
    print("4. Add: HF_API_TOKEN = your_token_here")
    print("5. Redeploy")
    
    print("\n✅ Once done, your AI will work like Adobe Podcast!")
    
    token = input("\n🔑 Paste your Hugging Face token here (or press Enter to skip): ").strip()
    
    if token and token.startswith('hf_'):
        print(f"\n✅ Great! Your token: {token[:10]}...")
        print("\n🚀 Now add this to Vercel environment variables:")
        print(f"   HF_API_TOKEN = {token}")
        return token
    else:
        print("\n⏭️  No token provided. Your app will work in demo mode.")
        return None

if __name__ == "__main__":
    get_huggingface_token()