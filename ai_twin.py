import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import base64

import streamlit as st
from groq import Groq
import firebase_admin
from firebase_admin import credentials, firestore

# ── Firebase Init ──────────────────────────────────────────────────────────
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        firebase_ok = True
    except Exception as e:
        st.error(f"Firebase error: {e}")
        firebase_ok = False
else:
    db = firestore.client()
    firebase_ok = True

st.set_page_config(
    page_title="AI Twin - Premium",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

GROQ_MODEL = "llama-3.3-70b-versatile"

# ── Theme CSS ──────────────────────────────────────────────────────────────
def get_css(theme_mode):
    if theme_mode == "Dark":
        return """
        <style>
        :root {
            --primary: #6C63FF;
            --secondary: #FF6B9D;
            --bg-main: #0f0f1e;
            --bg-secondary: #1a1a2e;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --border: #2a2a3e;
        }
        
        .main {
            background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
        }
        
        .stChatMessage {
            background: var(--bg-secondary);
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid var(--primary);
        }
        
        .user-message {
            background: linear-gradient(135deg, #6C63FF 0%, #FF6B9D 100%);
            border-left: 4px solid var(--secondary);
        }
        
        .chat-input {
            border-radius: 12px;
            border: 2px solid var(--border);
            background: var(--bg-secondary);
            color: var(--text-primary);
        }
        
        .stats-card {
            background: linear-gradient(135deg, #6C63FF20 0%, #FF6B9D20 100%);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
        }
        </style>
        """
    else:
        return """
        <style>
        :root {
            --primary: #6C63FF;
            --secondary: #FF6B9D;
            --bg-main: #ffffff;
            --bg-secondary: #f8f9fa;
            --text-primary: #1a1a1a;
            --text-secondary: #666666;
            --border: #e0e0e0;
        }
        
        .main {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        }
        
        .stChatMessage {
            background: var(--bg-secondary);
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid var(--primary);
        }
        
        .user-message {
            background: linear-gradient(135deg, #6C63FF 0%, #FF6B9D 100%);
            color: white;
            border-left: 4px solid var(--secondary);
        }
        
        .chat-input {
            border-radius: 12px;
            border: 2px solid var(--border);
            background: var(--bg-secondary);
            color: var(--text-primary);
        }
        
        .stats-card {
            background: linear-gradient(135deg, #6C63FF10 0%, #FF6B9D10 100%);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
        }
        </style>
        """

def _detect_language(text: str) -> str:
    """Detect if text is in Sinhala or English"""
    sinhala_count = 0
    english_count = 0
    
    for char in text:
        code = ord(char)
        if 0x0D80 <= code <= 0x0DFF:
            sinhala_count += 1
        elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
            english_count += 1
    
    return "Sinhala" if sinhala_count > english_count else "English"


PERSONA_INSTRUCTIONS: Dict[str, str] = {
    "AiAssist": "You are AiAssist, a helpful AI assistant.",
    "DevBot": "You are DevBot, a senior software engineer. Give code in markdown blocks.",
    "Mentor": "You are Mentor, a supportive teacher who explains simply.",
}


def _groq_api_key() -> Optional[str]:
    try:
        raw = st.secrets["GROQ_API_KEY"]
        if raw is not None:
            s = str(raw).strip()
            if s:
                return s
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "").strip() or None


# ── Firebase Functions ──────────────────────────────────────────────────────
def save_message(session_id: str, role: str, content: str) -> bool:
    if not firebase_ok:
        return False
    try:
        db.collection("chats").document(session_id)\
          .collection("messages").add({
            "role": role,
            "content": content,
            "timestamp": firestore.SERVER_TIMESTAMP,
        })
        return True
    except Exception:
        return False


def load_messages(session_id: str) -> List[dict]:
    if not firebase_ok:
        return []
    try:
        docs = db.collection("chats").document(session_id)\
                 .collection("messages")\
                 .order_by("timestamp").stream()
        return [{"role": d.get("role"), "content": d.get("content")}
                for d in docs]
    except Exception:
        return []


def get_sessions() -> List[str]:
    if not firebase_ok:
        return []
    try:
        return sorted([d.id for d in db.collection("chats").stream()],
                     reverse=True)
    except Exception:
        return []


def delete_session(session_id: str) -> bool:
    if not firebase_ok:
        return False
    try:
        messages = db.collection("chats").document(session_id)\
                     .collection("messages").stream()
        for msg in messages:
            msg.reference.delete()
        db.collection("chats").document(session_id).delete()
        return True
    except Exception:
        return False


def export_chat_txt(messages: List[dict]) -> str:
    """Export chat as text file"""
    text = f"AI Twin Chat Export\n"
    text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += "=" * 50 + "\n\n"
    
    for msg in messages:
        role = "You" if msg.get("role") == "user" else "AI Twin"
        text += f"{role}:\n{msg.get('content', '')}\n\n"
    
    return text


def export_chat_json(messages: List[dict], session_id: str) -> str:
    """Export chat as JSON"""
    export_data = {
        "session_id": session_id,
        "exported_at": datetime.now().isoformat(),
        "messages": messages
    }
    return json.dumps(export_data, indent=2)


# ── Session State ──────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = "main_chat"

if "messages" not in st.session_state:
    st.session_state.messages = load_messages(st.session_state.session_id)

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

api_key = _groq_api_key()

# ── Apply Theme ────────────────────────────────────────────────────────────
st.markdown(get_css(st.session_state.theme_mode), unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.markdown("## 🤖")

with col2:
    st.title("AI Twin Premium")
    st.caption("Advanced chatbot with Groq API & Firebase")

with col3:
    theme = st.selectbox("Theme", ["Dark", "Light"], 
                        key="theme_select",
                        label_visibility="collapsed")
    if theme != st.session_state.theme_mode:
        st.session_state.theme_mode = theme
        st.rerun()

st.divider()

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👤 Settings")
    st.text_input("Your name", key="user_name",
                  placeholder="Enter your name",
                  label_visibility="collapsed")
    
    st.divider()
    
    st.markdown("### 📊 Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", len(st.session_state.messages))
    with col2:
        st.metric("Conversations", len(get_sessions()))
    
    st.divider()
    
    st.markdown("### 🎭 Persona")
    persona = st.radio("Select", ["AiAssist", "DevBot", "Mentor"],
                      label_visibility="collapsed", key="persona")
    
    st.divider()
    
    st.markdown("### 💬 Conversations")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.session_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    sessions = get_sessions()
    if sessions:
        st.markdown("**Previous chats:**")
        for s in sessions[:5]:
            if st.button(s[-12:], use_container_width=True, key=f"load_{s}"):
                st.session_state.session_id = s
                st.session_state.messages = load_messages(s)
                st.rerun()
    
    st.divider()
    
    st.markdown("### 📥 Export")
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.messages:
            txt_data = export_chat_txt(st.session_state.messages)
            st.download_button(
                label="📄 TXT",
                data=txt_data,
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                use_container_width=True
            )
    with col2:
        if st.session_state.messages:
            json_data = export_chat_json(st.session_state.messages, 
                                        st.session_state.session_id)
            st.download_button(
                label="📋 JSON",
                data=json_data,
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                use_container_width=True
            )

# ── Main Content ────────────────────────────────────────────────────────────
# Search Function
search_col1, search_col2 = st.columns([4, 1])
with search_col1:
    st.session_state.search_query = st.text_input(
        "🔍 Search messages",
        placeholder="Type to search...",
        label_visibility="collapsed"
    )

# Display Messages
if not st.session_state.messages:
    st.info("👋 Start a conversation! Type a message below.")
else:
    for i, msg in enumerate(st.session_state.messages):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        # Filter by search
        if st.session_state.search_query:
            if st.session_state.search_query.lower() not in content.lower():
                continue
        
        with st.chat_message(role):
            st.markdown(content)
            if role == "user":
                col1, col2 = st.columns([4, 1])
                with col2:
                    if st.button("✏️", key=f"edit_{i}", help="Copy"):
                        st.write(content)

# ── AI Response ──────────────────────────────────────────────────────────────
if (st.session_state.messages and 
    st.session_state.messages[-1].get("role") == "user" and 
    api_key and firebase_ok):
    
    last_user_msg = st.session_state.messages[-1].get("content", "")
    detected_lang = _detect_language(last_user_msg)
    
    base_instruction = PERSONA_INSTRUCTIONS.get(
        st.session_state.persona, PERSONA_INSTRUCTIONS["AiAssist"])
    
    if detected_lang == "Sinhala":
        system_instruction = base_instruction + " Reply ONLY in Sinhala language."
    else:
        system_instruction = base_instruction + " Reply ONLY in English language."
    
    with st.chat_message("assistant"):
        with st.spinner("✨ Thinking..."):
            try:
                client = Groq(api_key=api_key)
                stream = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        *st.session_state.messages
                    ],
                    temperature=0.6,
                    stream=True,
                )
                
                placeholder = st.empty()
                full_text = ""
                for chunk in stream:
                    delta = getattr(chunk.choices[0].delta, "content", None) or ""
                    full_text += delta
                    placeholder.markdown(full_text + "▌")
                
                placeholder.markdown(full_text)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_text
                })
                save_message(st.session_state.session_id, "assistant", full_text)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")

# ── Chat Input ──────────────────────────────────────────────────────────────
st.divider()
prompt = st.chat_input("💬 Type your message...", key="chat_input")

if prompt:
    prompt = prompt.strip()
    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        save_message(st.session_state.session_id, "user", prompt)
        st.rerun()

# ── Footer ──────────────────────────────────────────────────────────────────
st.divider()
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.caption("🚀 Powered by Groq API")
with col2:
    st.caption("🔥 Firebase Firestore")
with col3:
    st.caption("✨ Streamlit")
