from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import glob

load_dotenv()

from app.pdf_loader import load_pdf
from app.rag import RAGSystem

app = FastAPI(title="UniversityRAGBot")
rag = RAGSystem()


# Загрузка ВСЕХ PDF из папки data/
def load_all_pdfs():
    """Загружает все PDF из папки data/"""
    all_chunks = []
    pdf_files = glob.glob('data/*.pdf')

    if not pdf_files:
        print("[WARNING] Нет PDF файлов в папке data/")
        return

    for pdf_path in pdf_files:
        print(f"[INFO] Загрузка: {pdf_path}")
        chunks = load_pdf(pdf_path)
        all_chunks.extend(chunks)
        print(f"[OK] Загружено {len(chunks)} чанков из {os.path.basename(pdf_path)}")

    if all_chunks:
        rag.add_documents(all_chunks)
        print(f"[OK] Всего загружено {len(all_chunks)} чанков")
    else:
        print("[WARNING] Не удалось загрузить ни одного чанка")


# Загрузка при старте
load_all_pdfs()


class Question(BaseModel):
    query: str
    top_k: Optional[int] = 5


@app.post("/ask")
async def ask(q: Question):
    try:
        context = rag.search(q.query, q.top_k)
        result = rag.generate_answer(q.query, context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "UniversityRAGBot с RAG работает!",
        "chunks_loaded": len(rag.chunks)
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "chunks_loaded": len(rag.chunks) > 0,
        "chunks_count": len(rag.chunks)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)