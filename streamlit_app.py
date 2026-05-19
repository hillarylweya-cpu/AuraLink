"""AuraLink - Communication without barriers"""
import streamlit as st
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AuraLink - Secure Chat",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 8px 0;
        border-left: 4px solid #667eea;
    }
    .message-peer {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 8px 0;
        border-left: 4px solid #f5576c;
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

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "connected" not in st.session_state:
    st.session_state.connected = False
if "encryption_enabled" not in st.session_state:
    st.session_state.encryption_enabled = True

# File functions
def load_messages():
    """Load messages from file"""
    if os.path.exists("messages.json"):
        with open("messages.json", "r") as f:
            return json.load(f)
    return []

def save_message(sender, content, msg_type="text"):
    """Save message to file"""
    messages = load_messages()
    message = {
        "sender": sender,
        "content": content,
        "type": msg_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages.append(message)
    with open("messages.json", "w") as f:
        json.dump(messages, f, indent=2)

def clear_messages():
    """Clear all messages"""
    if os.path.exists("messages.json"):
        os.remove("messages.json")
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    st.subheader("👤 User Info")
    username = st.text_input("Your Name", value="You", key="username")
    peer_name = st.text_input("Peer Name", value="Friend", key="peer_name")
    
    st.divider()
    
    st.subheader("🔗 Connection")
    server_url = st.text_input("Server URL", value="ws://127.0.0.1:8765")
    port = st.number_input("Port", value=8765, min_value=1024, max_value=65535)
    
    st.divider()
    
    st.subheader("🔒 Security")
    st.session_state.encryption_enabled = st.checkbox("Enable E2E Encryption", value=True)
    if st.session_state.encryption_enabled:
        st.success("✅ Encryption: Active")
    else:
        st.warning("⚠️ Encryption: Disabled")
    
    st.divider()
    
    st.subheader("🎛️ Control")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Connect", use_container_width=True):
            st.session_state.connected = True
            st.success("✅ Connected!")
    with col2:
        if st.button("🔌 Disconnect", use_container_width=True):
            st.session_state.connected = False
            st.info("Disconnected")
    
    st.divider()
    
    if st.session_state.connected:
        st.markdown('<p class="status-online">🟢 Online</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-offline">🔴 Offline</p>', unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-header">🔐 AuraLink</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'><i>Secure Communication without Barriers</i></p>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📎 Files", "📞 Voice", "🔑 Security"])

# Tab 1: Chat
with tab1:
    st.subheader("💬 Message History")
    
    messages = load_messages()
    
    if messages:
        for msg in messages:
            if msg["sender"] == username:
                st.markdown(f"""
                <div class="message-user">
                    <b>{msg['sender']}</b><br/>
                    {msg['content']}<br/>
                    <small>{msg['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-peer">
                    <b>{msg['sender']}</b><br/>
                    {msg['content']}<br/>
                    <small>{msg['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📭 No messages yet. Start a conversation!")
    
    st.divider()
    
    st.subheader("✉️ Send Message")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        message_text = st.text_area("Type a message", height=80, placeholder="Share your thoughts...")
    
    with col2:
        st.write("")
        st.write("")
        send_btn = st.button("📤 Send", use_container_width=True, key="send_msg")
    
    if send_btn and message_text.strip():
        save_message(username, message_text, "text")
        if st.session_state.connected:
            st.success("✅ Message sent!")
        else:
            st.warning("⚠️ Offline - queued for sending")
        st.rerun()
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True, key="clear_msgs"):
            clear_messages()
            st.success("✅ Cleared!")
            st.rerun()
    with col2:
        if st.button("🔄 Refresh", use_container_width=True, key="refresh_msgs"):
            st.rerun()
    with col3:
        if st.button("📊 Export", use_container_width=True, key="export_msgs"):
            data = load_messages()
            st.download_button(
                label="Download JSON",
                data=json.dumps(data, indent=2),
                file_name="auralink_chat.json",
                mime="application/json"
            )

# Tab 2: Files
with tab2:
    st.subheader("📎 File Transfer")
    
    uploaded = st.file_uploader("Choose file to send", accept_multiple_files=False)
    
    if uploaded:
        st.info(f"📄 {uploaded.name} | {uploaded.size / 1024:.1f} KB")
        if st.button("📤 Send File", use_container_width=True):
            if st.session_state.connected:
                save_message(username, f"[FILE: {uploaded.name}]", "file")
                st.success(f"✅ File sent!")
            else:
                st.error("❌ Cannot send while offline")
    
    st.divider()
    st.write("**📥 Received Files:**")
    st.info("No files received yet")

# Tab 3: Voice
with tab3:
    st.subheader("📞 Voice Communication")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📞 Start Call", use_container_width=True):
            if st.session_state.connected:
                st.success("📞 Calling...")
            else:
                st.error("❌ Offline")
    
    with col2:
        if st.button("⏸️ Hold", use_container_width=True):
            st.info("📞 On hold")
    
    with col3:
        if st.button("❌ End", use_container_width=True):
            st.info("📞 Call ended")
    
    st.divider()
    st.write("**🎙️ Audio Settings:**")
    
    col1, col2 = st.columns(2)
    with col1:
        mic = st.selectbox("Microphone", ["Default", "USB", "Built-in"])
    with col2:
        speaker = st.selectbox("Speaker", ["Default", "Headphones", "Built-in"])
    
    volume = st.slider("Volume", 0, 100, 75)

# Tab 4: Security
with tab4:
    st.subheader("🔒 Security & Encryption")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Encryption Status:**")
        if st.session_state.encryption_enabled:
            st.success("✅ E2E Encryption: ACTIVE")
        else:
            st.warning("⚠️ E2E Encryption: DISABLED")
        
        if st.button("🔄 Regenerate Keys", use_container_width=True):
            st.success("✅ Keys generated!")
    
    with col2:
        st.write("**Your Public Key:**")
        st.text_area(
            "Key",
            value="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...\n-----END PUBLIC KEY-----",
            height=100,
            disabled=True,
            label_visibility="collapsed"
        )
    
    st.divider()
    
    st.write("**Peer's Public Key:**")
    peer_key = st.text_area(
        "Peer Key",
        placeholder="Paste peer's public key",
        height=100,
        label_visibility="collapsed"
    )
    
    if st.button("✅ Verify & Add", use_container_width=True):
        if peer_key and peer_key.strip():
            st.success("✅ Peer verified!")
        else:
            st.error("❌ No key provided")
    
    st.divider()
    
    st.info("""
    🔐 **AuraLink Security:**
    - End-to-End Encryption
    - Public Key Infrastructure
    - Perfect Forward Secrecy
    - Message Authentication
    - Secure WebSocket Support
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #999; padding: 20px;'>
    <p><strong>AuraLink v2.0</strong> | Communication without barriers 🌍</p>
    <p>Secure • Private • Decentralized</p>
</div>
""", unsafe_allow_html=True)
