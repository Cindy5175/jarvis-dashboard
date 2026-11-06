import streamlit as st
import datetime
import sqlite3
import io

# Importación segura de gTTS para voz y autorefresh
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
