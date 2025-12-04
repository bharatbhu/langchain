# app_gemini_flash.py
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Google AI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("""
    ❌ GOOGLE_API_KEY not found in .env file!
    
    Steps to fix:
    1. Create a file named '.env' in your project folder
    2. Add this line: GOOGLE_API_KEY=your_actual_key_here
    3. Get key from: https://aistudio.google.com/app/apikey
    """)
    st.stop()

try:
    genai.configure(api_key=api_key)
    st.success("✅ API configured successfully!")
except Exception as e:
    st.error(f"❌ API configuration failed: {str(e)}")
    st.stop()

# Streamlit UI Configuration
st.set_page_config(
    page_title="Gemini 2.5 Flash AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Model badge */
    .model-badge {
        display: inline-block;
        background: #FF6B6B;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    /* Chat bubbles */
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .ai-bubble {
        background: #f0f2f6;
        color: #333;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        max-width: 80%;
        margin-right: auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #4CAF50;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    /* Stats cards */
    .stats-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #667eea;
    }
    
    /* Input area */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        font-size: 16px;
        padding: 15px;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Header with model info
st.markdown("""
<div class="main-header">
    <h1>⚡ Gemini 2.5 Flash AI Assistant</h1>
    <div class="model-badge">Latest Model • Ultra Fast</div>
    <p>Powered by Google's fastest Gemini model</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Model Settings")
    
    # Model selection
    st.markdown("### 🤖 Selected Model")
    st.info(f"**Gemini 2.5 Flash**\n\n*Google's fastest model*\n*Best for real-time chat*")
    
    # Model parameters
    st.markdown("---")
    st.markdown("### 🎛️ Parameters")
    
    temperature = st.slider(
        "**Creativity**",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Lower = more factual, Higher = more creative"
    )
    
    max_tokens = st.slider(
        "**Response Length**",
        min_value=100,
        max_value=4000,
        value=1500,
        step=100,
        help="Maximum tokens in response"
    )
    
    top_p = st.slider(
        "**Top-P**",
        min_value=0.0,
        max_value=1.0,
        value=0.95,
        step=0.05,
        help="Nucleus sampling parameter"
    )
    
    top_k = st.slider(
        "**Top-K**",
        min_value=1,
        max_value=100,
        value=40,
        step=1,
        help="Number of highest probability tokens"
    )
    
    # Safety settings
    st.markdown("---")
    st.markdown("### 🔒 Safety Settings")
    
    safety_settings = {
        "HARASSMENT": st.selectbox(
            "Harassment",
            ["BLOCK_NONE", "BLOCK_LOW_AND_ABOVE", "BLOCK_MEDIUM_AND_ABOVE"],
            index=1
        ),
        "HATE_SPEECH": st.selectbox(
            "Hate Speech",
            ["BLOCK_NONE", "BLOCK_LOW_AND_ABOVE", "BLOCK_MEDIUM_AND_ABOVE"],
            index=1
        ),
        "SEXUAL": st.selectbox(
            "Sexual Content",
            ["BLOCK_NONE", "BLOCK_LOW_AND_ABOVE", "BLOCK_MEDIUM_AND_ABOVE"],
            index=2
        ),
        "DANGEROUS": st.selectbox(
            "Dangerous Content",
            ["BLOCK_NONE", "BLOCK_LOW_AND_ABOVE", "BLOCK_MEDIUM_AND_ABOVE"],
            index=1
        )
    }
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.total_tokens = 0
    
    # Clear chat button
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.success("Chat history cleared!")
        st.rerun()
    
    # Stats
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    st.metric("Total Messages", len(st.session_state.messages))
    st.metric("Estimated Tokens", st.session_state.total_tokens)

# Main chat area - Two columns layout
col1, col2 = st.columns([2, 1])

with col1:
    # Display chat history
    st.markdown("### 💬 Conversation")
    
    if not st.session_state.messages:
        st.info("👋 Start a conversation by typing below!")
    else:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-bubble"><strong>You:</strong> {message["content"]}</div>', 
                          unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-bubble"><strong>AI:</strong> {message["content"]}</div>', 
                          unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    user_input = st.text_area(
        "**Type your message:**",
        height=120,
        placeholder="Ask me anything... (Shift+Enter for new line, Enter to send)",
        key="user_input"
    )
    
    # Send button
    send_col1, send_col2, send_col3 = st.columns([1, 2, 1])
    with send_col2:
        send_button = st.button("🚀 Send Message", use_container_width=True, type="primary")

with col2:
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    quick_questions = [
        "Explain quantum computing simply",
        "Write Python code for Fibonacci",
        "Best practices for mental health",
        "Summarize the benefits of AI",
        "How to learn programming fast",
        "Tell me a motivational story"
    ]
    
    for i, question in enumerate(quick_questions):
        if st.button(f"{question[:30]}...", key=f"quick_{i}", use_container_width=True):
            st.session_state.user_input = question
            st.rerun()
    
    # Model info
    st.markdown("---")
    st.markdown("### ℹ️ Model Info")
    
    with st.container():
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.markdown("**Gemini 2.5 Flash**")
        st.markdown("⚡ **Ultra Fast**")
        st.markdown("🎯 **Latest Version**")
        st.markdown("💬 **Optimized for Chat**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tips
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.info("""
    • Be specific with questions
    • Use Shift+Enter for multi-line
    • Adjust temperature for creativity
    • Try different safety settings
    """)

# Process message when send button is clicked
if send_button and user_input:
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Update token estimate
    st.session_state.total_tokens += len(user_input.split())
    
    # Show thinking indicator
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div class="model-badge">⚡ Processing...</div>
        <p>Gemini 2.5 Flash is thinking</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Initialize model with correct name
        model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",  # Use the exact model name
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": top_p,
                "top_k": top_k,
            }
        )
        
        # Generate response
        response = model.generate_content(user_input)
        
        # Extract response text safely
        if response and hasattr(response, '_result'):
            if response._result.candidates:
                candidate = response._result.candidates[0]
                
                # Check if response was blocked
                if candidate.finish_reason == 1:  # STOP - normal completion
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        response_text = candidate.content.parts[0].text
                        
                        # Add to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "model": "Gemini 2.5 Flash"
                        })
                        
                        # Update token estimate
                        st.session_state.total_tokens += len(response_text.split())
                        
                    else:
                        response_text = "⚠️ No text content in response"
                elif candidate.finish_reason == 2:  # SAFETY - blocked
                    response_text = "🚫 Response blocked for safety reasons. Please rephrase your question."
                else:
                    response_text = f"⚠️ Unknown response (finish_reason: {candidate.finish_reason})"
            else:
                response_text = "⚠️ No response generated by the model"
        else:
            # Try direct access as fallback
            try:
                response_text = response.text
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.session_state.total_tokens += len(response_text.split())
            except:
                response_text = "❌ Could not extract response"
        
        # Clear thinking indicator
        thinking_placeholder.empty()
        
        # Rerun to update UI
        st.rerun()
        
    except Exception as e:
        thinking_placeholder.empty()
        st.error(f"❌ Error: {str(e)}")
        
        # Try alternative approach
        try:
            st.info("Trying alternative approach...")
            # Try without 'models/' prefix
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(user_input)
            
            if hasattr(response, 'text'):
                response_text = response.text
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
        except Exception as e2:
            st.error(f"Alternative also failed: {str(e2)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>⚡ <strong>Powered by Gemini 2.5 Flash</strong> • Google's Fastest AI Model</p>
    <p>🚀 Real-time responses • 🔒 Secure • 💬 Conversational</p>
    <p style="font-size: 12px; margin-top: 20px;">Made with ❤️ using Streamlit & Google AI</p>
</div>
""", unsafe_allow_html=True)

# Auto-scroll to latest message
st.markdown("""
<script>
    // Auto-scroll to bottom
    window.addEventListener('load', function() {
        window.scrollTo(0, document.body.scrollHeight);
    });
    
    // Auto-scroll when new messages are added
    const observer = new MutationObserver(function() {
        window.scrollTo(0, document.body.scrollHeight);
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)