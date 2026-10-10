import os
import time
import base64
import json
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Page Setup
st.set_page_config(
    page_title="AI Talking-Head Studio | D-ID",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Dark Studio Aesthetic
st.markdown("""
<style>
    /* Dark theme overrides */
    .stApp {
        background-color: #09090b;
        color: #f4f4f5;
    }
    
    /* Card Glassmorphism Containers */
    .studio-card {
        background-color: #121215;
        border: 1px solid #27272a;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    /* Custom Badges */
    .badge-active {
        background-color: rgba(16, 185, 129, 0.1);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .badge-pro {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(6, 182, 212, 0.2));
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    /* Subtext and headers */
    .studio-header {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #f4f4f5, #a1a1aa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .studio-subtext {
        color: #a1a1aa;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }

    /* Primary Gradient Button */
    .stButton > button {
        background: linear-gradient(90deg, #7c3aed, #4f46e5, #0891b2) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 25px -5px rgba(124, 58, 237, 0.5) !important;
    }

    /* Hide default Streamlit top padding & footer */
    header[data-testid="stHeader"] {
        background-color: transparent;
    }
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONSTANTS & DEFAULT AVATAR
# ---------------------------------------------------------

VOICE_OPTIONS = {
    "en-US-JennyNeural": "🇺🇸 Jenny - Natural American Female",
    "en-US-GuyNeural": "🇺🇸 Guy - Conversational American Male",
    "en-US-AriaNeural": "🇺🇸 Aria - Expressive American Female",
    "en-GB-SoniaNeural": "🇬🇧 Sonia - British Female",
    "en-GB-RyanNeural": "🇬🇧 Ryan - British Male",
}

VOICE_MAPPING = {
    "🇺🇸 Jenny - Natural American Female": "en-US-JennyNeural",
    "🇺🇸 Guy - Conversational American Male": "en-US-GuyNeural",
    "🇺🇸 Aria - Expressive American Female": "en-US-AriaNeural",
    "🇬🇧 Sonia - British Female": "en-GB-SoniaNeural",
    "🇬🇧 Ryan - British Male": "en-GB-RyanNeural",
    "en-US-JennyNeural": "en-US-JennyNeural",
    "en-US-GuyNeural": "en-US-GuyNeural",
    "en-US-AriaNeural": "en-US-AriaNeural",
    "en-GB-SoniaNeural": "en-GB-SoniaNeural",
    "en-GB-RyanNeural": "en-GB-RyanNeural",
}

def map_voice_id(input_voice: str) -> str:
    """Map UI voice option display name or key to exact Azure Voice ID."""
    if not input_voice:
        return "en-US-JennyNeural"
    if input_voice in VOICE_MAPPING:
        return VOICE_MAPPING[input_voice]
    
    val = str(input_voice).lower()
    if "guy" in val:
        return "en-US-GuyNeural"
    elif "aria" in val:
        return "en-US-AriaNeural"
    elif "sonia" in val:
        return "en-GB-SoniaNeural"
    elif "ryan" in val:
        return "en-GB-RyanNeural"
    elif "jenny" in val:
        return "en-US-JennyNeural"
        
    return "en-US-JennyNeural"

SAMPLE_SCRIPTS = {
    "Product Launch": "Welcome to the future of AI content creation. With our D-ID integration, you can transform plain script text into realistic talking avatars in seconds.",
    "Executive Intro": "Hello everyone! Thank you for joining today's briefing. I am thrilled to demonstrate how artificial intelligence is changing how we communicate.",
    "Educational Byte": "Did you know that videos with human presenters increase audience retention by over 40 percent? Start crafting interactive avatar clips right away.",
}

# ---------------------------------------------------------
# HELPER FUNCTIONS & D-ID API CLIENT
# ---------------------------------------------------------
def get_api_key() -> str:
    """Retrieve API key from environment variable or Streamlit secrets."""
    key = os.getenv("D_ID_API_KEY")
    if not key and "D_ID_API_KEY" in st.secrets:
        key = st.secrets["D_ID_API_KEY"]
    return key or ""

def get_auth_header(api_key: str) -> dict:
    """Construct Basic Auth header matching D-ID requirements."""
    encoded_key = base64.b64encode(api_key.encode("utf-8")).decode("utf-8")
    return {
        "Authorization": f"Basic {encoded_key}",
        "Content-Type": "application/json"
    }

def upload_image_to_did(api_key: str, image_bytes: bytes, mime_type: str) -> str:
    """Uploads a local image to D-ID and returns the temporary URL."""
    url = "https://api.d-id.com/images"
    headers = {
        "Authorization": f"Basic {base64.b64encode(api_key.encode('utf-8')).decode('utf-8')}"
    }
    
    ext = ".png" if "png" in mime_type.lower() else ".jpg"
    files = {"image": (f"avatar{ext}", image_bytes, mime_type)}
    
    response = requests.post(url, headers=headers, files=files, timeout=30)
    data = response.json()
    
    if not response.ok:
        err_msg = data.get("description") or data.get("message") or f"HTTP {response.status_code}: {response.reason}"
        raise Exception(f"D-ID Image Upload Error: {err_msg}")
        
    return data.get("url")

def create_talk(api_key: str, source_url: str, text: str, voice_id: str) -> str:
    """Initiate a talk generation request on D-ID production servers."""
    url = "https://api.d-id.com/talks"
    headers = get_auth_header(api_key)
    
    mapped_voice_id = map_voice_id(voice_id)
    
    payload = {
        "source_url": source_url,
        "script": {
            "type": "text",
            "input": text,
            "provider": {
                "type": "microsoft",
                "voice_id": mapped_voice_id
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    data = response.json()
    
    if not response.ok:
        err_msg = data.get("description") or data.get("message") or f"HTTP {response.status_code}: {response.reason}"
        raise Exception(f"D-ID API Error: {err_msg}")
        
    return data.get("id")

def poll_talk_status(api_key: str, talk_id: str) -> dict:
    """Poll talk status from D-ID API."""
    url = f"https://api.d-id.com/talks/{talk_id}"
    headers = get_auth_header(api_key)
    response = requests.get(url, headers=headers, timeout=15)
    return response.json()

# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "current_video" not in st.session_state:
    st.session_state.current_video = None

if "script_input" not in st.session_state:
    st.session_state.script_input = SAMPLE_SCRIPTS["Product Launch"]

# ---------------------------------------------------------
# SIDEBAR & SETTINGS
# ---------------------------------------------------------
api_key = get_api_key()

with st.sidebar:
    st.image("https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=500&q=80", width=80)
    st.markdown("### AI Studio Configuration")
    
    if api_key:
        st.markdown("""
        <div class="badge-active">
            <span style="width: 8px; height: 8px; background-color: #34d399; border-radius: 50%;"></span>
            API Key Authenticated
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("⚠️ `D_ID_API_KEY` is not set!")
        st.info("Add your D-ID API key to `.env` or Streamlit Secrets (`.streamlit/secrets.toml`).")
        user_key_input = st.text_input("Enter API Key for current session:", type="password")
        if user_key_input:
            api_key = user_key_input
            
    st.markdown("---")
    st.markdown("#### About D-ID Engine")
    st.markdown("""
    This Streamlit Web App synthesizes realistic AI presenter videos using:
    - **D-ID Talking-Head Neural API**
    - **Microsoft Azure Speech Synthesis**
    - **Streamlit Python & Requests**
    """)
    st.markdown("---")
    st.markdown("🚀 Ready for 1-click **GitHub** & **Streamlit Cloud** deployment.")

# ---------------------------------------------------------
# MAIN STUDIO HEADER
# ---------------------------------------------------------
col_head1, col_head2 = st.columns([3, 1])

with col_head1:
    st.markdown('<div class="studio-header">🎬 AI Talking-Head Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="studio-subtext">Generate photorealistic talking avatar videos in real-time powered by D-ID</div>', unsafe_allow_html=True)

with col_head2:
    st.markdown("""
    <div style="text-align: right; padding-top: 8px;">
        <span class="badge-pro">D-ID PRO ENGINE</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# STUDIO TWO-COLUMN LAYOUT
# ---------------------------------------------------------
left_col, right_col = st.columns([5, 6], gap="large")

# --- LEFT COLUMN: CONTROLS ---
with left_col:
    st.markdown("### 1. Select Presenter Avatar")
    
    # Custom Avatar Image Upload
    uploaded_file = st.file_uploader(
        "Upload Custom Frontal Face Image",
        type=["jpg", "jpeg", "png"],
        help="Upload a clean frontal face image (JPEG or PNG)."
    )

    # Dynamic Image Preview
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Presenter Avatar Preview", width=250)
    else:
        st.info("⚠️ Please upload a Frontal Face Image.")

    st.markdown("### 2. Voice & Script Settings")
    
    # Voice Dropdown
    selected_voice_key = st.selectbox(
        "Choose Neural Voice (Azure Speech):",
        options=list(VOICE_OPTIONS.keys()),
        format_func=lambda k: VOICE_OPTIONS[k]
    )

    # Sample Scripts Pills
    st.markdown("**Quick Inspiration Presets:**")
    sample_cols = st.columns(3)
    for idx, (title, sample_text) in enumerate(SAMPLE_SCRIPTS.items()):
        with sample_cols[idx]:
            if st.button(f"+ {title}", key=f"btn_sample_{idx}"):
                st.session_state.script_input = sample_text
                st.rerun()

    # Script Textarea
    script_text = st.text_area(
        "Presenter Speech Script:",
        value=st.session_state.script_input,
        height=140,
        max_chars=1000,
        placeholder="Enter the speech script for your presenter..."
    )
    st.session_state.script_input = script_text
    st.caption(f"Character count: {len(script_text)} / 1000")

    # Generate CTA Button
    generate_clicked = st.button("✨ Generate AI Talking Video")

# --- RIGHT COLUMN: LIVE MONITOR ---
with right_col:
    st.markdown("### 3. Live Studio Monitor")
    
    if generate_clicked:
        if not api_key:
            st.error("Please provide your `D_ID_API_KEY` in the sidebar or `.env` file.")
        elif not uploaded_file:
            st.warning("⚠️ Please upload a Custom Frontal Face Image before generating the video.")
        elif not script_text.strip():
            st.error("Please enter a speech script.")
        else:
            with st.spinner("Uploading image and dispatching talk request to D-ID..."):
                try:
                    # Upload image to D-ID
                    image_url = upload_image_to_did(api_key, uploaded_file.getvalue(), uploaded_file.type)
                    
                    # Create talk request
                    talk_id = create_talk(api_key, image_url, script_text, selected_voice_key)
                    st.info(f"Talk request created! Talk ID: `{talk_id}`")
                    
                    # Polling loop
                    status_placeholder = st.empty()
                    progress_bar = st.progress(0)
                    start_time = time.time()
                    timeout_seconds = 120
                    video_result_url = None

                    while time.time() - start_time < timeout_seconds:
                        elapsed = int(time.time() - start_time)
                        status_data = poll_talk_status(api_key, talk_id)
                        status = status_data.get("status")

                        if status == "done":
                            video_result_url = status_data.get("result_url")
                            progress_bar.progress(100)
                            status_placeholder.success("🎉 Video rendered successfully!")
                            break
                        elif status in ["error", "rejected"]:
                            err_info = status_data.get("error", "Unknown error from D-ID API.")
                            status_placeholder.error(f"Generation Failed: {err_info}")
                            break
                        else:
                            # Still processing ('started' or 'created')
                            pct = min(95, int((elapsed / 45.0) * 100))
                            progress_bar.progress(pct)
                            status_placeholder.warning(f"Rendering lip-sync video on neural cluster... ({elapsed}s)")
                            time.sleep(3)

                    if video_result_url:
                        st.session_state.current_video = video_result_url
                        # Convert uploaded image to base64 for history display
                        base64_avatar = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                        avatar_data_url = f"data:{uploaded_file.type};base64,{base64_avatar}"
                        
                        # Record history item
                        new_record = {
                            "id": f"rec_{int(time.time())}",
                            "talkId": talk_id,
                            "videoUrl": video_result_url,
                            "avatarUrl": avatar_data_url,
                            "scriptText": script_text,
                            "voiceName": VOICE_OPTIONS[selected_voice_key].split(" ")[1],
                            "createdAt": datetime.now().strftime("%b %d, %H:%M"),
                        }
                        st.session_state.history.insert(0, new_record)
                        st.rerun()

                except Exception as e:
                    st.error(f"Error initiating talk: {str(e)}")

    # Video Player Display
    if st.session_state.current_video:
        st.video(st.session_state.current_video)
        
        # Download & Direct Link Actions
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            st.markdown(f"[🔗 Open Direct Video Link]({st.session_state.current_video})")
        with col_act2:
            try:
                video_bytes = requests.get(st.session_state.current_video).content
                st.download_button(
                    label="📥 Download MP4",
                    data=video_bytes,
                    file_name=f"did-talking-avatar-{int(time.time())}.mp4",
                    mime="video/mp4"
                )
            except Exception:
                st.write("Click direct link to download.")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; border: 2px dashed #27272a; border-radius: 16px; background: #121215;">
            <p style="font-size: 2.5rem; margin-bottom: 8px;">📹</p>
            <h4 style="color: #e4e4e7; margin-bottom: 4px;">Your rendered video will appear here</h4>
            <p style="color: #71717a; font-size: 0.85rem;">Select your presenter, enter script text, and click Generate.</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# BOTTOM SECTION: GENERATION HISTORY
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### 📜 Saved Generation History")

if st.session_state.history:
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

    hist_cols = st.columns(3)
    for idx, record in enumerate(st.session_state.history):
        col_idx = idx % 3
        with hist_cols[col_idx]:
            st.markdown(f"""
            <div style="background: #121215; border: 1px solid #27272a; border-radius: 12px; padding: 12px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <img src="{record['avatarUrl']}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">
                    <div>
                        <div style="font-weight: 600; font-size: 0.85rem; color: #f4f4f5;">{record['voiceName']}</div>
                        <div style="font-size: 0.75rem; color: #71717a;">{record['createdAt']}</div>
                    </div>
                </div>
                <p style="font-style: italic; font-size: 0.8rem; color: #a1a1aa; margin-bottom: 8px;">"{record['scriptText'][:90]}..."</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"▶️ Replay Clip #{idx+1}", key=f"replay_{record['id']}"):
                st.session_state.current_video = record["videoUrl"]
                st.rerun()
else:
    st.info("No saved generations in this session yet.")
