# Блок кода №17: реализация резидентной векторной базы данных с автовекторизацией на лету
import math

class ResidentVectorStore:
    def __init__(self, threshold: float = 0.75):
        """
        Инициализирует локальное резидентное векторное хранилище в ОЗУ.
        Задает жесткий инженерный порог отсечения смыслового брака.
        """
        self.repository = []
        self.threshold = threshold
        self.global_vocabulary = []
        self.global_idf = {}

    def _clean_and_tokenize(self, text: str) -> list:
        """Внутренний такт: очищает строку от знаков препинания и нарезает на отдельные слова."""
        punctuation = [".", ",", "!", "?", '"', "{", "}", "[", "]", ":", "-", "—", "'"]
        cleaned_text = text.lower()
        for char in punctuation:
            cleaned_text = cleaned_text.replace(char, " ")
        return cleaned_text.split()

    def _compute_tf(self, document_words: list) -> dict:
        """Внутренний такт: вычисляет локальную частоту (TF) каждого слова."""
        tf_dict = {}
        total_words = len(document_words)
        if total_words == 0:
            return tf_dict
        for word in document_words:
            tf_dict[word] = tf_dict.get(word, 0) + 1
        for word in tf_dict:
            tf_dict[word] = tf_dict[word] / total_words
        return tf_dict

    def _calculate_cosine(self, vector_a: list, vector_b: list) -> float:
        """Внутренний такт: расчет нормированного косинусного сходства смыслов."""
        scalar_product = sum(a * b for a, b in zip(vector_a, vector_b))
        length_a = sum(x ** 2 for x in vector_a) ** 0.5
        length_b = sum(x ** 2 for x in vector_b) ** 0.5
        if length_a == 0 or length_b == 0:
            return 0.0
        return scalar_product / (length_a * length_b)

    def fit_vocabulary(self, raw_documents_list: list):
        """
        Сканирует массив сырых документов, формирует единые оси латентного
        пространства и рассчитывает глобальные коэффициенты редкости слов (IDF).
        """
        tokenized_docs = [self._clean_and_tokenize(doc) for doc in raw_documents_list]
        self.global_vocabulary = sorted(list(set(word for doc in tokenized_docs for word in doc)))

        total_documents = len(tokenized_docs)
        for word in self.global_vocabulary:
            doc_count_with_word = sum(1 for doc in tokenized_docs if word in doc)
            self.global_idf[word] = math.log2(total_documents / doc_count_with_word)

    def text_to_vector(self, raw_text: str) -> list:
        """Автоматически переводит сырую текстовую строку в многомерный вектор координат TF-IDF."""
        words = self._clean_and_tokenize(raw_text)
        tf_measures = self._compute_tf(words)
        vector = []
        for word in self.global_vocabulary:
            tf_value = tf_measures.get(word, 0.0)
            idf_value = self.global_idf.get(word, 0.0)
            vector.append(tf_value * idf_value)
        return vector

    def add_document(self, text_chunk: str, metadata: dict = None):
        """Динамически векторизует сырой смысловой фрагмент и сохраняет его паспорт в ОЗУ."""
        # Вычисляем вектор координат "на лету" прямо при добавлении документа!
        semantic_vector = self.text_to_vector(text_chunk)
        self.repository.append({
            "text": text_chunk,
            "vector": semantic_vector,
            "metadata": metadata or {}
        })

    def query_live_search(self, raw_query_text: str, metadata_filter: dict = None, top_k: int = 1) -> list:
        """
        Принимает сырую текстовую строку вопроса клиента, на лету превращает её в вектор
        и осуществляет высокоточный гибридный поиск с фильтрацией метаданных.
        """
        query_vector = self.text_to_vector(raw_query_text)
        scored_results = []

        for item in self.repository:
            if metadata_filter:
                match_failed = False
                for filter_key, filter_value in metadata_filter.items():
                    if item["metadata"].get(filter_key) != filter_value:
                        match_failed = True
                        break
                if match_failed:
                    continue  # Пропускаем расчет косинуса, спасая ОЗУ

            similarity = self._calculate_cosine(query_vector, item["vector"])

            if similarity >= self.threshold:
                scored_results.append({
                    "text": item["text"],
                    "similarity": similarity,
                    "metadata": item["metadata"]
                })

        scored_results.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_results[:top_k]

# --- ИСПЫТАНИЯ АВТОНОМНОГО ПОИСКОВОГО ИНДЕКСА В КОНСОЛИ COLAB ---
if __name__ == "__main__":
    print("=== ЗАПУСК ОНЛАЙН-ТЕСТИРОВАНИЯ МОДЕРНИЗИРОВАННОГО ИНДЕКСА ===")

    # Возвращаем эталонные промышленные тексты с пересекающимися ключевыми словами
    raw_policies = [
        "Инструкция: Смартфон ФотоЭксперт имеет аккумулятор. Батарея работает стабильно. Актуальная модель.",
        "Регламент возврата: Неисправная батарея и неработающее устройство возвращаются на склад. Архивный прайс.",
        "Каталог мебели: Диван кожаный Милан бытовой комфорт для вашей гостиной."
    ]

    db = ResidentVectorStore(threshold=0.20) # Ставим рабочий инженерный порог для частотного поиска
    db.fit_vocabulary(raw_policies)
    print(f"📐 Автоматически развернуто многомерное скрытое пространство: {len(db.global_vocabulary)} осей.")

    # Наполняем базу сырыми строками. Векторы внутри класса сосчитаются автоматически
    db.add_document(raw_policies[0], metadata={"category": "smartphones", "status": "active"})
    db.add_document(raw_policies[1], metadata={"category": "smartphones", "status": "archived"})
    db.add_document(raw_policies[2], metadata={"category": "furniture", "status": "active"})

    # Живой текстовый вопрос покупателя
    live_client_question = "Где моя новая батарея, телефон не работает!"
    search_filter = {"category": "smartphones", "status": "active"}

    print(f"\n[Входящий поток] Сырой текстовый запрос: '{live_client_question}'")
    print(f"[Конвейер] Применен жесткий предфильтр метаданных: {search_filter}")

    raw_results = db.query_live_search(live_client_question, metadata_filter=search_filter, top_k=1)

    print("\n=== ВЕРДИКТ АВТОНОМНОГО ГЕОМЕТРИЧЕСКОГО СЛУЖЕБНОГО ИНДЕКСА ===")
    if raw_results:
        res = raw_results[0]
        print(f"✅ Успешно извлечен точечный факт! [Косинус сходства смыслов: {res['similarity']:.4f}]")
        print(f"   Текст из внешней памяти RAG: '{res['text']}'")
    else:
        print("🚨 Документы не найдены или отсечены по порогу сходства.")
