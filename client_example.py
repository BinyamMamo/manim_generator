#!/usr/bin/env python3
"""
Simple MCP client to interact with the Manim MCP server using Gemini.
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict, List
import google.generativeai as genai
import os
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Please set GEMINI_API_KEY environment variable")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

class ManimMCPClient:
    def __init__(self):
        self.session = None
        
    async def connect(self):
        """Connect to the MCP server"""
        # Start the MCP server as a subprocess
        server_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Create stdio client
        stdio_transport = stdio_client(server_process.stdin, server_process.stdout)
        
        # Create session
        self.session = ClientSession(stdio_transport)
        await self.session.__aenter__()
        
        # Initialize the session
        await self.session.initialize()
        
        return server_process
    
    async def list_tools(self):
        """List available tools from the MCP server"""
        result = await self.session.list_tools()
        return result.tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Call a tool on the MCP server"""
        result = await self.session.call_tool(tool_name, arguments)
        return result.content
    
    async def get_prompt(self, prompt_name: str, arguments: Dict[str, Any]):
        """Get a prompt from the MCP server"""
        result = await self.session.get_prompt(prompt_name, arguments)
        return result.messages

async def main():
    client = ManimMCPClient()
    
    try:
        # Connect to MCP server
        print("🔌 Connecting to Manim MCP server...")
        server_process = await client.connect()
        
        # List available tools
        print("\n📋 Available tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Interactive loop
        print("\n🎬 Manim Animation Generator")
        print("Type your animation request (or 'quit' to exit):")
        
        while True:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            try:
                # Get Manim code generation prompt
                print("🤖 Getting Manim code prompt...")
                prompt_result = await client.get_prompt("manim_prompt", {"prompt": user_input})
                manim_prompt = prompt_result[0].content.text if prompt_result else ""
                
                # Use Gemini to generate Manim code
                print("✨ Generating Manim code with Gemini...")
                response = model.generate_content(manim_prompt)
                manim_code = response.text
                
                print(f"\n📝 Generated Manim code:\n{manim_code}")
                
                # Ask user if they want to execute the code
                execute = input("\n🎯 Execute this animation? (y/n): ").strip().lower()
                
                if execute == 'y':
                    print("🎬 Executing Manim animation...")
                    
                    # Call the manim execution tool
                    result = await client.call_tool("manin_executable_code", {"manim_code": manim_code})
                    
                    if result:
                        print(f"✅ Result: {result[0].text if result else 'No result'}")
                    else:
                        print("❌ No result returned from tool")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue
    
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {str(e)}")
    
    finally:
        # Clean up
        if 'server_process' in locals():
            server_process.terminate()
            server_process.wait()
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
