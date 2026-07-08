from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from groq import Groq
from app.config import config


class RAGSystem:
    def __init__(self):
        print("[INFO] Загрузка модели эмбеддингов...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.groq_client = Groq(api_key=config.GROQ_API_KEY)
        self.chunks = []
        self.index = None
        print("[OK] Модель загружена!")

    def add_documents(self, chunks: List[Dict[str, Any]]):
        """Добавляет документы и создаёт индекс"""
        self.chunks = chunks

        # Создаём эмбеддинги для всех чанков
        texts = [c['text'] for c in chunks]
        print(f"[INFO] Создание эмбеддингов для {len(texts)} чанков...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        # Создаём FAISS индекс
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings.astype('float32'))

        print(f"[OK] Загружено {len(chunks)} чанков в индекс")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Умный поиск по смыслу"""
        if not self.index or not self.chunks:
            return []

        # Создаём эмбеддинг для вопроса
        query_embedding = self.embedding_model.encode([query])

        # Ищем ближайшие чанки
        distances, indices = self.index.search(
            query_embedding.astype('float32'),
            top_k
        )

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx != -1 and idx < len(self.chunks):
                # Чем меньше расстояние, тем выше релевантность
                score = float(1 / (1 + dist))
                results.append({
                    'text': self.chunks[idx]['text'],
                    'metadata': self.chunks[idx]['metadata'],
                    'score': score
                })

        return results

    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not context:
            return {
                'answer': 'Извините, в документах не найдено информации по вашему вопросу. Попробуйте переформулировать вопрос.',
                'sources': [],
                'confidence': 0.0
            }

        # Формируем контекст для LLM
        context_text = "\n\n".join([
            f"[Документ: {c['metadata']['source']}, стр. {c['metadata']['page']}]\n{c['text']}"
            for c in context
        ])

        prompt = f"""
Ты - помощник университета. Отвечай ТОЛЬКО на основе контекста.
Если ответа нет в контексте - скажи "Я не знаю, обратитесь в Студенческий офис".
В конце укажи источники.

Вопрос: {query}

Контекст:
{context_text}

Ответ:
"""

        try:
            response = self.groq_client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )

            answer = response.choices[0].message.content

            sources = [
                {
                    'document': c['metadata']['source'],
                    'page': c['metadata']['page'],
                    'text': c['text'][:200] + "..."
                }
                for c in context[:3]
            ]

            return {
                'answer': answer,
                'sources': sources,
                'confidence': min(0.9, len(context) * 0.1 + 0.3)
            }

        except Exception as e:
            return {
                'answer': f'Ошибка при генерации: {str(e)}',
                'sources': [],
                'confidence': 0.0
            }