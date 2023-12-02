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

# get the OPENAI API Key
openai_api_key_env = os.getenv('OPENAI_API_KEY')
openai_api_key = st.sidebar.text_input(
    'OpenAI API Key', placeholder='sk-', value=openai_api_key_env)
url = "https://platform.openai.com/account/api-keys"
st.sidebar.markdown("Get an Open AI Access Key [here](%s). " % url)
if openai_api_key:
    openai.api_key = openai_api_key
    
    # Function to handle the debate mode initiation
def handle_debate_mode(topic):
    tool_call_id = "unique_id_for_debate_mode"  # Generate or assign a unique ID
    function_name = 'debate_mode'

    # Print information for debugging or logging purposes
    print("Tool ID:" + tool_call_id)
    print("Function to Call:" + function_name)
    print("Debate Topic:" + topic)

    # Here, add the logic for debating on the topic
    # For demonstration, let's just create a sample output
    output = f"And what is your stance on: {topic}"
    # Submitting the tool outputs (adjust as per your application's requirements)
    # Example: client.beta.threads.runs.submit_tool_outputs(...)

    
    # button to start the chat session
# or continue the chat session
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if st.session_state.start_chat:
    button_label = "Declare"
else:
    button_label = "Ask me about your Freedom 🗽"

if st.sidebar.button(button_label):
    st.session_state.start_chat = True
    if not st.session_state.thread_id:
        # Create a thread once and store its ID in session state
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        st.write("thread id: ", thread.id)
    
# Only show the chat interface if the chat has been started
if st.session_state.start_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Chat input for the user
    prompt = st.chat_input("Shall we fight tyranny together?")
    if prompt is not None:
    # Add user message to the state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if the entered prompt is the keyword for triggering debate mode
    if prompt.strip().lower() == 'debate_mode':
        # Prompt user for debate topic
        topic = st.text_input("I stand ever-ready to engage in invigorating and\
            thought-provoking discourse. And what shall we focus on, dear compatriot?")
        if topic:
            output = f"And what is your stance on: {topic}"
            # Call the function to handle debate mode with the given topic
            handle_debate_mode(topic)

        # Add the user's message to the existing thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )
        
        # Create a run with additional instructions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions=
            "Debate the user about a topic they choose, winning is extremely important,\
            do not concede or give up, and do not break character"        
            )

        # Poll for the run to complete and retrieve the assistant's messages
        while run.status not in ["completed", "failed"]:
            st.sidebar.write(run.status)
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        st.sidebar.write(run.status)

        # Retrieve messages added by the assistant
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )                    

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            response = message
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response, unsafe_allow_html=True)
                