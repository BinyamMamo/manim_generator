#!/usr/bin/env python3
import asyncio
import json
import os
import sys
import tempfile
import subprocess
import shelve
import time
from pathlib import Path
from typing import List, Tuple, Dict
import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Please set GEMINI_API_KEY in .env file")
    sys.exit(1)

if gr.NO_RELOAD:
    genai.configure(api_key=GEMINI_API_KEY)

class ManimChatBot:
    def __init__(self):
        if not gr.NO_RELOAD:
            genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def generate_manim_code(self, prompt: str) -> str:
        system_prompt = """
        Generate Manim code for mathematical animations.
        Use Manim Community (import from manim import *)
        Create Scene class with construct method
        Use LaTeX with Tex() and MathTex()
        Return only complete Python code.
        """
        
        full_prompt = f"{system_prompt}\n\nRequest: {prompt}"
        
        try:
            response = self.model.generate_content(full_prompt)
            code = response.text.strip()
            
            if code.startswith("```python"):
                code = code[9:]
            if code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
                
            return code.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def execute_manim_code(self, code: str) -> Tuple[str, str]:
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            scene_name = "Scene"
            for line in code.split('\n'):
                if line.strip().startswith('class ') and '(Scene)' in line:
                    scene_name = line.split()[1].split('(')[0]
                    break

            result = subprocess.run([
                'manim', temp_file, scene_name, '-ql', '--media_dir', './media'
            ], capture_output=True, text=True, cwd=os.getcwd())

            os.unlink(temp_file)

            if result.returncode == 0:
                media_dir = Path('./media/videos')
                if media_dir.exists():
                    mp4_files = list(media_dir.rglob('*.mp4'))
                    if mp4_files:
                        latest_video = max(mp4_files, key=lambda p: p.stat().st_mtime)
                        return "Animation created", str(latest_video)
                
                return "Animation completed, video not found", ""
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return f"Execution failed: {error_msg}", ""

        except Exception as e:
            return f"Error: {str(e)}", ""

if gr.NO_RELOAD:
    chatbot = ManimChatBot()
else:
    chatbot = None

# Chat history storage
CHAT_HISTORY_DB = "chat_history.db"

def save_chat_session(session_id: str, messages: List[Dict]):
    with shelve.open(CHAT_HISTORY_DB) as db:
        db[session_id] = {
            'messages': messages,
            'timestamp': time.time()
        }

def load_chat_sessions():
    try:
        with shelve.open(CHAT_HISTORY_DB) as db:
            sessions = []
            for session_id, data in db.items():
                if data['messages']:
                    first_message = data['messages'][0]['content'][:50] + "..."
                    sessions.append((session_id, first_message, data['timestamp']))
            return sorted(sessions, key=lambda x: x[2], reverse=True)
    except:
        return []

def load_chat_session(session_id: str):
    try:
        with shelve.open(CHAT_HISTORY_DB) as db:
            return db.get(session_id, {}).get('messages', [])
    except:
        return []

current_session_id = str(int(time.time()))

def chat_with_manim(message: str, history: List[Dict]) -> Tuple[List[Dict], str]:
    global chatbot, current_session_id
    if chatbot is None:
        chatbot = ManimChatBot()
        
    if not message.strip():
        return history, ""
    
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": "Generating..."})
    
    code = chatbot.generate_manim_code(message)
    
    if code.startswith("Error"):
        history[-1]["content"] = f"Error: {code}"
        save_chat_session(current_session_id, history)
        return history, ""
    
    status, video_path = chatbot.execute_manim_code(code)
    
    if video_path:
        history[-1]["content"] = "Animation created"
    else:
        history[-1]["content"] = f"Error: {status}"
    
    save_chat_session(current_session_id, history)
    return history, video_path if video_path else ""

dark_theme = gr.themes.Base(
    primary_hue="slate",
    secondary_hue="zinc",
    neutral_hue="gray",
).set(
    body_background_fill="*neutral_950",
    body_text_color="*neutral_200",
    background_fill_primary="*neutral_900",
    background_fill_secondary="*neutral_800",
    border_color_primary="*neutral_700",
    color_accent_soft="*neutral_800"
)

with gr.Blocks(title="Manim Chat", theme=dark_theme, css="""
    .gradio-container {
        max-width: 1400px !important;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
    footer {
        visibility: hidden;
    }
    .template-prompts {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .template-btn {
        padding: 1rem;
        background: #374151;
        border: 1px solid #4b5563;
        border-radius: 8px;
        color: #e5e7eb;
        cursor: pointer;
        transition: all 0.2s;
    }
    .template-btn:hover {
        background: #4b5563;
        border-color: #6b7280;
    }
    textarea {
        background-color: #374151 !important;
        border-color: #4b5563 !important;
        color: #e5e7eb !important;
    }
    textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }
    .history-item {
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        background: #374151;
        border-radius: 6px;
        cursor: pointer;
        transition: background 0.2s;
    }
    .history-item:hover {
        background: #4b5563;
    }
""", js="""
function loadChatSession(sessionId) {
    // This will be handled by Gradio event system
    console.log('Loading session:', sessionId);
}
""") as demo:
    
    with gr.Sidebar(label="Chat History", open=True, width=300):
        gr.HTML("<h3 style='color: #e5e7eb; margin-bottom: 1rem;'>Chat History</h3>")
        history_list = gr.HTML("")
        new_chat_btn = gr.Button("New Chat", variant="secondary", size="sm")
    
    gr.HTML("<h1 style='text-align: center; margin-bottom: 1rem; color: #e5e7eb; font-weight: 300; font-size: 2.5rem;'>Manim Generator</h1>")
    gr.HTML("<p style='text-align: center; margin-bottom: 3rem; color: #9ca3af; font-size: 18px;'>Create mathematical animations from natural language</p>")
    
    with gr.Row():
        # Main content area
        with gr.Column(scale=2):
            # Template prompts (initially visible)
            with gr.Column() as template_section:
                gr.HTML("<h3 style='color: #e5e7eb; margin-bottom: 1rem; text-align: center;'>Try these examples:</h3>")
                with gr.Row(elem_classes="template-prompts"):
                    template1 = gr.Button("Create a circle that transforms into a square", elem_classes="template-btn")
                    template2 = gr.Button("Show the Pythagorean theorem with animation", elem_classes="template-btn")
                    template3 = gr.Button("Animate Euler's identity e^(iπ) + 1 = 0", elem_classes="template-btn")
                    template4 = gr.Button("Draw a sine wave morphing into a cosine wave", elem_classes="template-btn")
            
            # Chat interface (initially hidden)
            chatbot_ui = gr.Chatbot(
                type="messages",
                height=400,
                show_copy_button=False,
                visible=False
            )
            
            # Input field
            msg_input = gr.Textbox(
                placeholder="Describe your animation... (Enter to send, Shift+Enter for new line)",
                show_label=False,
                container=False,
                lines=2,
                max_lines=6,
                submit_btn=True
            )
        
        # Video column (initially hidden)
        with gr.Column(scale=1, visible=False) as video_column:
            video_output = gr.Video(
                show_label=False,
                height=400,
                autoplay=True
            )

    def handle_send(message, history):
        new_history, video = chat_with_manim(message, history)
        updated_history_html = update_history_list()
        return (
            new_history, 
            "", 
            video,
            gr.update(visible=True),  # Show chatbot
            gr.update(visible=True),  # Show video column
            gr.update(visible=False), # Hide template section
            updated_history_html
        )
    
    def handle_template_click(template_text):
        return template_text
    
    def start_new_chat():
        global current_session_id
        current_session_id = str(int(time.time()))
        updated_history_html = update_history_list()
        return (
            [], # Clear chatbot
            "", # Clear input
            None, # Clear video
            gr.update(visible=False), # Hide chatbot
            gr.update(visible=False), # Hide video column
            gr.update(visible=True),  # Show template section
            updated_history_html
        )
    
    def update_history_list():
        sessions = load_chat_sessions()
        if not sessions:
            return "<p style='color: #6b7280; text-align: center; padding: 1rem;'>No chat history</p>"
        
        html = ""
        for session_id, preview, timestamp in sessions[:10]:  # Show last 10 sessions
            html += f"""
            <div class='history-item'>
                <div style='color: #e5e7eb; font-weight: 500; font-size: 13px; margin-bottom: 4px;'>{preview}</div>
                <div style='color: #9ca3af; font-size: 11px;'>{time.strftime("%m/%d %H:%M", time.localtime(timestamp))}</div>
            </div>
            """
        return html
    
    # Event handlers
    msg_input.submit(
        handle_send,
        inputs=[msg_input, chatbot_ui],
        outputs=[chatbot_ui, msg_input, video_output, chatbot_ui, video_column, template_section, history_list]
    )
    
    # Template button handlers
    template1.click(handle_template_click, inputs=[template1], outputs=[msg_input])
    template2.click(handle_template_click, inputs=[template2], outputs=[msg_input])
    template3.click(handle_template_click, inputs=[template3], outputs=[msg_input])
    template4.click(handle_template_click, inputs=[template4], outputs=[msg_input])
    
    # New chat button
    new_chat_btn.click(
        start_new_chat,
        outputs=[chatbot_ui, msg_input, video_output, chatbot_ui, video_column, template_section, history_list]
    )
    
    # Load initial history
    demo.load(update_history_list, outputs=[history_list])

if __name__ == "__main__":
    print("🚀 Starting Manim Animation Generator...")
    print("🌐 Web interface: http://localhost:7860")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )