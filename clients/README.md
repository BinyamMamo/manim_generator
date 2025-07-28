# Client Implementations

This directory contains different ways to interact with the Manim MCP server:

## 🖥️ Terminal Clients

### `simple_client.py`
- **Best for**: Quick testing and simple usage
- **Features**: Direct Gemini integration, minimal setup
- **Usage**: `python simple_client.py`

### `client_example.py` 
- **Best for**: Full MCP protocol implementation
- **Features**: Complete MCP client with session management
- **Usage**: `python client_example.py`

## 🚀 Quick Start

1. Set your API key:
   ```bash
   export GEMINI_API_KEY='your-api-key-here'
   ```

2. Run a client:
   ```bash
   python simple_client.py
   ```

3. Describe your animation:
   ```
   > Create a circle that transforms into a square
   ```

## 💡 Pro Tip

For the best experience, use the main Gradio web interface:
```bash
cd .. && python gradio_app.py
```
