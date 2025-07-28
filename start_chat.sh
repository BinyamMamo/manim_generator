#!/bin/bash
# Quick launcher for Manim Animation Chat

echo "🎬 Manim Animation Chat Launcher"
echo "================================="

# Check if API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set!"
    echo "Please run: export GEMINI_API_KEY='your-api-key-here'"
    echo "Get your key from: https://aistudio.google.com/app/apikey"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔄 Activating virtual environment..."
    source .venv/bin/activate
fi

# Install gradio if not present
if ! python -c "import gradio" 2>/dev/null; then
    echo "📦 Installing Gradio..."
    uv pip install gradio
fi

echo "🚀 Starting Gradio interface..."
echo "🌐 Open your browser to: http://localhost:7860"
echo "📝 Describe animations in natural language!"
echo ""

python gradio_app.py
