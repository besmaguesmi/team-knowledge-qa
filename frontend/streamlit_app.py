import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Team Knowledge Q&A", layout="wide")

st.title("Team Knowledge Base Q&A")
st.markdown("Upload your team's documents (PDF/TXT) and ask questions based on their content.")

# Sidebar for file upload
with st.sidebar:
    st.header("Upload Documents")
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
    if uploaded_file is not None:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        try:
            response = requests.post(f"{BACKEND_URL}/upload", files=files)
            if response.status_code == 200:
                st.success(f"Uploaded {uploaded_file.name} successfully!")
            else:
                st.error(f"Upload failed: {response.text}")
        except Exception as e:
            st.error(f"Could not connect to backend: {e}")

# Main area: chat interface
st.header("Ask a Question")
question = st.text_input("Your question:")
if st.button("Ask"):
    if question.strip():
        with st.spinner("Searching documents and generating answer..."):
            try:
                resp = requests.post(f"{BACKEND_URL}/ask", json={"question": question})
                if resp.status_code == 200:
                    data = resp.json()
                    st.subheader("Answer:")
                    st.write(data["answer"])
                    with st.expander("Sources"):
                        for src in data["sources"]:
                            st.write(f"- {src}")
                else:
                    st.error(f"Error: {resp.text}")
            except Exception as e:
                st.error(f"Backend connection error: {e}")
    else:
        st.warning("Please enter a question.")