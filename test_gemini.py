#!/usr/bin/env python3
"""Test script to verify Gemini API connection"""

import os
import sys

# Check API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not set!")
    print("Please run: export GEMINI_API_KEY='your-api-key-here'")
    sys.exit(1)

try:
    import google.generativeai as genai
    print("✅ google-generativeai imported successfully")
except ImportError:
    print("❌ google-generativeai not installed")
    print("Please run: uv pip install google-generativeai")
    sys.exit(1)

try:
    # Configure and test Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    print("🧪 Testing Gemini API connection...")
    response = model.generate_content("Hello! Please respond with 'API connection successful'")
    print(f"✅ Gemini response: {response.text}")
    
    print("\n🎉 All tests passed! You're ready to use the client.")
    
except Exception as e:
    print(f"❌ Gemini API test failed: {e}")
    print("Please check your API key is correct")
    sys.exit(1)
