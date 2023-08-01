import os
import streamlit as st
from io import StringIO
import re
import sys
from modules.history import ChatHistory
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar

from langchain.agents import AgentType
from langchain.agents import initialize_agent, Tool, load_tools
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chains import LLMMathChain
from langchain.chat_models import ChatOpenAI
from langchain.utilities import WikipediaAPIWrapper, GoogleSearchAPIWrapper
from langchain.memory import ConversationBufferMemory

from dotenv import load_dotenv
load_dotenv()

import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

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

ChatHistory = history_module.ChatHistory
Layout = layout_module.Layout
Utilities = utils_module.Utilities
Sidebar = sidebar_module.Sidebar

st.set_page_config(layout="wide", page_icon="💬", page_title="KB AI - Web Browsing")

# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()

layout.show_header()

user_api_key = utils.load_api_key()

if not user_api_key:
    layout.show_api_key_missing()
else:
    os.environ["OPENAI_API_KEY"] = user_api_key

    # Configure the sidebar
    sidebar.show_options()
    sidebar.about()

    # Initialize chat history
    history = ChatHistory()
    try:
        # Tools setup
        llm = ChatOpenAI(model_name=st.session_state["model"],
                         temperature=st.session_state["temperature"],
                         streaming=True)
        memory = ConversationBufferMemory(memory_key="chat_history")
        search = GoogleSearchAPIWrapper()
        wikipedia = WikipediaAPIWrapper()
        llm_math_chain = LLMMathChain.from_llm(llm)
        tools = [
            Tool(
                name="Google Search",
                func=search.run,
                description="Search Google for recent results. Answer in French",
            ),
            Tool(
                name="Calculator",
                func=llm_math_chain.run,
                description="useful for when you need to answer questions about math",
            ),
            Tool(
                name="Wikipedia",
                func=wikipedia.run,
                description="A useful tool for searching the Internet to find information on world events, issues, etc. Worth using for general topics. Use precise questions.",
            ),
        ]

        # Initialize agent
        chatbot = initialize_agent(tools, llm, memory=memory, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

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

                output = st.session_state["chatbot"].run(user_input, callbacks=[st_callback])

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
        st.error(f"Error something bad happened: {str(e)}")


