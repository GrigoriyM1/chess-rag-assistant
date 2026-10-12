# app.py
"""Streamlit интерфейс для шахматного RAG-ассистента."""

import streamlit as st
from src.loaders import load_pdf
from src.chunking import split_by_articles
from src.embeddings import create_vectorstore
from src.rag import create_rag_chain

# ============================================
# НАСТРОЙКИ СТРАНИЦЫ
# ============================================

st.set_page_config(page_title="Шахматный RAG-ассистент", page_icon="♟️")
st.title("♟️ Шахматный RAG-ассистент")
st.markdown("Задай вопрос по правилам шахмат ФИДЕ 2023")

# ============================================
# ИНИЦИАЛИЗАЦИЯ (один раз)
# ============================================

if "chain" not in st.session_state:
  with st.spinner("Загружаю правила шахмат..."):
    docs = load_pdf("data/fide_rules_2023_ru.pdf")
    chunks = split_by_articles(docs)
    vectorstore = create_vectorstore(chunks)
    st.session_state.chain = create_rag_chain(vectorstore)
  st.success("✅ Правила загружены! Можешь задавать вопросы.")

# ============================================
# ЧАТ
# ============================================

if "messages" not in st.session_state:
  st.session_state.messages = []

# Показываем историю
for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])

# Поле ввода
if question := st.chat_input("Задай вопрос по правилам шахмат..."):
  # Показываем вопрос
  st.session_state.messages.append({"role": "user", "content": question})
  with st.chat_message("user"):
    st.markdown(question)

  # Генерируем ответ
  with st.chat_message("assistant"):
    with st.spinner("Ищу в правилах..."):
      answer = st.session_state.chain.invoke(question)
    st.markdown(answer)

  st.session_state.messages.append({"role": "assistant", "content": answer})
  
#! streamlit run app.py    ГРУЗИТ ДОЛГО САЙТ, ЖДЕМ!

#* НЕ ВСЕ ОТВЕТЫ МОЖЕТ ИДЕАЛЬНО ДАВАТЬ - ЭТО НОРМАЛЬНО!!