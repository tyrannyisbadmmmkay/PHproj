# imports
import openai
import streamlit as st
import time
import os
import json
from dotenv import load_dotenv
load_dotenv()

# defining tools
def handle_function(run):
    tools_to_call = run.required_action.submit_tool_outputs.tool_calls
    tools_output_array = []
    for each_tool in tools_to_call:
        tool_call_id = each_tool.id
        function_name = each_tool.function.name
        function_arg = each_tool.function.arguments
        print("Tool ID:" + tool_call_id)
        print("Function to Call:" + function_name )
        print("Parameters to use:" + function_arg)


        # if (function_name == 'get_stock_price'):
            # arguments_str = each_tool.function.arguments
            # arguments_dict = json.loads(arguments_str)
            # symbol = arguments_dict['symbol']
            # st.sidebar.write('get stock price for ', symbol)

            # output = getStockPrice(symbol)
            # tools_output_array.append({"tool_call_id": tool_call_id, "output": output})

    # client.beta.threads.runs.submit_tool_outputs(
        # thread_id = st.session_state.thread_id,
        # run_id = run.id,
        # tool_outputs=tools_output_array
    # )

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

    # Display existing messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Chat input for the user
    if prompt := st.chat_input("How can I help you?"):
        # Add user message to the state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

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
            if run.status == "requires_action":
                handle_function(run)
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
            full_response = process_message_with_citations(message)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            with st.chat_message("assistant"):
                st.markdown(full_response, unsafe_allow_html=True)
                