🤖 AI Twin Premium
A Production-Ready AI Chatbot Application with Advanced Features
![GitHub](https://github.com/nilupulbandara40-source/ai-twin)
![Python](https://www.python.org/)
![Streamlit](https://streamlit.io/)
![License](LICENSE)
---
🎯 Overview
AI Twin Premium is a sophisticated conversational AI application that demonstrates full-stack development capabilities. Built with Python and Streamlit, it integrates the Groq API for advanced language processing, Firebase for data persistence, and includes production-ready features.
Perfect for:
💼 Companies evaluating developer capabilities
🎓 Portfolio demonstration
🚀 Learning full-stack development
🤖 Understanding LLM integration
---
✨ Features
Core Chat Features
💬 Multi-Persona Chat - Choose between AiAssist, DevBot, and Mentor personalities
🔄 Real-time Responses - Instant AI replies powered by Groq API
🌐 Bilingual Support - Automatic Sinhala/English detection
📱 Responsive Design - Works on desktop and mobile
🎨 Theme Toggle - Dark/Light mode support
Advanced Features
📊 Statistics Dashboard - Real-time message analytics
🔍 Smart Search - Find messages with highlighting
💾 Export Conversations - PDF, JSON, TXT formats
🗂️ Multiple Conversations - Organize chats by topic
⏰ Message Timestamps - Track conversation timeline
📋 Copy to Clipboard - Easy message sharing
Technical Features
🔐 Secure API Integration - Environment variable management
💾 Data Persistence - Firebase Firestore integration
⚡ Fast Performance - Optimized state management
📦 Clean Code - Well-structured, maintainable codebase
🛡️ Error Handling - Comprehensive exception management
---
🚀 Quick Start
Option 1: Desktop Application (Recommended)
```bash
# Download AI\_Twin\_Premium.bat from releases
# Double-click the file
# App starts automatically!
```
Option 2: Manual Setup
```bash
# Clone repository
git clone https://github.com/nilupulbandara40-source/ai-twin.git
cd ai-twin

# Install dependencies
pip install -r requirements.txt

# Set up secrets
# Create .streamlit/secrets.toml with your GROQ\_API\_KEY

# Run application
streamlit run ai\_twin.py
```
Option 3: Web Access
Visit: https://ai-twin-sahan.netlify.app
---
📋 Requirements
Python 3.11+
Streamlit 1.33+
Groq API Key (free from groq.com)
Modern web browser
---
🔧 Installation
1. Clone Repository
```bash
git clone https://github.com/nilupulbandara40-source/ai-twin.git
cd ai-twin
```
2. Install Dependencies
```bash
pip install -r requirements.txt
```
3. Configure Secrets
Create `.streamlit/secrets.toml`:
```toml
GROQ\_API\_KEY = "your\_api\_key\_here"
```
4. Run Application
```bash
streamlit run ai\_twin.py
```
App opens at: `http://localhost:8501`
---
💻 Tech Stack
Frontend
Streamlit - Python web framework
HTML/CSS - Custom styling
JavaScript - Interactive features
Backend
Python - Core language
Streamlit - Web framework
Requests - HTTP client
AI/ML
Groq API - LLM inference
llama-3.3-70b - Language model
Database
Firebase Firestore - Chat history storage
JSON - Data serialization
Deployment
Netlify - Landing page hosting
GitHub - Version control
Streamlit Cloud - Optional web deployment
---
📁 Project Structure
```
ai-twin/
├── ai\_twin.py                 # Main application
├── requirements.txt           # Dependencies
├── index.html                 # PWA landing page
├── manifest.json              # PWA configuration
├── service-worker.js          # Service worker
├── .streamlit/
│   ├── config.toml           # Streamlit config
│   └── secrets.toml          # API keys (not in git)
├── .gitignore                # Git ignore rules
├── README.md                 # This file
└── LICENSE                   # MIT License
```
---
🎯 Use Cases
For End Users
Chat with multiple AI personalities
Export conversations for documentation
Search previous conversations
Track chat statistics
For Companies
Evaluate full-stack development skills
Assess code quality and architecture
Review feature implementation
Test production-ready application
For Developers
Learn Streamlit development
Understand LLM API integration
See Firebase implementation
Study deployment strategies
---
📊 Dashboard Features
Statistics Tab
Total message count
User vs AI message ratio
Average message length
Persona usage distribution
Search Tab
Real-time message search
Highlighted results
Quick copy functionality
Export Tab
PDF Export - Professional formatted document
JSON Export - Structured data format
TXT Export - Plain text format
---
🔐 Security
✅ API keys stored in environment variables
✅ No credentials in version control
✅ HTTPS for all connections
✅ Input validation implemented
✅ Error handling without exposing internals
---
📈 Performance
⚡ Fast response times (< 2 seconds typical)
💾 Efficient state management
🔄 Optimized API calls
📱 Mobile-responsive design
---
🤝 Contributing
Contributions are welcome! Please:
Fork the repository
Create a feature branch
Commit changes
Push to branch
Create Pull Request
---
📝 License
MIT License - See LICENSE file for details
---
👨‍💻 Author
Sahan N Bandara
🎓 University of Ruhuna, Computer Engineering
💼 Full-Stack Developer
🚀 AI/ML Enthusiast
---
🔗 Links
🌐 Live Demo: https://ai-twin-sahan.netlify.app
📦 GitHub: https://github.com/nilupulbandara40-source/ai-twin
💬 Groq API: https://groq.com
📚 Streamlit Docs: https://docs.streamlit.io
---
⭐ Show Your Support
If you find this project useful, please:
⭐ Star the repository
🍴 Fork for your own use
💬 Share feedback
📢 Recommend to others
---
📞 Contact
📧 Email: nilupulbandara40@gmail.com
💼 LinkedIn: [Your LinkedIn Profile]
🐙 GitHub: https://github.com/nilupulbandara40-source
---
🙏 Acknowledgments
Groq for excellent API
Streamlit for powerful framework
Firebase for robust database
Community for inspiration
---
Built with ❤️ for learning and growth
Last Updated: May 2026
Version: 3.0 - Production Ready
