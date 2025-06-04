import streamlit as st
import fitz  # PyMuPDF
import os
import google.generativeai as genai

# Configure API key from environment variable
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    st.error("API key not found! Please set the GENAI_API_KEY environment variable.")
    st.stop()
genai.configure(api_key=api_key)

# Function to extract text from PDF
@st.cache_data(show_spinner=True)
def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

# Generate AI response from conversation + PDF text context
def generate_response(pdf_text, chat_history, user_input):
    conversation = ""
    for turn in chat_history:
        conversation += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"

    prompt = f"""
You are a helpful assistant for AiCouncil. Use the information below to answer user questions naturally without mentioning the source document.

Please provide your answers with clear formatting. Use bullet points or numbered lists wherever applicable to improve readability.

{pdf_text}

Conversation so far:
{conversation}
User: {user_input}
Assistant:
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

def main():
    st.title("AiCouncil PDF Chatbot")

    # Load PDF text once and cache it
    pdf_path = "aicouncil_brochure.pdf"
    pdf_text = extract_pdf_text(pdf_path)

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat input form
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask a question about AiCouncil courses or training:")
        submit = st.form_submit_button("Send")

        if submit and user_input.strip() != "":
            with st.spinner("Generating response..."):
                answer = generate_response(pdf_text, st.session_state.chat_history, user_input)
                st.session_state.chat_history.append({"user": user_input, "assistant": answer})

    # Display chat history in reverse order (latest last)
    if st.session_state.chat_history:
        for chat in st.session_state.chat_history:
            st.markdown(f"**You:** {chat['user']}")
            st.markdown(f"**Assistant:**\n{chat['assistant']}")

if __name__ == "__main__":
    main()
