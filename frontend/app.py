import streamlit as st
import os
from components.ui_helpers import apply_custom_css
from components.process_visualization import render_process_visualization

st.set_page_config(
    page_title="A-RxM Process Flow Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_custom_css()

# Render Process Visualization Main Dashboard
st.markdown('<div class="main-content">', unsafe_allow_html=True)
render_process_visualization()
st.markdown('</div>', unsafe_allow_html=True)
