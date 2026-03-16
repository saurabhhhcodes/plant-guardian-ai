import streamlit as st
import sys
import io
import asyncio
import os
import locale
from pathlib import Path
from PIL import Image
import cv2
import numpy as np
import base64
from datetime import datetime
from dotenv import load_dotenv

# Add the current directory to the Python path FIRST
sys.path.append(str(Path(__file__).parent))

load_dotenv()
# Ensure UTF-8 encoding for all output (fixes emoji errors)
try:
    if sys.getdefaultencoding().lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # Try to set locale to UTF-8
    locale.setlocale(locale.LC_ALL, '')
    if locale.getpreferredencoding().lower() != 'utf-8':
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    # Set PYTHONIOENCODING for subprocesses
    os.environ['PYTHONIOENCODING'] = 'utf-8'
except Exception as e:
    st.warning(f"Could not set UTF-8 encoding: {e}")

# Import the plant agent
try:
    from plant_agent import PlantCareAgent
except ImportError as e:
    st.error(f"Failed to import PlantCareAgent: {e}")
    st.error("Please make sure all dependencies are installed and the file exists.")
    st.stop()

try:
    from auth import initialize_db, register_user, login_user
except ImportError as e:
    st.error(f"Failed to import auth functions: {e}")
    st.error("Please make sure auth.py exists and is in the same directory.")
    st.stop()

try:
    from packages import PACKAGES
except ImportError as e:
    st.error(f"Failed to import PACKAGES: {e}")
    st.error("Please make sure packages.py exists and is in the same directory.")
    st.stop()

def initialize_session_state():
    """Initialize session state variables."""
    if 'plant_agent' not in st.session_state:
        st.session_state.plant_agent = None
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'provider' not in st.session_state:
        st.session_state.provider = "gemini"
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm Flora, your PlantGuardian AI expert. How can I help you save your plants today?"}
        ]
    if 'gemini_search_count' not in st.session_state:
        st.session_state.gemini_search_count = 0
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'location' not in st.session_state:
        st.session_state.location = ""
    if 'is_farm' not in st.session_state:
        st.session_state.is_farm = False

try:
    from weather_service import WeatherService
except ImportError:
    WeatherService = None

try:
    from story_generator import StoryGenerator
except ImportError:
    StoryGenerator = None

def display_sidebar():
    """Display the sidebar with LLM provider selection and API key input."""
    with st.sidebar:
        st.title("🛡️ PlantGuardian AI")
        st.info("Your Context-Aware Plant Doctor")
        
        # Location input for weather context
        st.subheader("📍 Environmental Context")
        
        # Auto-fetch location if empty
        if not st.session_state.location and WeatherService:
            with st.spinner("Detecting your location..."):
                auto_loc = WeatherService.get_location_from_ip()
                if auto_loc:
                    st.session_state.location = auto_loc
                    st.success(f"Detected: {auto_loc}")
        
        location = st.text_input("City/Region", value=st.session_state.location)
        st.session_state.location = location
        
        st.session_state.is_farm = st.toggle("🚜 Farm Mode (AGRICULTURAL)", value=st.session_state.get('is_farm', False))

        api_key = os.getenv("GEMINI_API_KEY")
        st.session_state.api_key = api_key

        if not api_key:
            st.error("GEMINI_API_KEY is not set. Please contact support.")
            return

        if not st.session_state.agent_initialized:
            try:
                with st.spinner("Initializing PlantGuardian Agent..."):
                    st.session_state.plant_agent = PlantCareAgent(
                        api_key=api_key
                    )
                    st.session_state.agent_initialized = True
            except Exception as e:
                st.error(f"Error initializing Agent: {str(e)}")
                st.session_state.agent_initialized = False

        # Status indicators
        st.subheader("Status")
        if st.session_state.agent_initialized:
            st.success("✅ PlantGuardian is ready")
        else:
            st.error("❌ Agent not initialized")

        # App information
        st.subheader("About")
        st.info("""
        **PlantGuardian AI** is a next-gen agentic assistant:
        - 📸 **Vision**: Real-time health analysis.
        - 🌍 **Context**: Weather & Location aware.
        - ✍️ **Creative Story**: Generates recovery roadmaps.
        - 💬 **Live Chat**: Multimodal communication.
        """)
        if st.session_state.logged_in:
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.rerun()

def display_upload_section():
    """Display the image upload and analysis section."""
    st.header("📸 Multimodal Diagnosis")
    
    # File uploader for images
    uploaded_file = st.file_uploader(
        "Upload a photo of your plant",
        type=["jpg", "jpeg", "png"],
        key="file_uploader"
    )

    # Video uploader
    uploaded_video = st.file_uploader(
      "Or upload a video of your plant",
        type=["mp4", "mov", "avi"],
        key="video_uploader"
    )

    # Camera input
    camera_image = st.camera_input("Or take a photo live")

    image_to_use = None
    if camera_image is not None:
        image_to_use = camera_image
    elif uploaded_file is not None:
        image_to_use = uploaded_file

    # Preferred location
    location = st.session_state.get('location', 'Lucknow')

    # Analysis button
    analysis_disabled = not st.session_state.agent_initialized or image_to_use is None
    
    if st.button("🚀 Start Diagnosis", disabled=analysis_disabled):
        analyze_plant_image(image_to_use, location, st.session_state.is_farm)

def analyze_plant_image(image_input, location, is_farm=False):
    """Analyze the plant image with location, weather, and farm context."""
    with st.spinner(f"Fetching weather for {location}..."):
        weather_data = None
        if WeatherService:
            weather_data = WeatherService.get_weather(location)
        
    with st.spinner("PlantGuardian is analyzing your plant..."):
        try:
            # Convert image to base64
            image = Image.open(image_input)
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Show the image
            st.image(image, caption="Analyzed Plant Image", width="stretch")

            if st.session_state.agent_initialized and st.session_state.plant_agent:
                analysis = asyncio.run(st.session_state.plant_agent.analyze_image(img_str, location, weather_data, is_farm))
                display_analysis_results(analysis, weather_data, is_farm)
            else:
                st.error("PlantGuardian Agent is not initialized")
                
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")

def display_analysis_results(analysis, weather_data=None, is_farm=False):
    """Display the enhanced analysis results."""
    if analysis.get('status') == 'success':
        st.balloons()
        st.success("Diagnosis Complete! 🎉")
        
        # Plant Info
        st.subheader(f"🌿 {analysis.get('species', 'Plant identified')}")
        
        summary = analysis.get('summary', {})
        
        # Weather Context
        if weather_data:
            with st.expander("🌤️ Local Weather Context", expanded=True):
                col1, col2, col3 = st.columns(3)
                col1.metric("Temperature", f"{weather_data.get('temp_C')}°C")
                col2.metric("Humidity", f"{weather_data.get('humidity')}%")
                col3.metric("Condition", weather_data.get('weatherDesc'))
                st.write(f"**AI Insight:** {summary.get('weather_context')}")
                if is_farm:
                    st.warning("🚜 **Farm Insights Active**: Analyzing soil drainage and regional crop risks.")

        # Diagnosis Breakdown
        st.subheader("🩺 Diagnosis")
        st.info(summary.get('diagnosis'))

        # Metrics
        health = analysis.get('health_analysis', {})
        col1, col2, col3 = st.columns(3)
        col1.metric("Health Score", f"{health.get('healthy_percentage', 0):.1f}%")
        col2.metric("Yellowing", f"{health.get('yellow_percentage', 0):.1f}%")
        col3.metric("Browning", f"{health.get('brown_percentage', 0):.1f}%")

        # Recovery Story (Multimodal Storyteller)
        recovery = analysis.get('recovery_story', {})
        if recovery:
            st.divider()
            st.subheader("🗺️ Plant Recovery Roadmap (Infographic)")
            infographic = recovery.get('infographic', {})
            
            # CSS-styled infographic steps
            cols = st.columns(len(infographic.get('steps', [])))
            for i, step in enumerate(infographic.get('steps', [])):
                with cols[i]:
                    st.markdown(f"""
                    <div style="background: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; text-align: center;">
                        <h2 style="margin: 0;">{step.get('icon', '🌱')}</h2>
                        <h4 style="margin: 5px 0;">Day {step.get('day')}</h4>
                        <p style="font-size: 0.9em;">{step.get('action')}</p>
                    </div>
                    """, unsafe_allow_html=True)

    else:
        st.error(f"Analysis failed: {analysis.get('message', 'Unknown error')}")

def display_chat_interface():
    """Display the chat interface for plant care questions."""
    st.header("💬 Chat with Flora")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            try:
                # Always force UTF-8 for display
                content = message["content"]
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='replace')
                else:
                    content = str(content).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                st.markdown(content)
            except Exception as e:
                st.markdown(f"[Unicode error displaying message: {e}]")

    # Chat input
    chat_disabled = not st.session_state.agent_initialized
    if prompt := st.chat_input("Ask Flora about your plants...", disabled=chat_disabled):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    if st.session_state.agent_initialized and st.session_state.plant_agent:
                        response = asyncio.run(st.session_state.plant_agent.chat(
                            message=prompt,
                            chat_history=st.session_state.messages[:-1]
                        ))
                        # Always force UTF-8 for output
                        if isinstance(response, bytes):
                            response = response.decode('utf-8', errors='replace')
                        else:
                            response = str(response).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        st.error("PlantGuardian Agent is not initialized")
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def main():
    # Set page config
    st.set_page_config(
        page_title="🛡️ PlantGuardian AI",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    initialize_session_state()
    initialize_db()

    if not st.session_state.logged_in:
        display_login_page()
    else:
        # Display sidebar
        display_sidebar()
        
        # Main content
        st.title("🛡️ PlantGuardian AI")
        st.markdown("### 🌿 Next-Gen Multimodal Plant Health Assistant")
        
        st.info("🚀 Powered by Gemini 2.5 Flash - Context-Aware Diagnostics.")
        
        if st.session_state.get('is_guest'):
            st.warning("⚠️ Running in Guest Mode. Limited features might apply.")

        # Create tabs for different features
        tab1, tab2, tab3 = st.tabs(["📸 AI Diagnosis", "💬 Chat with Flora", "📦 Premium Plans"])
        
        with tab1:
            display_upload_section()
        
        with tab2:
            display_chat_interface()

        with tab3:
            display_packages()

def display_login_page():
    st.title("🛡️ PlantGuardian Login")
    
    choice = st.selectbox("Choose an action", ["Login", "Register"])
    
    username = st.text_input("Username")
    if choice == "Register":
        email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if choice == "Register":
        if st.button("Register"):
            if register_user(username, email, password):
                from email_agent import send_welcome_email
                send_welcome_email(email, username)
                st.success("Registration successful! Please login.")
            else:
                st.error("Username or email already exists.")
    else:
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password.")
                
    st.divider()
    if st.button("🚀 Bypass to Guest App"):
        st.session_state.logged_in = True
        st.session_state.username = "Guest"
        st.session_state.is_guest = True
        st.rerun()

def display_packages():
    st.header("Premium Subscription Packages")
    
    for package in PACKAGES:
        with st.container():
            st.subheader(package["name"])
            st.metric("Price", package["price"])
            for feature in package["features"]:
                st.markdown(f"- {feature}")
            st.link_button("Subscribe", package["payment_link"])


if __name__ == "__main__":
    main()
