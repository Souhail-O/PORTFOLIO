import os
import base64
import streamlit as st

import ssl

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

from dotenv import load_dotenv
load_dotenv()
#REQUESTS_CA_BUNDLE = os.getenv('REQUESTS_CA_BUNDLE')

#Config
st.set_page_config(layout="wide", page_icon="💬", page_title="Kaufman & Broad | AI-Assistant")


# Logo Kaufman & Broad
# Function to convert image to base64
def get_image_string(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Getting base64 string for the image
img_str = get_image_string("./logo.png")

# Displaying the image in markdown with center align
st.markdown(
    f"""
    <img src="data:image/png;base64,{img_str}" style="display:block;margin-left:auto;margin-right:auto;width:25%;">
    """,
    unsafe_allow_html=True,)

#Title
st.markdown(
    """
    <h1 style='text-align: center;'>Assistant IA</h1>\
     <h2 style='text-align: center;'>Analyse multi-documents</h2>
    """,
    unsafe_allow_html=True,)


st.markdown("---")


#Description
st.markdown(
    """ 
    <h5 style='text-align:center;'>Bonjour 👋, <br>
    Je suis votre assistant virtuel intelligent. J'exploite des modèles linguistiques avancés (LLM) pour fournir des interactions précises et contextuelles.<br>
    Mon but principal est de vous aider à mieux appréhender vos documents. Je gère divers formats tels que PDF, TXT, XLS et transcriptions YouTube.<br>
    """,
    unsafe_allow_html=True)
st.markdown("---")


#Robby's Pages

st.markdown("<h3 style='text-align: center;'> 🧠 Fonctionnalités Disponibles</h3>", unsafe_allow_html=True)
st.write("""
- **Documents Textuels**: Outil d'analyse et de Question/Réponse sur tous vos documents *textuels* (PDF, TXT,CSV)
- **Documents Tabulaires**: Outil d'analyse et de Question/Réponse sur tous vos documents *tabulaires* (CSV, XLS)
- **Vidéos**: Outil d'analyse et de Question/Réponse sur toutes vos *Vidéos* (CSV, XLS)
- **Images**: Outil d'analyse et de Captioning de vos *Images* (CSV, XLS)
""")
st.markdown("---")







