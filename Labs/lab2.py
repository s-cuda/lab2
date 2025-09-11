import streamlit as st
from openai import OpenAI
import fitz 

# Function to read PDF
def load_pdf(file_obj):
    txt = ""
    with fitz.open(stream=file_obj.read(), filetype="pdf") as pdf:
        for pg in pdf:
            txt += pg.get_text()
    return txt

def app():
    # --- Page title ---
    st.title("LAB - 2 : Summarize Documents (Secret API Key)")
    st.write("Upload a document (TXT or PDF) and get a summary in your preferred language and format.")

    # --- Sidebar options ---
    language = st.sidebar.selectbox(
        "Select Language",
        options=["English", "Spanish", "French", "German"]
    )

    summary_type = st.sidebar.selectbox(
        "Select Summary Type",
        options=[
            "100 words",
            "2 connecting paragraphs",
            "5 bullet points"
        ]
    )

    use_advanced = st.sidebar.checkbox("Use Advanced Model (4o)", value=False)

    # --- Load API key from secrets ---
    openai_api_key = st.secrets["openai"]["api_key"]

    if not openai_api_key:
        st.error("OpenAI API key not found in secrets.toml", icon="🗝️")
    else:
        client = OpenAI(api_key=openai_api_key)

        # --- File uploader ---
        uploaded_file = st.file_uploader(
            "Upload a document (.txt or .pdf)", type=("txt", "pdf")
        )

        if uploaded_file:
            # Detect file type
            file_extension = uploaded_file.name.split(".")[-1].lower()
            if file_extension == "txt":
                document = uploaded_file.read().decode("utf-8")
            elif file_extension == "pdf":
                document = load_pdf(uploaded_file)
            else:
                st.error("Unsupported file type ❌")
                document = None

            # --- Generate summary if document exists ---
            if document:
                model = "gpt-5-4o" if use_advanced else "gpt-5-nano"
                prompt = f"Summarize the following document in {language}.\n\nDocument:\n{document}\n\nSummary type: {summary_type}"

                st.info(f"Using model: {model}", icon="🤖")
                st.subheader("Summary")

                # Generate summary
                stream = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                )
                st.write_stream(stream)
