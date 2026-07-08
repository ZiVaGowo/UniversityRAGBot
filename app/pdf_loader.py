import pdfplumber
from typing import List, Dict, Any


def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Загружает PDF с правильной кодировкой через pdfplumber"""
    chunks = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()

                if text and text.strip():
                    # Разбиваем на абзацы
                    paragraphs = text.split('\n\n')

                    for para in paragraphs:
                        para = para.strip()
                        if len(para) > 50:  # Минимальная длина чанка
                            chunks.append({
                                'text': para,
                                'metadata': {
                                    'page': page_num,
                                    'source': file_path.split('/')[-1]
                                }
                            })
    except Exception as e:
        print(f"[ERROR] Ошибка чтения PDF: {e}")

    return chunks