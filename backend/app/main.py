from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import QuestionRequest, AnswerResponse
from .rag_engine import RAGEngine

app = FastAPI(title="Team Knowledge Q&A API")

# Allow frontend (Streamlit) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialise RAG engine (singleton)
rag = RAGEngine()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or TXT file to be indexed."""
    contents = await file.read()
    num_chunks = rag.add_document(file.filename, contents)
    return {"message": f"Uploaded {file.filename}", "chunks_created": num_chunks}

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question based on all uploaded documents."""
    result = rag.answer_question(request.question)
    return AnswerResponse(answer=result["answer"], sources=result["sources"])

@app.get("/health")
async def health():
    return {"status": "ok"}