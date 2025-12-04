# app_ollama_simple.py
import streamlit as st
from langchain_community.llms import Ollama  # Use community version
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import time

st.set_page_config(
    page_title="Local AI Chat with Ollama",
    page_icon="💻",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .local-badge {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        display: inline-block;
        margin: 10px 0;
    }
    .message-box {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid;
    }
    .user-message {
        background-color: #e3f2fd;
        border-color: #2196f3;
    }
    .ai-message {
        background-color: #f1f8e9;
        border-color: #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <h1>💻 Local AI Chat</h1>
    <div class="local-badge">No API Key Required • 100% Local • Privacy First</div>
    <p>Powered by Ollama - Run AI models on your own computer</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.markdown("### 📦 Available Models")
    st.info("""
    First, install Ollama and download models:
    
    **Installation:**
    1. Download from: https://ollama.com/
    2. Install for your OS
    3. Open terminal and run:
    ```
    ollama pull llama2
    ollama pull mistral
    ollama pull codellama
    ```
    """)
    
    # Model selection
    available_models = [
        "llama2", 
        "mistral", 
        "codellama",
        "llama2:7b",
        "llama2:13b",
        "llama2:70b",
        "mixtral",
        "neural-chat"
    ]
    
    selected_model = st.selectbox(
        "Select Model",
        available_models,
        index=0,
        help="Make sure the model is downloaded in Ollama"
    )
    
    # Model parameters
    st.markdown("---")
    st.markdown("### 🎛️ Parameters")
    
    temperature = st.slider(
        "Temperature",
        0.0, 1.0, 0.7, 0.1,
        help="Creativity level"
    )
    
    num_predict = st.slider(
        "Max Tokens",
        100, 4000, 1000, 100,
        help="Maximum response length"
    )
    
    # Check if Ollama is running
    st.markdown("---")
    st.markdown("### 🔍 Connection Status")
    
    if st.button("Check Ollama Connection", key="check_conn"):
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                st.success("✅ Ollama is running!")
                st.json(response.json())
            else:
                st.warning("⚠️ Ollama responded with error")
        except:
            st.error("❌ Ollama not running or not installed")
            st.info("""
            To start Ollama:
            1. Open terminal
            2. Run: `ollama serve`
            3. Keep that terminal open
            4. In another terminal: `ollama pull llama2`
            """)
    
    # Clear chat button
    st.markdown("---")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.success("Chat cleared!")
        st.rerun()

# Main chat area
st.markdown("### 💬 Chat")

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="message-box user-message">
            <strong>You:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="message-box ai-message">
            <strong>AI ({message.get('model', 'Local')}):</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)

# Chat input
user_input = st.text_area(
    "Type your message:",
    height=100,
    placeholder="Ask me anything...",
    key="user_input"
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    send_button = st.button("🚀 Send Message", use_container_width=True, type="primary")

# Process message
if send_button and user_input:
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": time.strftime("%H:%M:%S")
    })
    
    # Show thinking indicator
    thinking_placeholder = st.empty()
    thinking_placeholder.info(f"🤖 {selected_model} is thinking...")
    
    try:
        # Method 1: Try using LangChain Community
        llm = Ollama(
            model=selected_model,
            temperature=temperature,
            num_predict=num_predict,
            base_url="http://localhost:11434"
        )
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Provide clear and accurate responses."),
            ("user", "{input}")
        ])
        
        # Create chain
        chain = prompt | llm | StrOutputParser()
        
        # Generate response
        response = chain.invoke({"input": user_input})
        
        # Add to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "model": selected_model,
            "timestamp": time.strftime("%H:%M:%S")
        })
        
        # Clear thinking indicator
        thinking_placeholder.empty()
        
        # Rerun to update UI
        st.rerun()
        
    except Exception as e:
        thinking_placeholder.empty()
        st.error(f"❌ LangChain error: {str(e)}")
        
        # Try Method 2: Direct Ollama API
        st.info("Trying direct Ollama API...")
        
        try:
            import requests
            import json
            
            # Prepare request
            payload = {
                "model": selected_model,
                "prompt": user_input,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": num_predict
                }
            }
            
            # Make request
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response,
                    "model": selected_model,
                    "timestamp": time.strftime("%H:%M:%S")
                })
                
                st.rerun()
            else:
                st.error(f"Ollama API error: {response.status_code}")
                
        except Exception as e2:
            st.error(f"Direct API also failed: {str(e2)}")
            st.info("""
            **Troubleshooting steps:**
            1. Make sure Ollama is installed
            2. Run: `ollama serve` in terminal
            3. Download model: `ollama pull llama2`
            4. Keep Ollama running in background
            """)

# Quick examples
st.markdown("---")
st.markdown("### 💡 Example Questions")

examples = [
    "Explain quantum computing simply",
    "Write a Python function for factorial",
    "What is machine learning?",
    "Tell me a short story"
]

cols = st.columns(4)
for idx, example in enumerate(examples):
    with cols[idx]:
        if st.button(example[:25] + "...", key=f"ex_{idx}", use_container_width=True):
            st.session_state.user_input = example
            st.rerun()

# Installation instructions
with st.expander("📋 Installation Guide"):
    st.markdown("""
    ### Step-by-Step Ollama Setup:
    
    **1. Install Ollama:**
    ```bash
    # Visit: https://ollama.com/
    # Download for your OS (Windows/Mac/Linux)
    ```
    
    **2. Run Ollama:**
    ```bash
    # Open terminal and run:
    ollama serve
    # Keep this running in background
    ```
    
    **3. Download Models (in new terminal):**
    ```bash
    # Popular models:
    ollama pull llama2
    ollama pull mistral
    ollama pull codellama
    ollama pull neural-chat
    ```
    
    **4. Verify Installation:**
    ```bash
    ollama list  # Should show downloaded models
    ```
    
    **5. Test in Python:**
    ```bash
    pip install langchain-community ollama
    ```
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>💻 <strong>100% Local • No Internet Required • Complete Privacy</strong></p>
    <p>Powered by Ollama • Models run on your computer</p>
</div>
""", unsafe_allow_html=True)
