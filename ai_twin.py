import streamlit as st
import requests
import json
from datetime import datetime
from fpdf import FPDF

# ======================== PAGE CONFIG ========================
st.set_page_config(
    page_title="AI Twin Premium",
    page_icon="🤖",
    layout="wide"
)

# ======================== CONFIGURATION ========================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ======================== SESSION STATE ========================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "ආයුබෝවන්! මම AI Twin Premium. කොහොම උදවු කරන්නද? 🤖",
            "timestamp": datetime.now().isoformat(),
            "conversation_id": "default"
        }
    ]

if "conversations" not in st.session_state:
    st.session_state.conversations = {"default": "Main Conversation"}

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = "default"

if "theme_dark" not in st.session_state:
    st.session_state.theme_dark = True

# ======================== HEADER ========================
col1, col2, col3 = st.columns([2, 3, 1])

with col1:
    st.markdown("# 🤖 AI Twin Premium")
    st.markdown("*by Sahan N Bandara 👨‍💻*")

with col3:
    theme_btn = st.toggle(
        "🌙 Dark Mode" if st.session_state.theme_dark else "☀️ Light Mode",
        value=st.session_state.theme_dark
    )
    st.session_state.theme_dark = theme_btn

st.divider()

# ======================== MAIN TABS ========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chat",
    "📊 Statistics",
    "🔍 Search",
    "📥 Export",
    "⚙️ Settings"
])

# ======================== TAB 1: CHAT ========================
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("Personas")
        selected_persona = st.selectbox(
            "Choose AI Persona:",
            ["AiAssist", "DevBot", "Mentor"],
            key="persona_select"
        )
    
    with col1:
        st.subheader("Chat")
    
    st.divider()
    
    # Display Chat Messages
    current_messages = [
        m for m in st.session_state.messages
        if m.get("conversation_id") == st.session_state.current_conversation
    ]
    
    for message in current_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            st.caption(
                f"*{datetime.fromisoformat(message['timestamp']).strftime('%H:%M')}*"
            )
    
    # Input using st.chat_input (PROPER WAY!)
    user_input = st.chat_input(
        "Type message and press Enter...",
        key=f"chat_input_{st.session_state.current_conversation}"
    )
    
    # Handle message sending
    if user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat(),
            "conversation_id": st.session_state.current_conversation
        })
        
        # Get AI response
        try:
            with st.spinner("🤔 Thinking..."):
                recent_messages = [
                    {
                        "role": m["role"],
                        "content": m["content"]
                    }
                    for m in current_messages[-5:]
                ]
                
                response = requests.post(
                    GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {
                                "role": "system",
                                "content": f"""You are {selected_persona}.
                                {selected_persona} Profile:
                                - AiAssist: General helpful AI assistant
                                - DevBot: Software development expert
                                - Mentor: Educational mentor
                                
                                Respond in same language as user.
                                Keep responses concise."""
                            },
                            *recent_messages,
                            {
                                "role": "user",
                                "content": user_input
                            }
                        ],
                        "temperature": 0.6,
                        "max_tokens": 500
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    ai_message = response.json()["choices"][0]["message"]["content"]
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_message,
                        "timestamp": datetime.now().isoformat(),
                        "conversation_id": st.session_state.current_conversation,
                        "persona": selected_persona
                    })
                    st.rerun()
                else:
                    st.error(f"API Error: {response.status_code}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ======================== TAB 2: STATISTICS ========================
with tab2:
    st.subheader("📊 Chat Statistics")
    
    current_messages = [
        m for m in st.session_state.messages
        if m.get("conversation_id") == st.session_state.current_conversation
    ]
    
    total_messages = len(current_messages)
    user_messages = len([m for m in current_messages if m["role"] == "user"])
    ai_messages = total_messages - user_messages
    avg_length = sum(len(m["content"]) for m in current_messages) / max(total_messages, 1)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Messages", total_messages)
    with col2:
        st.metric("Your Messages", user_messages)
    with col3:
        st.metric("AI Responses", ai_messages)
    with col4:
        st.metric("Avg Length", f"{int(avg_length)} chars")
    
    st.divider()
    st.subheader("Persona Usage")
    
    personas_used = {}
    for message in current_messages:
        persona = message.get("persona", "Unknown")
        personas_used[persona] = personas_used.get(persona, 0) + 1
    
    if personas_used:
        st.bar_chart(personas_used)

# ======================== TAB 3: SEARCH ========================
with tab3:
    st.subheader("🔍 Search Conversations")
    
    search_term = st.text_input("Search messages:", placeholder="Enter search term...")
    
    if search_term:
        search_results = [
            m for m in st.session_state.messages
            if search_term.lower() in m["content"].lower()
            and m.get("conversation_id") == st.session_state.current_conversation
        ]
        
        if search_results:
            st.write(f"**Found {len(search_results)} results:**")
            st.divider()
            
            for result in search_results:
                with st.chat_message(result["role"]):
                    highlighted = result["content"].replace(
                        search_term,
                        f"🔍 **{search_term}**"
                    )
                    st.write(highlighted)
                    st.caption(
                        f"*{datetime.fromisoformat(result['timestamp']).strftime('%H:%M')}*"
                    )
        else:
            st.warning("No results found")
    else:
        st.info("Enter a search term")

# ======================== TAB 4: EXPORT ========================
with tab4:
    st.subheader("📥 Export Conversation")
    
    current_messages = [
        m for m in st.session_state.messages
        if m.get("conversation_id") == st.session_state.current_conversation
    ]
    
    col1, col2, col3 = st.columns(3)
    
    # JSON Export
    with col1:
        if st.button("📄 JSON", use_container_width=True):
            export_data = {
                "conversation": st.session_state.conversations[st.session_state.current_conversation],
                "messages": current_messages,
                "export_date": datetime.now().isoformat(),
                "total_messages": len(current_messages)
            }
            
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="💾 Download JSON",
                data=json_str,
                file_name=f"ai_twin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # TXT Export
    with col2:
        if st.button("📝 TXT", use_container_width=True):
            txt_content = "AI Twin Premium - Chat Export\n"
            txt_content += f"Conversation: {st.session_state.conversations[st.session_state.current_conversation]}\n"
            txt_content += f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            txt_content += "="*50 + "\n\n"
            
            for message in current_messages:
                timestamp = datetime.fromisoformat(message['timestamp']).strftime('%H:%M:%S')
                role = "You" if message["role"] == "user" else "AI"
                txt_content += f"[{timestamp}] {role}:\n{message['content']}\n\n"
            
            st.download_button(
                label="💾 Download TXT",
                data=txt_content,
                file_name=f"ai_twin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # PDF Export
    with col3:
        if st.button("📋 PDF", use_container_width=True):
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "AI Twin Premium - Chat Export", ln=True, align="C")
                
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 10, f"Conversation: {st.session_state.conversations[st.session_state.current_conversation]}", ln=True)
                pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
                pdf.ln(5)
                
                pdf.set_font("Arial", "", 9)
                
                for message in current_messages:
                    timestamp = datetime.fromisoformat(message['timestamp']).strftime('%H:%M')
                    role = "You" if message["role"] == "user" else "AI"
                    
                    pdf.set_font("Arial", "B", 9)
                    pdf.cell(0, 5, f"[{timestamp}] {role}:", ln=True)
                    
                    pdf.set_font("Arial", "", 9)
                    pdf.multi_cell(0, 4, message['content'])
                    pdf.ln(2)
                
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                
                st.download_button(
                    label="💾 Download PDF",
                    data=pdf_bytes,
                    file_name=f"ai_twin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF Error: {str(e)}")

# ======================== TAB 5: SETTINGS ========================
with tab5:
    st.subheader("⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Conversations")
        
        for conv_id, conv_name in st.session_state.conversations.items():
            col_a, col_b = st.columns([3, 1])
            
            with col_a:
                if st.button(conv_name, use_container_width=True, key=f"select_{conv_id}"):
                    st.session_state.current_conversation = conv_id
                    st.rerun()
            
            with col_b:
                if st.button("🗑️", key=f"delete_{conv_id}"):
                    if conv_id != "default":
                        del st.session_state.conversations[conv_id]
                        st.session_state.messages = [
                            m for m in st.session_state.messages
                            if m.get("conversation_id") != conv_id
                        ]
                        st.rerun()
        
        new_conv_name = st.text_input("New conversation name:")
        if st.button("➕ Create New", use_container_width=True):
            if new_conv_name:
                new_id = f"conv_{datetime.now().timestamp()}"
                st.session_state.conversations[new_id] = new_conv_name
                st.session_state.current_conversation = new_id
                st.rerun()
    
    with col2:
        st.subheader("About AI Twin")
        st.markdown("""
        **Version:** 3.0 ULTIMATE
        
        **Features:**
        ✨ Multi-persona chat
        📊 Statistics
        🔍 Search
        📥 Export
        🌙 Dark/Light theme
        🗂️ Multiple conversations
        ⌨️ Enter key WORKS!
        ✅ Input clears AUTOMATICALLY!
        🚀 PERFECT!
        
        **Tech:**
        • Python & Streamlit
        • Groq LLM API
        • FPDF2
        
        Built by: **Sahan N Bandara**
        """)

# ======================== FOOTER ========================
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    <p>AI Twin Premium © 2024 | Sahan N Bandara</p>
</div>
""", unsafe_allow_html=True)
