import streamlit as st

lab1 = st.Page("lab1.py",title = "LAB 1",icon = ":material/add_circle:")
lab2 = st.Page("lab2.py",title = "LAB 2",icon = ":material/add_circle:")

pg = st.navigation([lab1,lab2])
st.set_page_config(page_title="Multi-page app" , page_icon=":material/edit:")
pg.run()
