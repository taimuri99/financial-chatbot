# chroma vector store embeddings
# split texts, create docs, embeddings, vectorstore, retriever

from langchain_community.vectorstores import Chroma
# from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from .config import EMBEDDINGS_MODEL
from .llm import init_llm
import streamlit as st
#import os

@st.cache_resource
def create_retriever(texts, chunk_size=1000, chunk_overlap=100, top_k=3):
    
    # Split into chunks
    if not texts.strip():  # empty string check
        texts = "No data available for this company."  # safe fallback
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(texts)
    docs = [Document(page_content=chunk) for chunk in chunks]

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL, model_kwargs={"device": "cpu"})

    with st.spinner("Building retriever and vector store..."):
    
        #Load or create persistent Chroma vectorstore
        # db_path = "data/chroma"
        # # Create vectorstore
        # if os.path.exists(db_path) and os.listdir(db_path):
        #     # Load existing DB
            
        #     vectorstore = Chroma(embedding_function=embeddings, persist_directory=db_path)
        #     # Append new docs
        #     vectorstore.add_documents(docs)
        # else:
        #     # Create new DB
        #     vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=db_path)
        # vectorstore.persist()  # saves to disk

        #Chroma not working locally, faiss for local testing
        #vectorstore = FAISS.from_documents(docs, embeddings)

        #uploading to streamlit so skip pers directory and reboot eachtimw
        vectorstore = Chroma.from_documents(docs, embeddings)


        retriever = vectorstore.as_retriever(search_kwargs={"k": min(top_k, len(docs))})

    # Initialize QA
    llm = init_llm()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa_chain
