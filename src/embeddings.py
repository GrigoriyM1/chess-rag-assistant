"""Создание эмбеддингов и сохранение в ChromaDB."""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma 
from langchain_core.documents import Document

def get_embeddings_model():
  """
  Локальная мультиязычная модель эмбеддингов.
  Понимает русский, работает бесплатно.
  """
  embeddings = HuggingFaceEmbeddings(
    model_name='intfloat/multilingual-e5-small',
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
  )
  #! encode_kwargs={'normalize_embeddings': True}
  #! - просто нормализация от -1 до 1 векторов!
  print("✅ Модель эмбеддингов загружена")
  return embeddings

def create_vectorstore(
  chunks: list[Document],
  persist_directory: str = './chroma_db'
):
  """Создаёт векторную базу из кусков."""
  embeddings = get_embeddings_model()
  
  vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=persist_directory,
  )
  print(f"✅ Векторная база создана: {len(chunks)} кусков")
  return vectorstore

if __name__ == "__main__":
  from loaders import load_pdf
  from chunking import split_by_articles

  docs = load_pdf("../data/fide_rules_2023_ru.pdf")
  chunks = split_by_articles(docs)
  vectorstore = create_vectorstore(chunks)

  #! Тестируем поиск - ТОТ САМЫЙ ВОПРОС!
  query = "Можно ли рокировать, если король уже ходил?"
  results = vectorstore.similarity_search(query, k=20)

  print(f"\n🔍 Запрос: {query}")
  for i, doc in enumerate(results, 1):
    print(f"\n--- Результат {i} (стр. {doc.metadata.get('page', '?')}) ---")
    print(doc.page_content[:300])