import streamlit as st
from openai import OpenAI

st.title("LAB - 2 : Answer questions regarding document (SM)")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
)

# Get API key from secrets
openai_api_key = st.secrets["openai"]["api_key"]

if not openai_api_key:
    st.error("OpenAI API key not found in secrets.toml", icon="🗝️")
else:

    client = OpenAI(api_key=openai_api_key)

    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )

    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        document = uploaded_file.read().decode()
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question}",
            }
        ]

        stream = client.chat.completions.create(
            model="gpt-5-nano",
            messages=messages,
            stream=True,
        )

        st.write_stream(stream)
