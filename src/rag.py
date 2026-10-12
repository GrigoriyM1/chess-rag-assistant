"""RAG-цепочка: поиск в ChromaDB + генерация ответа через Ollama"""

import os 
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def format_docs(docs):
  """Склеивает найденные куски в один текст для LLM."""
  return '\n\n'.join(doc.page_content for doc in docs)

def create_rag_chain(vectorstore, model_name: str = 'llama3.2'):
  """
  Создаёт RAG-цепочку:
  вопрос -> поиск в ChromaDB -> промпт -> LLM -> ответ
  """
  
  #! 1. Retriever (берём 5 кусков, т.к. статья короткие)
  retriever = vectorstore.as_retriever(search_kwargs={'k': 5})
  
  #! 2. LLM через Ollama 
  OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
  llm = ChatOllama(
    model=model_name, 
    temperature=0, 
    base_url=OLLAMA_HOST
  )
  
  #! 3. Промпт для шахматного ассистента 
  template = """Ты — ассистент по правилам шахмат ФИДЕ.
  Отвечай на вопрос, используя ТОЛЬКО следующий контекст.
  Если ответа в контексте нет — скажи "Я не знаю".
  В конце ответа укажи номер статьи, из которой взял информацию.

  Контекст:
  {context}

  Вопрос: {question}

  Ответ:"""
  
  prompt = ChatPromptTemplate.from_template(template)
  
  #! 4. Собираем цепочку 
  chain = (
    {
      "context": retriever | format_docs,
      "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
  )
  print(f"✅ RAG-цепочка готова (модель: {model_name})")
  return chain

if __name__ == "__main__":
  import json
  from loaders import load_pdf
  from chunking import split_by_articles
  from embeddings import create_vectorstore

  # 1. Загружаем документ и режем
  docs = load_pdf("../data/fide_rules_2023_ru.pdf")
  chunks = split_by_articles(docs)

  # 2. Создаём векторную базу
  vectorstore = create_vectorstore(chunks)

  # 3. Создаём RAG-цепочку
  chain = create_rag_chain(vectorstore)

  # 4. Загружаем тестовые вопросы из evals
  with open("../evals/test_questions.json", "r", encoding="utf-8") as f:
    test_questions = json.load(f)

  # 5. Прогоняем все вопросы
  for i, item in enumerate(test_questions, 1):
    question = item["question"]
    correct = item["correct_answer"]

    print(f"\n{'='*60}")
    print(f"❓ Вопрос {i}: {question}")
    print(f"✅ Ожидаемый ответ: {correct}")

    answer = chain.invoke(question)
    print(f"💬 Ответ LLM: {answer}")
#! ollama serve ЗАПУСТИТЬ НАДО!!  ЧТОБ ОШИБОК НЕ БЫЛО!!