import streamlit as st

class Layout:
    
    def show_header(self, types_files=None):
        """
        Displays the header of the app
        """
        if not types_files:
            st.markdown(
                f"""
                <h1 style='text-align: center;'> Consulter le Web avec ChatGPT !</h1>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <h1 style='text-align: center;'> Analysez vos documents {types_files} !</h1>
                """,
                unsafe_allow_html=True,
            )

    def show_api_key_missing(self):
        """
        Displays a message if the user has not entered an API key
        """
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>Enter your <a href="https://platform.openai.com/account/api-keys" target="_blank">OpenAI API key</a> to start chatting</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def prompt_form(self):
        """
        Displays the prompt form
        """
        with st.form(key="my_form", clear_on_submit=True):
            user_input = st.text_area(
                "Query:",
                placeholder="Posez vos questions sur le document...",
                key="input",
                label_visibility="collapsed",
            )
            submit_button = st.form_submit_button(label="Send")
            
            is_ready = submit_button and user_input
        return is_ready, user_input
    
