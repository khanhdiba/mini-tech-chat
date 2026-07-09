import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- 1. Page Configuration ---
st.set_page_config(page_title="OptiBot Support", layout="centered")
st.title("OptiBot Help Center")
st.caption("Ask me anything about OptiSigns. I'll search our documentation for the answer.")

# --- 2. Setup API Client ---
load_dotenv()
try:
    client = genai.Client()
except Exception as e:
    st.error(f"Failed to initialize GenAI Client. Did you set GEMINI_API_KEY? Error: {e}")
    st.stop()

SYSTEM_PROMPT = """
You are OptiBot, the customer-support bot for OptiSigns.com.
Tone: helpful, factual, concise.
Only answer using the uploaded docs.
Max 5 bullet points; else link to the doc.
Cite up to 3 "Article URL:" lines per reply.
"""

# --- 3. Cache the Knowledge Base ---
# This prevents the app from hitting the API to list files every time you type a message
@st.cache_resource(show_spinner=False)
def load_knowledge_base():
    try:
        active_files = list(client.files.list())
        return active_files
    except Exception as e:
        st.error(f"Error fetching files: {e}")
        return []

with st.spinner("Syncing with OptiSigns Knowledge Base..."):
    active_files = load_knowledge_base()

if not active_files:
    st.warning("No articles found in the Gemini storage. Please run your ingestion script first.")

# --- 4. Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! I'm OptiBot. How can I help you today?"}
    ]

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. Chat Input and Generation ---
if prompt := st.chat_input("E.g., 'How do I add a YouTube video?'"):
    
    # Append user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and append AI response
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            try:
                # Combine all loaded files with the user's specific prompt
                prompt_contents = active_files + [prompt]
                
                # FIXED TYPO: gemini-1.5-flash
                response = client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=prompt_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.0
                    )
                )
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"An error occurred during generation: {e}")