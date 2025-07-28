#!/usr/bin/env python3
"""
Simple Manim Animation Generator using Gemini AI and Manim MCP Server
"""

import asyncio
import json
import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Check if we have the required environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ Please set GEMINI_API_KEY environment variable")
    print("   export GEMINI_API_KEY='your-api-key-here'")
    sys.exit(1)

try:
    import google.generativeai as genai
except ImportError:
    print("❌ Please install google-generativeai: pip install google-generativeai")
    sys.exit(1)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def generate_manim_code(user_request: str) -> str:
    """Generate Manim code using Gemini AI"""
    
    prompt = f"""
You are a professional Manim developer. Your task is to generate correct Manim code that will run without errors and create the animation the user requested.

User Request: {user_request}

Requirements:
1. Use Manim Community (import from manim import *)
2. Create a Scene class that inherits from Scene
3. Implement the construct method
4. Use proper Manim syntax and methods
5. Make sure the code is complete and runnable
6. Include appropriate colors, animations, and styling
7. The scene should be visually appealing and clear

Return ONLY the Python code, no explanations or markdown formatting.

Example structure:
```python
from manim import *

class MyAnimation(Scene):
    def construct(self):
        # Your animation code here
        pass
```
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error generating code with Gemini: {e}")
        return None

def execute_manim_code(manim_code: str) -> str:
    """Execute Manim code directly"""
    
    # Create a temporary directory for this animation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Write the code to a temporary file
        code_file = temp_path / "animation.py"
        with open(code_file, 'w') as f:
            f.write(manim_code)
        
        # Create media directory
        media_dir = temp_path / "media"
        media_dir.mkdir(exist_ok=True)
        
        # Extract scene class name from the code
        scene_name = None
        for line in manim_code.split('\n'):
            if 'class ' in line and '(Scene)' in line:
                scene_name = line.split('class ')[1].split('(')[0].strip()
                break
        
        if not scene_name:
            return "❌ Could not find Scene class in the generated code"
        
        try:
            # Run manim command
            cmd = [
                sys.executable, "-m", "manim", 
                str(code_file), scene_name, 
                "-q", "m",  # medium quality
                "--media_dir", str(media_dir)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=temp_dir,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode == 0:
                # Find the output video file
                video_files = list(media_dir.glob("**/*.mp4"))
                if video_files:
                    output_file = video_files[0]
                    
                    # Copy to current directory
                    final_output = Path(f"{scene_name}.mp4")
                    final_output.write_bytes(output_file.read_bytes())
                    
                    return f"✅ Animation created successfully: {final_output.absolute()}"
                else:
                    return "❌ Animation completed but no video file found"
            else:
                return f"❌ Manim execution failed:\n{result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "❌ Animation timed out (took longer than 60 seconds)"
        except Exception as e:
            return f"❌ Error executing animation: {str(e)}"

def main():
    print("🎬 Manim Animation Generator with Gemini AI")
    print("=" * 50)
    print("Type your animation request or 'quit' to exit")
    print("Examples:")
    print("  - Create a circle that changes color")
    print("  - Show the Pythagorean theorem")
    print("  - Animate a mathematical function")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n🎯 What animation do you want? > ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Generating Manim code with Gemini...")
            manim_code = generate_manim_code(user_input)
            
            if not manim_code:
                continue
            
            # Clean up the code (remove markdown if present)
            if "```python" in manim_code:
                manim_code = manim_code.split("```python")[1].split("```")[0].strip()
            elif "```" in manim_code:
                manim_code = manim_code.split("```")[1].split("```")[0].strip()
            
            print("\n📝 Generated code:")
            print("-" * 40)
            print(manim_code)
            print("-" * 40)
            
            # Ask if user wants to execute
            execute = input("\n🎬 Execute this animation? (y/n): ").strip().lower()
            
            if execute in ['y', 'yes']:
                print("\n🎥 Creating animation...")
                result = execute_manim_code(manim_code)
                print(result)
            else:
                print("⏭️  Animation skipped")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            continue

if __name__ == "__main__":
    main()
