import streamlit as st


st.set_page_config(
    page_title="My Multi-Page Lab App",
    page_icon=":books:",
    layout="centered",        #
    initial_sidebar_state="expanded"
)

st.sidebar.title("🔹 Lab Navigation")

lab1 = st.Page("lab1.py",title = "LAB 1",icon = ":material/edit:")
lab2 = st.Page("lab2.py",title = "LAB 2",icon = ":material/edit:")

pg = st.navigation([lab1,lab2])
pg.run()
