import os
import sys
import re
import uuid
import streamlit as st
from io import StringIO

from modules.history import ChatHistory
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
from modules.tools import ImageCaptionTool, ObjectDetectionTool

from langchain.agents import initialize_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory


#To be able to update the changes made to modules in localhost (press r)
def reload_module(module_name):
    import importlib
    import sys
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    return sys.modules[module_name]

history_module = reload_module('modules.history')
layout_module = reload_module('modules.layout')
utils_module = reload_module('modules.utils')
sidebar_module = reload_module('modules.sidebar')
tools_module = reload_module('modules.tools')

ChatHistory = history_module.ChatHistory
Layout = layout_module.Layout
Utilities = utils_module.Utilities
Sidebar = sidebar_module.Sidebar

st.set_page_config(layout="wide", page_icon="💬", page_title="KB AI - Documents")

# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()

layout.show_header("PNG, JPEG")

user_api_key = utils.load_api_key()

if not user_api_key:
    layout.show_api_key_missing()
else:
    os.environ["OPENAI_API_KEY"] = user_api_key

    uploaded_files = utils.handle_upload(["jpeg", "jpg", "png"])

    if uploaded_files:

        uploaded_file = uploaded_files[0]
        # generate a random filename
        filename = str(uuid.uuid4())

        # write the file
        with open(filename, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        image_path = filename

        # Configure the sidebar
        sidebar.show_options()
        sidebar.about()

        # Initialize chat history
        history = ChatHistory()

        try:
            llm = ChatOpenAI(model_name=st.session_state["model"],
                             temperature=st.session_state["temperature"],
                             streaming=True, verbose=True)
            tools = [ImageCaptionTool(), ObjectDetectionTool()]

            conversational_memory = ConversationBufferWindowMemory(memory_key='chat_history', k=5, return_messages=True)

            chatbot = initialize_agent(agent="chat-conversational-react-description",
                                       tools=tools,
                                       llm=llm,
                                       max_iterations=5,
                                       verbose=True,
                                       memory=conversational_memory,
                                       early_stopping_method='generate')
            st.session_state["chatbot"] = chatbot

            # Create containers for chat responses and user prompts
            response_container, prompt_container = st.container(), st.container()

            with prompt_container:
                # Display the prompt form
                is_ready, user_input = layout.prompt_form()

                # Initialize the chat history
                history.initialize(" ")

                st_callback = StreamlitCallbackHandler(response_container)

                # Reset the chat history if button clicked
                if st.session_state["reset_chat"]:
                    history.reset(" ")

                if is_ready:
                    # Update the chat history and display the chat messages
                    history.append("user", user_input)

                    old_stdout = sys.stdout
                    sys.stdout = captured_output = StringIO()

                    output = st.session_state["chatbot"].run('{}, this is the image path: {}'.
                                                             format(user_input, image_path), callbacks=[st_callback])

                    sys.stdout = old_stdout

                    history.append("assistant", output)

                    # Clean up the agent's thoughts to remove unwanted characters
                    thoughts = captured_output.getvalue()
                    cleaned_thoughts = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', thoughts)
                    cleaned_thoughts = re.sub(r'\[1m>', '', cleaned_thoughts)

                    # Display the agent's thoughts
                    with st.expander("Display the agent's thoughts"):
                        st.write(cleaned_thoughts)

            history.generate_messages(response_container)
        except Exception as e:
            st.error(f"Error: {str(e)}")


