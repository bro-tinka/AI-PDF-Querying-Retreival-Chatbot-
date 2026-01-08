import fitz
import faiss
import numpy as np
import gradio as gr
from sentence_transformers import SentenceTransformer
import os


class PDFRetrievalPipeline:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []

    def ingest_pdfs(self, pdf_files, chunk_size=36, overlap=8):
        chunks = []

        for pdf in pdf_files:
            doc = fitz.open(pdf.name)
            fname = os.path.basename(pdf.name)

            for page in doc:
                words = page.get_text("text").split()
                for i in range(0, len(words), chunk_size - overlap):
                    chunk = " ".join(words[i:i + chunk_size])
                    if chunk.strip():
                        chunks.append(chunk)

        self.chunks = chunks
        embeddings = self.model.encode(chunks).astype("float32")

        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def retrieve(self, query, top_k=3):
        q_emb = self.model.encode([query]).astype("float32")
        _, idx = self.index.search(q_emb, top_k)
        return "\n\n".join(self.chunks[i] for i in idx[0])


def upload_pdfs(files):
    pipeline = PDFRetrievalPipeline()
    pipeline.ingest_pdfs(files)
    return pipeline, "✅ PDFs indexed"


def ask(query, pipeline):
    if pipeline is None:
        return "❌ Upload PDFs first"
    return pipeline.retrieve(query)


with gr.Blocks() as app:
    gr.Markdown("## AI PDF Querying Chatbot")

    state = gr.State()

    pdfs = gr.File(file_types=[".pdf"], file_count="multiple")
    status = gr.Textbox(label="Status")

    question = gr.Textbox(label="Question")
    answer = gr.Textbox(label="Answer", lines=6)

    gr.Button("Index PDFs").click(upload_pdfs, pdfs, [state, status])
    question.submit(ask, [question, state], answer)

app.launch()
