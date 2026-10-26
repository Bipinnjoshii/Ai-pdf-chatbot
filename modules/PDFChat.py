import os
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from PIL import Image

load_dotenv()

# Safe asset icon resolution
icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.jpeg")
page_icon = icon_path if os.path.exists(icon_path) else "📄"

st.set_page_config(page_title="PDFChat AI — Document Q&A", page_icon=page_icon, layout="wide")
st.header("Ask Your PDF 📄")
st.caption("AI-powered Document Intelligence with Semantic Search")

pdf = st.file_uploader("Upload your PDF document", type="pdf")

if pdf is not None:
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    if not text.strip():
        st.warning("Could not extract readable text from this PDF. Please check if it's scanned or image-based.")
    else:
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )  

        chunks = text_splitter.split_text(text)
        st.info(f"Document processed: {len(pdf_reader.pages)} pages split into {len(chunks)} semantic chunks.")

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")

        if openai_api_key:
            embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            knowledge_base = FAISS.from_texts(chunks, embeddings)

            query = st.text_input("Ask a question about your document:")
            if query:
                docs = knowledge_base.similarity_search(query)

                with get_openai_callback() as cb:
                    llm = OpenAI(openai_api_key=openai_api_key, temperature=0.2)
                    chain = load_qa_chain(llm, chain_type="stuff")
                    response = chain.run(input_documents=docs, question=query)

                st.success(response)
                with st.expander("🔍 View Retrieved Context Chunks"):
                    for i, doc in enumerate(docs):
                        st.markdown(f"**Chunk {i+1}:**")
                        st.write(doc.page_content)
        else:
            st.warning("Please provide an OpenAI API Key in your .env or the input field above to start asking questions.")
