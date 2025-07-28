# Manim Animation Generator with Gemini AI

Create beautiful mathematical animations by simply describing what you want in natural language!

## 🚀 Quick Start

### 1. Get a Gemini API Key (free)
- Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
- Create a new API key
- Copy it

# Manim Animation Generator

Create mathematical animations using natural language descriptions.

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and add your Gemini API key
3. Install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

## Usage

For development with hot reload:
```bash
gradio gradio_app.py
```

For production:
```bash
python gradio_app.py
```

Open http://localhost:7860 in your browser.

## Examples

- "Create a circle that transforms into a square"
- "Show the Pythagorean theorem"
- "Animate Euler's identity"

## Structure

- `gradio_app.py` - Web interface
- `main.py` - MCP server
- `clients/` - Terminal clients

### 3. Install Dependencies (if not already done)
```bash
source .venv/bin/activate
uv pip install -r requirements.txt
```

## 💬 Usage Options

### Option 1: Quick Launcher (Easiest)
```bash
./start_chat.sh
```
This will automatically check dependencies and launch the web interface.

### Option 2: Gradio Chat Interface (Recommended)
Launch the web-based chat interface:
```bash
python gradio_app.py
```
Then open your browser to `http://localhost:7860`

### Option 3: Terminal Clients
- **Simple Client**: `python clients/simple_client.py`
- **Full MCP Client**: `python clients/client_example.py`

### Option 4: MCP Server
Run the MCP server directly:
```bash
python main.py
```
## 📁 Project Structure

```
manim-mcp/
├── main.py              # MCP server implementation
├── gradio_app.py        # Web chat interface (recommended)
├── clients/
│   ├── simple_client.py    # Direct terminal client
│   └── client_example.py   # Full MCP protocol client
├── examples/            # Sample videos and test files
├── media/              # Generated animations
└── requirements.txt    # All dependencies
```

## 💡 Example Requests

Try these animation ideas:

- "Create a circle that transforms into a square"
- "Show the Pythagorean theorem with animated triangles"
- "Animate Euler's identity e^(iπ) + 1 = 0"
- "Create a bouncing ball animation"
- "Show how integration works with rectangles under a curve"
- "Animate the quadratic formula with LaTeX"
- "Create a spinning 3D cube"
- "Show a mathematical proof step by step"

## 🔧 How It Works

1. **You describe** what animation you want in natural language
2. **Gemini AI generates** proper Manim code with LaTeX support
3. **Manim renders** the animation as an MP4 video
4. **You get** a beautiful mathematical animation!

## 📤 Output

- Animations are saved in the `media/` directory
- Web interface displays videos directly in the browser
- High-quality rendering with LaTeX mathematical notation

## 🚨 Troubleshooting

**"GEMINI_API_KEY not set"**:
- Make sure you exported the API key: `export GEMINI_API_KEY='your-key'`

**"Dependencies not installed"**:
- Activate venv: `source .venv/bin/activate`
- Install deps: `uv pip install -r requirements.txt`

**Animation fails to render**:
- Check if the generated code has syntax errors
- Some complex animations might need manual code adjustment
- Try a simpler description first

## ⭐ Features

- ✨ Natural language to Manim code conversion
- 🎬 Automatic animation rendering with LaTeX support
- 💬 Web-based chat interface
- 🔧 Multiple client options (web, terminal, MCP)
- 📊 Mathematical notation support
- 🚀 Simple command-line interface
- 🎯 No need to know Manim syntax
- 📱 Works with free Gemini API

Enjoy creating beautiful mathematical animations! 🎉

## Credits

This project is based on the MCP framework developed by [Avik-creator](https://github.com/Avik-creator/MCP.git).
