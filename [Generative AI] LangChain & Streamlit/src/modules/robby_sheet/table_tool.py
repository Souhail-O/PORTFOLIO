import re
import sys
from io import StringIO, BytesIO

import folium.folium
import matplotlib.pyplot as plt
import streamlit as st
from langchain.callbacks import get_openai_callback
from streamlit_chat import message
from streamlit_folium import st_folium, folium_static

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

from pandasai.middlewares.base import Middleware
from pandasai.middlewares.streamlit import StreamlitMiddleware


class StreamlitMiddleware2(Middleware):
    """Streamlit Middleware class"""

    def run(self, code: str) -> str:
        """
        Run the middleware to make the code compatible with streamlit.
        For example, it replaces `plt.show()` with `st.pyplot()`.

        Returns:
            str: Modified code
        """
        #draw a pie chart of the revenues of the 10 biggest companies

        code = "import streamlit as st\n" + code
        code = code.replace("plt.show(block=False)", "")
        # code = code.replace("plt.show(block=False)", "st.pyplot(plt.gcf())")
        code = code.replace("plt.close('all')", "")
        return code


class FigureCatcher:
    def __init__(self):
        self._figs = []
        plt.gcf().canvas.mpl_connect('draw_event', self)

    def __call__(self, event):
        fig = event.canvas.figure
        self._figs.append(fig)

    @property
    def figures(self):
        return self._figs


class PandasAgent:

    @staticmethod
    def count_tokens_agent(agent, query):
        """
        Count the tokens used by the CSV Agent
        """
        with get_openai_callback() as cb:
            result = agent(query)
            st.write(f'Spent a total of {cb.total_tokens} tokens')

        return result
    
    def __init__(self):
        pass

    def get_agent_response(self, uploaded_file_content, query):
        llm = OpenAI(model_name="gpt-4")
        pandas_ai = PandasAI(llm, verbose=True, middlewares=[StreamlitMiddleware(), StreamlitMiddleware2()],
                             custom_whitelisted_dependencies=["folium", "geopandas"])
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        response = pandas_ai.run(data_frame=uploaded_file_content, prompt=query)
        fig = plt.gcf()
        #st.pyplot(fig)

        sys.stdout = old_stdout
        return response, captured_output, fig


    def display_agent_response(self, response, fig=None):
        if isinstance(response, pd.DataFrame) or isinstance(response, pd.Series):
            # If the response is a DataFrame or a Series, display it as a dataframe
            st.dataframe(response)
        elif isinstance(response, (int, float, str)):
            # If the response is a number, display it with st.write
            st.write(response)
        if fig is not None:
            # If a figure is present, display it with st.pyplot
            tab1, tab2 = st.tabs(["Streamlit theme (default)", "same"])
            with tab1:
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            with tab2:
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    def process_agent_thoughts(self, captured_output):
        thoughts = captured_output.getvalue()
        cleaned_thoughts = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', thoughts)
        cleaned_thoughts = re.sub(r'\[1m>', '', cleaned_thoughts)
        return cleaned_thoughts

    def display_agent_thoughts(self, cleaned_thoughts):
        with st.expander("Display the agent's thoughts"):
            st.write(cleaned_thoughts)

    def update_chat_history(self, query, result, image=None):
        st.session_state.chat_history.append(("user", query))
        st.session_state.chat_history.append(("agent", (result, image)))

    def display_chat_history(self):
        for i, (sender, message_text) in enumerate(st.session_state.chat_history):
            if sender == "user":
                message(message_text, is_user=True, key=f"{i}_user")
            else:
                with st.chat_message('assistant'):
                    if isinstance(message_text, tuple):
                        response, fig = message_text
                        if isinstance(response, pd.DataFrame) or isinstance(response, pd.Series):
                            # If the response is a DataFrame or a Series, display it as a dataframe
                            st.dataframe(response)
                        elif isinstance(response, folium.folium.Map):
                            folium_static(response, width=725)
                        elif fig.axes:
                            col1, col2, col3 = st.columns([2, 5, 2])
                            with col2:
                                st.pyplot(fig, use_container_width=True)
                        # elif isinstance(response, (int, float, str, list)):
                        else:
                            # If the response is a number, display it with st.write
                            st.write(response)
                    else:
                        st.write("Unknown response type: ", type(response))