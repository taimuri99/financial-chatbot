# Chroma vector store
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from src.fin_dashboard.llm import init_llm
import streamlit as st

@st.cache_resource
def create_retriever(texts, chunk_size=1000, chunk_overlap=100, top_k=3):
    
    # Split into chunks
    if not texts.strip():  # empty string check
        texts = "No data available for this company."
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(texts)
    docs = [Document(page_content=chunk) for chunk in chunks]

    with st.spinner("Building retriever and vector store..."):

        # Create in-memory Chroma vectorstore (no persistence needed for Streamlit Cloud)
        vectorstore = Chroma.from_documents(docs, embedding_function=None)  # None if Gemini handles embedding internally

        retriever = vectorstore.as_retriever(search_kwargs={"k": min(top_k, len(docs))})

    # Initialize LLM (Gemini)
    llm = init_llm()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa_chain
