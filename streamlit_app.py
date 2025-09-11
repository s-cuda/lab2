import streamlit as st
from Labs import lab1, lab2, lab3

st.set_page_config(
    page_title="My Lab Manager",
    page_icon="📚",
    layout="wide"
)

st.title("Lab Manager")

st.sidebar.header("🧭 Navigation")
st.sidebar.markdown("---")

# Sidebar navigation
selection = st.sidebar.radio("Go to", ["LAB 1", "LAB 2","Lab 3"])

if selection == "LAB 1":
    lab1.app()  
elif selection == "LAB 2":
    lab2.app()
elif selection == "Lab 3":
    lab3.app() 
