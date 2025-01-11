import os
from typing import List
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader, CSVLoader
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def setup_gemini():
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai.GenerativeModel('gemini-pro')

def process_document(file_path: str):
    file_extension = os.path.splitext(file_path)[1].lower()
    st.write(f"Detected file extension: {file_extension}")  # Debugging info
    if file_extension == '.txt':
        return TextLoader(file_path).load()
    elif file_extension == '.pdf':
        return PyPDFLoader(file_path).load()
    elif file_extension == '.csv':
        return CSVLoader(file_path).load()
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def create_vectorstore(documents: List):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = text_splitter.split_documents(documents)
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY
    )
    
    return FAISS.from_documents(texts, embeddings)

def main():
    st.title("Real Time Legal Case Retrival using RAG")
    
    if not GOOGLE_API_KEY:
        st.error("Please set GOOGLE_API_KEY in .env file")
        return
    
    uploaded_file = st.file_uploader("Upload your document", type=['txt', 'pdf', 'csv'])
    
    if uploaded_file:
        # Extract file name and extension
        file_name = uploaded_file.name
        file_extension = os.path.splitext(file_name)[1].lower()
        temp_file_path = f"temp_file{file_extension}"
        
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        try:
            st.write(f"File uploaded successfully: {file_name}")  # Debugging info
            documents = process_document(temp_file_path)
            vectorstore = create_vectorstore(documents)
            
            query = st.text_input("Enter your query:")
            
            if query:
                relevant_docs = vectorstore.similarity_search(query, k=2)
                model = setup_gemini()
                context = "\n".join([doc.page_content for doc in relevant_docs])
                prompt = f"""Based on the following context, answer the query.
                Context: {context}
                Query: {query}
                """
                
                response = model.generate_content(prompt)
                st.write("Response:", response.text)
        except Exception as e:
            st.error(f"Error processing file: {e}")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

if __name__ == "__main__":
    main()
