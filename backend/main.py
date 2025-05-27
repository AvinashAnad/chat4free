from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pathlib import Path
from llama_cpp import Llama
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import LlamaCpp

# === Configuration ===
MODEL_PATH = "models/llama-3.gguf"  # Update this to actual gguf model path
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
UPLOAD_DIR = "uploaded_docs"

# Create directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
    with open("frontend/index.html", "r") as f:
        return f.read()

# Load LLaMA model (once, on startup)
llm = LlamaCpp(
    model_path=MODEL_PATH,
    n_ctx=2048,
    temperature=0.7,
    max_tokens=512,
    n_threads=os.cpu_count()
)

@app.post("/chat/")
async def chat(message: str = Form(...)):
    response = llm(message)
    return {"response": response["choices"][0]["text"].strip()}

@app.post("/summarize/")
async def summarize(file: UploadFile = File(...)):
    file_path = Path(UPLOAD_DIR) / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Load document and split text
    loader = UnstructuredFileLoader(str(file_path))
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    # Create embedding store
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever()

    # Setup QA chain
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    result = qa_chain.run("Summarize this document.")

    os.remove(file_path)

    return JSONResponse(content={"summary": result})
