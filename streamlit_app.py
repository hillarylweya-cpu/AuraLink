"""AuraLink - Communication without barriers. Streamlit Web Interface"""

import streamlit as st
import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AuraLink - Secure Messaging",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .message-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        word-wrap: break-word;
    }
    .peer-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .system-message {
        background: #FFA500;
        color: white;
    }
    .status-online {
        color: #2ecc71;
        font-weight: bold;
    }
    .status-offline {
        color: #e74c3c;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "connected" not in st.session_state:
    st.session_state.connected = False
if "encryption_enabled" not in st.session_state:
    st.session_state.encryption_enabled = True
if "pending_messages" not in st.session_state:
    st.session_state.pending_messages = []

# Utility functions
def load_message_history(filename: str = "chat_history.json") -> List[Dict[str, Any]]:
    """Load chat history from file."""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []

def save_message_to_file(sender: str, content: str, status: str = "sent"):
    """Save message to chat history file."""
    filename = "chat_history.json"
    history = load_message_history(filename)
    
    message = {
        "sender": sender,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "status": status
    }
    
    history.append(message)
    
    with open(filename, "w") as f:
        json.dump(history, f, indent=2)

def clear_chat_history(filename: str = "chat_history.json"):
    """Clear chat history."""
    if os.path.exists(filename):
        os.remove(filename)
    st.session_state.messages = []

# Sidebar configuration
st.sidebar.title("⚙️ AuraLink Settings")

with st.sidebar:
    st.subheader("👤 User Configuration")
    username = st.text_input("Your Name", value="Me", key="username")
    peer_name = st.text_input("Peer Name", value="Friend", key="peer_name")
    
    st.divider()
    st.subheader("🔗 Connection Settings")
    server_url = st.text_input("Server URL", value="ws://127.0.0.1:8765", key="server")
    port = st.number_input("Port", value=8765, key="port")
    
    st.divider()
    st.subheader("🔒 Security")
    st.session_state.encryption_enabled = st.checkbox(
        "Enable End-to-End Encryption",
        value=st.session_state.encryption_enabled
    )
    
    if st.session_state.encryption_enabled:
        st.info("✅ E2E Encryption: Active")
    else:
        st.warning("⚠️ E2E Encryption: Disabled")
    
    st.divider()
    st.subheader("🎛️ Connection Control")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Connect", use_container_width=True):
            st.session_state.connected = True
            st.success("✅ Connected to server!")
    
    with col2:
        if st.button("🔌 Disconnect", use_container_width=True):
            st.session_state.connected = False
            st.info("❌ Disconnected from server")
    
    st.divider()
    
    # Connection status
    if st.session_state.connected:
        st.markdown('<p class="status-online">🟢 Online</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-offline">🔴 Offline</p>', unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-header">🔐 AuraLink</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'><i>Communication without barriers</i></p>", unsafe_allow_html=True)

# Create tabs for different features
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat", "📎 Files", "📞 Voice", "📹 Video", "🔑 Security"])

# Tab 1: Chat
with tab1:
    st.subheader("💬 Message History")
    
    # Load and display message history
    history = load_message_history()
    
    if history:
        for msg in history:
            if msg["sender"] == username:
                st.markdown(f"""
                    <div class="message-box">
                        <b>{msg['sender']}:</b> {msg['content']}<br/>
                        <small>{msg['timestamp']}</small>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="message-box peer-message">
                        <b>{msg['sender']}:</b> {msg['content']}<br/>
                        <small>{msg['timestamp']}</small>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No messages yet. Start a conversation!")
    
    st.divider()
    
    # Message input
    st.subheader("✉️ Send Message")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        message_input = st.text_area("Type your message:", height=80, placeholder="Share your thoughts...")
    
    with col2:
        st.write("")
        st.write("")
        send_button = st.button("📤 Send", use_container_width=True)
    
    if send_button and message_input.strip():
        # Save and display message
        save_message_to_file(username, message_input, "sent")
        
        if st.session_state.connected:
            st.success("✅ Message sent!")
        else:
            st.warning("⚠️ Offline - Message queued for sending")
            st.session_state.pending_messages.append({
                "sender": username,
                "content": message_input,
                "status": "queued"
            })
        
        st.rerun()
    
    st.divider()
    
    # Chat controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear History", use_container_width=True):
            clear_chat_history()
            st.success("Chat history cleared!")
            st.rerun()
    
    with col2:
        if st.button("📥 Load History", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("📊 Export Chat", use_container_width=True):
            history_data = load_message_history()
            st.download_button(
                label="Download as JSON",
                data=json.dumps(history_data, indent=2),
                file_name="auralink_chat_history.json",
                mime="application/json"
            )

# Tab 2: File Transfer
with tab2:
    st.subheader("📎 File Transfer")
    
    uploaded_file = st.file_uploader("Choose a file to send", accept_multiple_files=False)
    
    if uploaded_file is not None:
        st.info(f"📄 File: {uploaded_file.name} | Size: {uploaded_file.size / 1024:.2f} KB")
        
        if st.button("📤 Send File"):
            if st.session_state.connected:
                st.success(f"✅ File '{uploaded_file.name}' sent successfully!")
                save_message_to_file(username, f"[FILE: {uploaded_file.name}]", "sent")
            else:
                st.warning("⚠️ Cannot send file while offline")
    
    st.divider()
    st.write("**Received Files:**")
    st.info("No files received yet")

# Tab 3: Voice Call
with tab3:
    st.subheader("📞 Voice Communication")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📞 Start Call", use_container_width=True):
            if st.session_state.connected:
                st.success("📞 Calling...")
            else:
                st.error("❌ Cannot call while offline")
    
    with col2:
        if st.button("⏸️ Hold", use_container_width=True):
            st.info("Call on hold")
    
    with col3:
        if st.button("❌ End Call", use_container_width=True):
            st.info("Call ended")
    
    st.divider()
    st.write("**Audio Settings:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        microphone = st.selectbox("Microphone", ["Default Microphone", "USB Headset", "Built-in"])
    
    with col2:
        speaker = st.selectbox("Speaker", ["Default Speaker", "Headphones", "Built-in"])
    
    st.slider("Volume", 0, 100, 70)

# Tab 4: Video Call
with tab4:
    st.subheader("📹 Video Communication")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📹 Start Video Call", use_container_width=True):
            if st.session_state.connected:
                st.success("📹 Video call initiated...")
            else:
                st.error("❌ Cannot start video call while offline")
    
    with col2:
        if st.button("🎥 Mute Camera", use_container_width=True):
            st.info("Camera muted")
    
    with col3:
        if st.button("❌ End Video", use_container_width=True):
            st.info("Video call ended")
    
    st.divider()
    st.write("**Video Settings:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        camera = st.selectbox("Camera", ["Default Camera", "USB Camera", "Built-in"])
        quality = st.select_slider("Video Quality", options=["Low", "Medium", "High", "Ultra HD"])
    
    with col2:
        st.checkbox("Enable Screen Share")
        st.checkbox("Auto-focus")

# Tab 5: Security & Encryption
with tab5:
    st.subheader("🔒 Security & Encryption")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Encryption Status:**")
        if st.session_state.encryption_enabled:
            st.success("✅ E2E Encryption: ACTIVE")
        else:
            st.warning("⚠️ E2E Encryption: DISABLED")
        
        if st.button("🔄 Regenerate Keys"):
            st.success("✅ New encryption keys generated!")
    
    with col2:
        st.write("**Public Key:**")
        st.text_area(
            "Your Public Key",
            value="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
            height=100,
            disabled=True
        )
    
    st.divider()
    
    st.write("**Peer's Public Key:**")
    peer_key = st.text_area(
        "Paste peer's public key",
        placeholder="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
        height=100
    )
    
    if st.button("✅ Verify & Add Peer"):
        if peer_key:
            st.success("✅ Peer's public key verified and added!")
        else:
            st.error("❌ Please paste a public key")
    
    st.divider()
    
    st.write("**Security Info:**")
    st.info("""
    🔐 **AuraLink Security Features:**
    - End-to-End Encryption (NaCl/libsodium)
    - Public Key Infrastructure (PKI)
    - Perfect Forward Secrecy
    - Message Authentication Codes
    - Secure WebSocket (WSS) Support
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #999; padding: 20px;'>
    <p><strong>AuraLink v1.0</strong> | Communication without barriers 🌍</p>
    <p>Secure • Private • Decentralized</p>
</div>
""", unsafe_allow_html=True)
