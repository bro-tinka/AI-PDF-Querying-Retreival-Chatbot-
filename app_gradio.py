import gradio as gr
from retriever.retriever import PDFRetrievalPipeline
from generator.generator import LLMGenerator

pipeline = None
generator = LLMGenerator()

def upload_pdfs(files):
    global pipeline
    pipeline = PDFRetrievalPipeline()
    pipeline.ingest_pdfs(files)
    return "✅ PDFs indexed successfully"

def ask_question(query):
    if pipeline is None:
        return "❌ Please upload PDFs first"

    context = pipeline.retrieve(query)
    answer = generator.generate_answer(query, context)
    return answer

with gr.Blocks(title="PDF RAG Chatbot (Gemini)") as demo:
    gr.Markdown("## 📄 PDF RAG Chatbot (Gemini + FAISS)")

    with gr.Row():
        pdf_files = gr.File(
            label="Upload File (pdf)",
            file_types=[".pdf"],
            file_count="multiple"
        )
        upload_btn = gr.Button("⚡ Index PDFs ⚡")

    status = gr.Textbox(label="Status")

    upload_btn.click(
        upload_pdfs,
        inputs=pdf_files,
        outputs=status
    )

    query = gr.Textbox(label="Ask a question")
    answer = gr.Textbox(label="Answer", lines=10)

    query.submit(
        ask_question,
        inputs=query,
        outputs=answer
    )

demo.launch()
