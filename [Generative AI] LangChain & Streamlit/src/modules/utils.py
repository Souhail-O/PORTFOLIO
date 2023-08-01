import os
import pandas as pd
import streamlit as st
import pdfplumber
import base64
from PIL import Image
from io import BytesIO

from modules.chatbot import Chatbot
from modules.embedder import Embedder


class Utilities:

    @staticmethod
    def load_api_key():
        """
        Loads the OpenAI API key from the .env file or 
        from the user's input and returns it
        """
        if not hasattr(st.session_state, "api_key"):
            st.session_state.api_key = None
        # you can define your API key in .env directly
        if os.path.exists(".env") and os.environ.get("OPENAI_API_KEY") is not None:
            user_api_key = os.environ["OPENAI_API_KEY"]
            st.sidebar.success("API key loaded from .env", icon="🚀")
        else:
            if st.session_state.api_key is not None:
                user_api_key = st.session_state.api_key
                st.sidebar.success("API key loaded from previous input", icon="🚀")
            else:
                user_api_key = st.sidebar.text_input(
                    label="#### Your OpenAI API key 👇", placeholder="sk-...", type="password"
                )
                if user_api_key:
                    st.session_state.api_key = user_api_key

        return user_api_key

    @staticmethod
    def handle_upload(file_types):
        """
        Handles and display uploaded_file
        :param file_types: List of accepted file types, e.g., ["csv", "pdf", "txt"]
        """
        uploaded_files = st.sidebar.file_uploader("upload", type=file_types,
                                                      label_visibility="collapsed",
                                                      accept_multiple_files=True)

        if uploaded_files is not None:

            def show_csv_file(uploaded_file):
                file_container = st.expander(f"Visualisez votre document CSV : {uploaded_file.name}")
                uploaded_file.seek(0)
                shows = pd.read_csv(uploaded_file)
                file_container.write(shows)

            def show_pdf_file(uploaded_file):
                file_container = st.expander(f"Visualisez votre document PDF : {uploaded_file.name}")

                uploaded_file.seek(0)
                raw_bytes = uploaded_file.read()
                base64_pdf = base64.b64encode(raw_bytes).decode('utf-8')

                # Embedding PDF in HTML
                pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" ' \
                              F'width="1000" height="1000" type="application/pdf">'

                # Displaying File
                #file_container.markdown(pdf_display, unsafe_allow_html=True)

                with pdfplumber.open(uploaded_file) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text() + "\n\n"
                file_container.write(pdf_text)

            def show_txt_file(uploaded_file):
                file_container = st.expander(f"Visualisez votre document TXT: {uploaded_file.name}")
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("utf-8")
                file_container.write(content)

            def show_img_file(uploaded_file):
                file_container = st.expander(f"Visualisez votre IMAGE: {uploaded_file.name}")
                uploaded_file.seek(0)
                content = uploaded_file.read()

                # Convert the file to an image
                img = Image.open(BytesIO(content))

                # Convert RGBA images to RGB
                if img.mode == "RGBA":
                    img = img.convert("RGB")

                # Convert the image to base64 and include MIME type
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                # Display the image
                file_container.markdown(f"<center><img src='data:image/png;base64,{img_str}' width=60%></center>",
                                        unsafe_allow_html=True)

            def get_file_extension(uploaded_file):
                return os.path.splitext(uploaded_file)[1].lower()

            for uploaded_file in uploaded_files:
                file_extension = get_file_extension(uploaded_file.name)

                # Show the contents of the file based on its extension
                if file_extension == ".csv":
                    show_csv_file(uploaded_file)
                if file_extension == ".pdf":
                    show_pdf_file(uploaded_file)
                elif file_extension == ".txt":
                    show_txt_file(uploaded_file)
                elif file_extension == ".png":
                    show_img_file(uploaded_file)

        else:
            st.session_state["reset_chat"] = True

        return uploaded_files

    @staticmethod
    def setup_chatbot(uploaded_files, model, temperature):
        """
        Sets up the chatbot with the uploaded file, model, and temperature
        """
        embeds = Embedder()
        vectors = []

        for uploaded_file in uploaded_files:
            with st.spinner("Processing..."):
                uploaded_file.seek(0)
                file = uploaded_file.read()
                # Get the document embeddings for the uploaded file
                vector = embeds.getDocEmbeds(file, uploaded_file.name)
                vectors.append(vector)

        if len(vectors) == 1:
            global_vector = vectors[0]
        else:
            global_vector = vectors[0]
            for vector in vectors[1:]:
                global_vector.merge_from(vector)

        # Create a Chatbot instance with the specified model and temperature
        chatbot = Chatbot(model, temperature, global_vector)
        st.session_state["ready"] = True

        return chatbot
