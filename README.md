# Manim Animation Generator with Gemini AI

Create beautiful mathematical animations by simply describing what you want in natural language!

## Setup

1. **Get a Gemini API Key** (free):
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy it

2. **Set the API Key**:
   ```bash
   export GEMINI_API_KEY='your-api-key-here'
   ```

3. **Install Dependencies** (if not already done):
   ```bash
   source .venv/bin/activate
   uv pip install -r client_requirements.txt
   ```

## Usage

### Option 1: Simple Client (Recommended)
```bash
./start_client.sh
```

### Option 2: Direct Python
```bash
source .venv/bin/activate
export GEMINI_API_KEY='your-api-key-here'
python simple_client.py
```

## Example Requests

Try these animation ideas:

- "Create a circle that transforms into a square"
- "Show the Pythagorean theorem with animated triangles"
- "Animate a sine wave being drawn"
- "Create a bouncing ball animation"
- "Show how integration works with rectangles under a curve"
- "Animate the quadratic formula"
- "Create a spinning 3D cube"
- "Show a mathematical proof step by step"

## How It Works

1. **You describe** what animation you want in natural language
2. **Gemini AI generates** proper Manim code based on your description
3. **Manim renders** the animation as an MP4 video
4. **You get** a beautiful mathematical animation!

## Output

- Animations are saved as MP4 files in the current directory
- Each animation is named after the scene class (e.g., `MyAnimation.mp4`)
- Medium quality rendering for faster generation

## Troubleshooting

**"GEMINI_API_KEY not set"**:
- Make sure you exported the API key: `export GEMINI_API_KEY='your-key'`

**"Dependencies not installed"**:
- Activate venv: `source .venv/bin/activate`
- Install deps: `uv pip install -r client_requirements.txt`

**Animation fails to render**:
- Check if the generated code has syntax errors
- Some complex animations might need manual code adjustment
- Try a simpler description first

## Features

- ✨ Natural language to Manim code conversion
- 🎬 Automatic animation rendering
- 🚀 Simple command-line interface
- 🎯 No need to know Manim syntax
- 📱 Works with free Gemini API

Enjoy creating beautiful mathematical animations! 🎉

## Credits

This project is based on the MCP framework developed by [Avik-creator](https://github.com/Avik-creator/MCP.git).
