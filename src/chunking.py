#! ВАЖНО: ДЛЯ ШАХМАТНЫХ ПРАВИЛ НЕЛЬЗЯ ПРОСТО РЕЗАТЬ ПО 500 СИМВОЛОВ
#! НАДО РЕЗАТЬ ПО СТАТЬЯМ - ЧТОБ КАЖДЫЙ КУСОК !БЫЛ ЛОГИЧЕСКИ ЗАВЕРШЁННЫМ ПРАВИЛОМ!

"""Нарезка правил шахмат на логические куски (по статьям)"""

import re 
from langchain_core.documents import Document

def split_by_articles(documents: list[Document]) -> list[Document]:
  """
  Режет правила по ПОДПУНКТАМ, А НЕ СТАТЬЯМ  (3.1, 3.1.1, 3.2, ..., 3.8.2)
  Каждый подпункт становится отдельным куском.
  """
  chunks = []
  
  for doc in documents:
    text = doc.page_content
    text = text.strip()
    
    # Пропускаем страницы без слова "Статья"
    if "Статья" not in text:
      continue

    # Пропускаем содержание (там много точек)
    if text.count("…") > 10:
      continue
    
    # Сначала режем по статьям
    article_pattern = r'(?=Статья\s+\d+\s*[:.])'
    articles = re.split(article_pattern, text)
    for article in articles:
      article = article.strip()
      if not article:
        continue

      # Пропускаем куски без "Статья"
      if not re.match(r'^Статья\s+\d+', article):
        continue

      # Теперь режем статью по подпунктам: 3.1, 3.1.1, 3.2, ...
      # Регулярка: число.число (опционально .число) в начале строки
      subpattern = r'(?=\n\s*\d+\.\d+(?:\.\d+)?\s)'
      subparts = re.split(subpattern, article)

      for subpart in subparts:
        subpart = subpart.strip()
        if not subpart:
          continue

        # Пропускаем слишком короткие куски
        if len(subpart) < 30:
          continue

        chunks.append(Document(
          page_content=subpart,
          metadata={
            "source": doc.metadata.get("source", ""),
            "page": doc.metadata.get("page", 0),
          }
        ))
  
  print(f'✅Разбито на {len(chunks)} кусков (по подпунктам)')
  return chunks

if __name__ == "__main__":
  from loaders import load_pdf

  docs = load_pdf("../data/fide_rules_2023_ru.pdf")
  chunks = split_by_articles(docs)

  print(f"\n📊 Всего кусков: {len(chunks)}")
  print(f"\n📊 Первые 10 кусков:")
  for i, chunk in enumerate(chunks[:10], 1):
    first_line = chunk.page_content.split("\n")[0][:80]
    print(f"  {i}. {first_line}")