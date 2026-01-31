#!/usr/bin/env python3
"""
Test script to verify ElevenLabs API integration
"""

import requests
import os

# ElevenLabs API Configuration
ELEVENLABS_API_KEY = "2f4a679a377bba4185e99e475cf62ba3ccfa9d35e1cc4f16776c76643ff30942"
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"

def test_api_key():
    """Test if the API key is valid"""
    print("🔑 Testing ElevenLabs API key...")
    
    url = f"{ELEVENLABS_BASE_URL}/user"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ API key is valid!")
            print(f"👤 User ID: {user_data.get('xi_user_id', 'unknown')}")
            return True
        elif response.status_code == 401:
            print("❌ API key is invalid!")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Connection error: {e}")
        return False

def test_audio_isolation():
    """Test audio isolation endpoint with a small test file"""
    print("\n🎵 Testing audio isolation endpoint...")
    
    # Create a minimal WAV file for testing (silence)
    # WAV header for 1 second of silence at 16kHz, 16-bit, mono
    wav_header = bytes([
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x24, 0x7E, 0x00, 0x00,  # File size - 8
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        0x66, 0x6D, 0x74, 0x20,  # "fmt "
        0x10, 0x00, 0x00, 0x00,  # Subchunk1Size (16)
        0x01, 0x00,              # AudioFormat (PCM)
        0x01, 0x00,              # NumChannels (1)
        0x40, 0x3E, 0x00, 0x00,  # SampleRate (16000)
        0x80, 0x7C, 0x00, 0x00,  # ByteRate
        0x02, 0x00,              # BlockAlign
        0x10, 0x00,              # BitsPerSample (16)
        0x64, 0x61, 0x74, 0x61,  # "data"
        0x00, 0x7E, 0x00, 0x00   # Subchunk2Size
    ])
    
    # Add 1 second of silence (32000 bytes of zeros for 16kHz 16-bit mono)
    silence_data = bytes(32000)
    test_audio = wav_header + silence_data
    
    url = f"{ELEVENLABS_BASE_URL}/audio-isolation"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    files = {
        'audio': ('test_audio.wav', test_audio, 'audio/wav')
    }
    
    data = {
        'file_format': 'other'
    }
    
    try:
        print(f"📤 Sending {len(test_audio)} bytes to ElevenLabs...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Audio isolation test successful!")
            print(f"📥 Received {len(response.content)} bytes")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed!")
            print(f"Response: {response.text}")
            return False
        elif response.status_code == 400:
            print("❌ Bad request!")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Request error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 ElevenLabs API Integration Test")
    print("=" * 40)
    
    # Test API key
    key_valid = test_api_key()
    
    # Even if user endpoint fails, try audio isolation
    print("\n🎵 Testing audio isolation anyway (API key might work for isolation)...")
    isolation_works = test_audio_isolation()
    
    if isolation_works:
        print("\n🎉 Audio isolation works! ElevenLabs integration should work.")
    elif key_valid:
        print("\n⚠️ API key is valid but audio isolation failed.")
    else:
        print("\n❌ Both API key test and audio isolation failed.")
    
    print("\n" + "=" * 40)