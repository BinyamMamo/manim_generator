#!/bin/bash
# Setup script for Manim MCP Client

echo "🎬 Setting up Manim Animation Generator"
echo "======================================"

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set!"
    echo ""
    echo "Please set your Gemini API key:"
    echo "  export GEMINI_API_KEY='your-api-key-here'"
    echo ""
    echo "You can get a free API key from: https://makersuite.google.com/app/apikey"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python -c "import google.generativeai, manim" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencies not installed properly"
    echo "Please run: source .venv/bin/activate && uv pip install -r client_requirements.txt"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 Starting Manim Animation Generator..."
echo "   You can now describe animations and I'll create them for you!"
echo ""

# Run the simple client
python simple_client.py
