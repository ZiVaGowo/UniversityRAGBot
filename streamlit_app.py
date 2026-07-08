import streamlit as st
import requests

st.set_page_config(page_title="UniversityRAGBot", page_icon="🎓")

st.title("🎓 UniversityRAGBot")
st.write("AI-ассистент для студентов")

# Боковая панель
with st.sidebar:
    st.header("Настройки")
    top_k = st.slider("Количество документов", 3, 10, 5)
    st.write(f"Используется {top_k} документов")

    st.divider()
    st.write("📚 Источники:")
    st.write("- Академическая политика")
    st.write("- Правила приема")
    st.write("- Академический календарь")

# Инициализация истории
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение истории
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        # Если есть источники
        if "sources" in msg and msg["sources"]:
            with st.expander("📚 Источники"):
                for src in msg["sources"]:
                    st.write(f"- {src['document']} (стр. {src['page']})")

# Ввод вопроса
if prompt := st.chat_input("Задайте вопрос..."):
    # Добавляем вопрос пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Ответ ассистента
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            try:
                # Отправка запроса к API
                response = requests.post(
                    "http://localhost:8000/ask",
                    json={"query": prompt, "top_k": top_k},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Нет ответа")
                    sources = data.get("sources", [])

                    st.write(answer)

                    # Сохраняем в историю
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                    # Показываем источники
                    if sources:
                        with st.expander("📚 Источники"):
                            for src in sources:
                                st.write(f"- **{src['document']}** — стр. {src['page']}")
                else:
                    st.error(f"Ошибка: {response.status_code}")

            except Exception as e:
                st.error(f"Ошибка: {str(e)}")