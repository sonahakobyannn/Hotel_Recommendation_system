import os
import uuid
import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma  

st.session_state.setdefault('chat_history', [])

def process_request():
    if st.session_state.search_input:
        st.session_state.chat_history.append(("You:", st.session_state.search_input))
        try:
            search_input = st.session_state.search_input
            results = perform_similarity_search(search_input)
            prompt = generate_chat_prompt(results, search_input)
            search_result = ChatOpenAI(model_name='gpt-4-0125-preview').predict(prompt)
            handle_response(results, search_result)
            st.session_state.search_input = ""

        except Exception as e:
            handle_error(e)

def perform_similarity_search(search_input):
    try:
        return Chroma(persist_directory="chromadb/", embedding_function=OpenAIEmbeddings(api_key=api_key)).similarity_search_with_relevance_scores(search_input)
    except Exception as e:
        raise Exception("Error performing similarity search:", e)

def generate_chat_prompt(results, search_input):
    try:
        text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

        prompt_template = ChatPromptTemplate.from_template("""
        Using the comprehensive hotel data stored in ChromaDB, please provide recommendations that 
        best match the user’s description of their preferred place to stay. If the user’s initial 
        prompt lacks clarity, follow up with additional questions to better understand 
        their preferences and requirements. Focus on delivering personalized and accurate 
        hotel suggestions based on the detailed user input:{background}
        Having the background provided above and the data in ChromaDB generate hotel recommendations:{question}
        """)
        return prompt_template.format(background=text, question=search_input)
    except Exception as e:
        raise Exception("Error generating chat prompt:", e)

def handle_response(results, search_result):
    try:
        if not results or results[0][1] < 0.6:
            st.session_state.chat_history.append(("AI assistant:", "Please clarify your question or provide additional details to help me better assist you!"))
        else:
            st.session_state.chat_history.append(("AI assistant:", search_result))
    except Exception as e:
        raise Exception("Error handling response:", e)

def handle_error(error):
    st.error(f"An error occurred: {error}")
    st.session_state.chat_history.append(("AI assistant:", "Try later as I encountered an error"))


st.set_page_config(page_title='Hotel Recommendation Assistant')
api_key = st.secrets["openai_api_key"] if 'openai_api_key' in st.secrets else os.getenv('openai_api_key')
if not api_key:
    st.error("API key not found. Please set it as an environment variable or in secrets.toml.")
    st.stop()

st.markdown("""
<h1 style="text-align: center; color: #4169E1;">Hotel Recommendation Assistant</h1>
<style>
    .reportview-container .main .block-container { padding-top: 5rem; }
    .chatbox-container { position: fixed; bottom: 5rem; left: 50%; transform: translate(-50%, 0); width: 90%; }
    .chat-message { color: white; background-color: #4169E1; border-radius: 5px; padding: 10px; margin-bottom: 10px; font-weight: bold; } /* Royal blue background with bold white text for chat messages */
    .chat-input { color: black; background-color: #d3d3d3; border-radius: 5px; padding: 10px; margin-top: 20px; }  /* Pale gray background and black text for input */
    .chat-input::placeholder, input::placeholder { color: black !important; opacity: 1; }  /* Black placeholder text */
    body { background-color: white; }  /* Set the background to white */
    .stButton>button { background-color: #4169E1; color: white; border: none; border-radius: 5px; padding: 10px 20px; font-weight: bold; } /* Styling the Streamlit button specifically */
</style>
""", unsafe_allow_html=True)


search_input = st.text_input("", placeholder="What are your hotel preferences?", key="search_input", on_change=process_request)
Search = st.button('Search', on_click=process_request)

for message in reversed(st.session_state.chat_history):
    unique_key = str(uuid.uuid4())
    message_type, message_text = message
    st.text_area(label="", value=f"{message_type} {message_text}", height=110, key=unique_key, disabled=True)

