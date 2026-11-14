import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="J.A.R.V.I.S. // IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }
        header, footer, #MainMenu {visibility: hidden;}
        body, .stApp {background-color: #040711;}
    </style>
""", unsafe_allow_html=True)

with open("hud.html", "r", encoding="utf-8") as f:
    jarvis_hud_html = f.read()

components.html(jarvis_hud_html, height=1200, scrolling=True)
