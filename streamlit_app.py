import streamlit as st
import os
import sys
import tempfile
import subprocess
import shelve
import time
from pathlib import Path
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

# Page config
st.set_page_config(
    page_title="Manim Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("Please set GEMINI_API_KEY in .env file")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

class ManimChatBot:
    def __init__(self):
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

    def execute_manim_code(self, code: str) -> tuple[str, str]:
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
                    first_message = data['messages'][0]['content'][:40] + "..."
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

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = ManimChatBot()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = str(int(time.time()))

if 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = True

# Custom CSS
st.markdown("""
<style>
    .stSidebar {
        background-color: #1e1e1e;
    }
    .welcome-header {
        font-size: 2.5rem;
        font-weight: 300;
        color: #e1e5e9;
        text-align: center;
        margin-bottom: 1rem;
    }
    .welcome-subtitle {
        font-size: 1.2rem;
        color: #9ca3af;
        text-align: center;
        margin-bottom: 2rem;
    }
    .example-card {
        background: #374151;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .example-card:hover {
        background: #4b5563;
    }
    /* Remove chat input border radius and add vertical padding */
    .stChatInput > div > div > div > div {
        border-radius: 0.5rem !important;
    }
    .st-emotion-cache-x1bvup {
        border-radius: 0.5rem !important;
        padding: 1.5rem 1rem;
        font-weight: lighter !important;
    }
    button.st-emotion-cache-vsnu81 {
      margin: auto;    
    }
    .stChatInput {
      padding: 20px 0px !important;
    }
    .st-emotion-cache-tsgsuq h3 {
      margin-bottom: 1rem;
    }
    /* Left align sidebar buttons */
    .stSidebar .stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
    }
    /* Single line for chat history */
    .stSidebar .stButton > button {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    /* Remove styling from chat history buttons specifically */
    .st-emotion-cache-41psij.el4r43z2 {
        background: transparent !important;
        border: none !important;
        padding: 0px !important;
        margin: 0px !important;
        box-shadow: none !important;
        gap: 0px !important;
        transition: all 0.2s ease !important;
    }
    .st-emotion-cache-41psij.el4r43z2:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
    }
    /* Reduce gap between chat history items */
    .stSidebar .stButton {
        margin-bottom: 2px !important;
    }
    /* Chat History title styling */
    .st-emotion-cache-1m3gj4w.e1fxfrsf0 > h4 {
        font-size: 1.2rem !important;
        font-weight: bold !important;
        margin-bottom: 1rem !important;
    }
    /* Reduce gap between chat elements */
    .stVerticalBlock.st-emotion-cache-8fjoqp.e1msl4mp2 {
        gap: 0.5rem !important;
    }
    /* Hide video controls */
    video::-webkit-media-controls {
        display: none !important;
    }
    video::-webkit-media-controls-enclosure {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    if st.button("✧˖°󠀠⠀New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_session_id = str(int(time.time()))
        st.session_state.show_welcome = True
        st.rerun()
    
    st.markdown("---")
    st.markdown("#### Chat History")
    
    # Load and display chat sessions
    sessions = load_chat_sessions()
    for session_id, preview, timestamp in sessions[:10]:
        # Remove the "..." and truncate to fit one line
        display_text = preview.replace("...", "")[:30]
        if st.button(
            display_text,
            key=f"session_{session_id}",
            use_container_width=True
        ):
            st.session_state.current_session_id = session_id
            st.session_state.messages = load_chat_session(session_id)
            st.session_state.show_welcome = False
            st.rerun()

# Main content area ✨
if st.session_state.show_welcome:
    # Welcome screen
    st.markdown('<h1 class="welcome-header">Welcome to Manim Generator! 🎬</h1>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-subtitle">Create mathematical animations from natural language descriptions</p>', unsafe_allow_html=True)
    
    st.markdown("### Try these examples:")
    
    col1, col2 = st.columns(2)
    
    examples = [
        "Create a circle that transforms into a square",
        "Show the Pythagorean theorem with animation", 
        "Animate Euler's identity e^(iπ) + 1 = 0",
        "Draw a sine wave morphing into a cosine wave"
    ]
    
    for i, example in enumerate(examples):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(example, key=f"example_{i}", use_container_width=True):
                st.session_state.messages = []
                st.session_state.show_welcome = False
                # Process the example immediately
                with st.spinner("Generating animation..."):
                    code = st.session_state.chatbot.generate_manim_code(example)
                    if not code.startswith("Error"):
                        status, video_path = st.session_state.chatbot.execute_manim_code(code)
                        st.session_state.messages.append({"role": "user", "content": example})
                        st.session_state.messages.append({"role": "assistant", "content": "Animation created", "video": video_path if video_path else None})
                        save_chat_session(st.session_state.current_session_id, st.session_state.messages)
                st.rerun()

    # Add chat input to welcome screen
    if prompt := st.chat_input("Describe your animation..."):
        st.session_state.messages = []
        st.session_state.show_welcome = False
        # Process the prompt immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("Generating animation..."):
            code = st.session_state.chatbot.generate_manim_code(prompt)
            if not code.startswith("Error"):
                status, video_path = st.session_state.chatbot.execute_manim_code(code)
                st.session_state.messages.append({"role": "assistant", "content": "Animation created", "video": video_path if video_path else None})
            else:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {code}"})
        
        save_chat_session(st.session_state.current_session_id, st.session_state.messages)
        st.rerun()

else:
    # Chat interface
    st.title("Manim Generator")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message.get("video"):
                st.video(message["video"], autoplay=True, loop=True, start_time=0)
    
    # Chat input
    if prompt := st.chat_input("Describe your animation..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Generating animation..."):
                code = st.session_state.chatbot.generate_manim_code(prompt)
                
                if code.startswith("Error"):
                    st.error(code)
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {code}"})
                else:
                    status, video_path = st.session_state.chatbot.execute_manim_code(code)
                    
                    if video_path:
                        st.success("Animation created successfully!")
                        st.video(video_path, autoplay=True, loop=True, start_time=0)
                        st.session_state.messages.append({"role": "assistant", "content": "Animation created", "video": video_path})
                    else:
                        st.error(f"Failed to create animation: {status}")
                        st.session_state.messages.append({"role": "assistant", "content": f"Error: {status}"})
        
        # Save chat session
        save_chat_session(st.session_state.current_session_id, st.session_state.messages)
        st.rerun()
