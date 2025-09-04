import streamlit as st

st.set_page_config(
    page_title="My Multi-Page Lab App",
    page_icon=":books:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.header("Lab Navigation")
st.sidebar.markdown("---")  # horizontal divider

# Define lab pages
lab2 = st.Page("lab2.py", title="LAB 2", icon=":material/edit:")
lab1 = st.Page("lab1.py", title="LAB 1", icon=":material/edit:")


# Navigation
pg = st.navigation([lab2, lab1])
pg.run()