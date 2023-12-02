# imports
import openai
import streamlit as st
import time
import os
import json
from dotenv import load_dotenv
load_dotenv()

# call assistant ID
assistant_id = os.getenv('ASSISTANT_ID')

# initialize openai client
client = openai

# Initialize session state variables for file IDs and chat control
if "file_id_list" not in st.session_state:
    st.session_state.file_id_list = []

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Set up the Streamlit page with a title and icon
st.set_page_config(page_title="Patrick Henry", page_icon=":scroll:", layout="wide")
st.header(":scroll: Patrick Henry")

#Get the OPENAI API Key
openai_api_key_env = os.getenv('OPENAI_API_KEY')
openai_api_key = st.sidebar.text_input(
    'OpenAI API Key', placeholder='sk-', value=openai_api_key_env)
url = "https://platform.openai.com/account/api-keys"
st.sidebar.markdown("Get an Open AI Access Key [here](%s). " % url)
if openai_api_key:
    openai.api_key = openai_api_key
    
    # Button to start the chat session
if st.sidebar.button("Ask me about your Freedom 🗽"):
    st.session_state.start_chat = True
    # Create a thread once and store its ID in session state
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.write("thread id: ", thread.id)
    
 # Only show the chat interface if the chat has been started
if st.session_state.start_chat:
   # st.write(getStockPrice('AAPL'))
    if "messages" not in st.session_state:
        st.session_state.messages = []   
