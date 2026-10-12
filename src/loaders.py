# src/loaders.py
"""Загрузка PDF с правилами шахмат."""

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


#! в loaders.py правильное разбиение по темам, а не просто по такой-то длине например каждые 400 символов 
# !поэтому находит закономерности нормально между правилами и не тупит!! 

def load_pdf(file_path: str):
  """
  Загружает PDF и возвращает список страниц.
  Каждая страница — отдельный Document с метаданными.
  """
  path = Path(file_path)

  if not path.exists():
    raise FileNotFoundError(f"Файл не найден: {file_path}")

  if path.suffix.lower() != ".pdf":
    raise ValueError(f"Ожидается PDF, получен: {path.suffix}")

  loader = PyPDFLoader(str(path))
  documents = loader.load()

  print(f"✅ Загружено {len(documents)} страниц из {path.name}")

  # Показываем первую страницу для проверки
  print(f"\n📄 Первая страница (фрагмент):")
  print(documents[0].page_content[:300])

  return documents


if __name__ == "__main__":
  docs = load_pdf("../data/fide_rules_2023_ru.pdf")
  print(f"\n📊 Всего страниц: {len(docs)}")
  print(f"📊 Метаданные первой страницы: {docs[0].metadata}")