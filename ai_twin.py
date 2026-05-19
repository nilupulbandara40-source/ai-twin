import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

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
    page_title="Sahan · AI Workspace",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

GROQ_MODEL = "llama-3.3-70b-versatile"


def _detect_language(text: str) -> str:
    """Detect if text is in Sinhala or English"""
    # Sinhala Unicode range: 0x0D80 to 0x0DFF
    sinhala_count = 0
    english_count = 0
    
    for char in text:
        code = ord(char)
        if 0x0D80 <= code <= 0x0DFF:
            sinhala_count += 1
        elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
            english_count += 1
    
    if sinhala_count > english_count:
        return "Sinhala"
    return "English"


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
    except Exception as e:
        st.error(f"Save error: {e}")
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


# ── Session State Init ──────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = "main_chat"

if "messages" not in st.session_state:
    st.session_state.messages = load_messages(st.session_state.session_id)

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

api_key = _groq_api_key()

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Workspace")
    st.markdown("**Sahan N. Bandara**")
    st.caption("University of Ruhuna · Computer Engineering")
    
    st.text_input("Your name", key="user_name",
                  placeholder="How should we address you?",
                  max_chars=64, label_visibility="collapsed")
    
    st.divider()
    st.metric("Messages", len(st.session_state.messages))
    st.divider()
    
    persona = st.radio("Persona", ["AiAssist", "DevBot", "Mentor"],
                       label_visibility="collapsed", key="persona")
    
    st.divider()
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Header ──────────────────────────────────────────────────────────────────
st.title("AI Workspace")
name = (st.session_state.get("user_name") or "").strip()
if name:
    st.caption(f"Hi {name} — Messages saved to Firebase ✅")
else:
    st.caption("Messages saved to Firebase ✅")

if not api_key:
    st.error("⚠️ GROQ_API_KEY missing")

if not firebase_ok:
    st.error("⚠️ Firebase not connected")

# ── Chat Display ────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.info("👋 Start chatting!")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg.get("role", "user")):
            st.markdown(msg.get("content", ""))

# ── AI Reply ────────────────────────────────────────────────────────────────
if (st.session_state.messages and 
    st.session_state.messages[-1].get("role") == "user" and 
    api_key and firebase_ok):
    
    # Detect user language from last message
    last_user_msg = st.session_state.messages[-1].get("content", "")
    detected_lang = _detect_language(last_user_msg)
    
    # Build system instruction with language
    base_instruction = PERSONA_INSTRUCTIONS.get(
        st.session_state.persona, PERSONA_INSTRUCTIONS["AiAssist"])
    
    if detected_lang == "Sinhala":
        system_instruction = base_instruction + " Reply ONLY in Sinhala language."
    else:
        system_instruction = base_instruction + " Reply ONLY in English language."
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
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
                
                # Add to session and save
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_text
                })
                save_message(st.session_state.session_id, "assistant", full_text)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")

# ── Input ───────────────────────────────────────────────────────────────────
prompt = st.chat_input("Message...")
if prompt:
    prompt = prompt.strip()
    if prompt:
        # Add to session and save
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        save_message(st.session_state.session_id, "user", prompt)
        st.rerun()
