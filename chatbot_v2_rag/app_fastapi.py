from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from retriever.retriever import PDFRetrievalPipeline
from generator.generator import LLMGenerator

app = FastAPI()

# Static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

pipeline = None
generator = LLMGenerator()
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
import shutil
import os

# Import your existing logic
from retriever.retriever import PDFRetrievalPipeline
from generator.generator import LLMGenerator

app = FastAPI()

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize your RAG components
pipeline = None
generator = LLMGenerator()

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    global pipeline
    # Create a temp directory for files if your pipeline needs paths
    os.makedirs("temp_pdfs", exist_ok=True)
    file_paths = []
    
    for file in files:
        path = f"temp_pdfs/{file.filename}"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(path)
    
    pipeline = PDFRetrievalPipeline()
    pipeline.ingest_pdfs(file_paths)
    return {"status": "success", "message": "PDFs indexed Sucessfully! ✅"}

@app.post("/ask")
async def ask_question(query: str = Form(...)):
    if pipeline is None:
        return {"answer": "❌ Error: System offline. Please upload PDFs first."}
    
    context = pipeline.retrieve(query)
    answer = generator.generate_answer(query, context)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    global pipeline

    pipeline = PDFRetrievalPipeline()
    pipeline.ingest_pdfs(files)

    return {"message": "✅ PDFs indexed successfully"}


@app.post("/ask")
async def ask_question(payload: dict):
    global pipeline

    if pipeline is None:
        return JSONResponse(
            status_code=400,
            content={"answer": "⚠ Please upload PDFs first ⚠"}
        )

    query = payload.get("query", "").strip()
    if not query:
        return {"answer": "❌ Empty query"}

    retrieved_chunks = pipeline.retrieve(query, top_k=3)
    answer = generator.generate_answer(query, retrieved_chunks)

    return {"answer": answer}
