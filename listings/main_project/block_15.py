# Блок кода №15: реализация векторизатора TF-IDF и косинусного сходства на чистом Python
import math

print("=== ЗАПУСК ПРАКТИКУМА ЧАСТОТНОЙ ВЕКТОРИЗАЦИИ ТЕКСТА ===")
print("⏳ Инициализируем математические функции и токенизатор...")

def clean_and_tokenize(text: str) -> list:
    """Очищает строку от знаков препинания и нарезает ее на отдельные слова."""
    punctuation = [".", ",", "!", "?", '"', "{", "}", "[", "]", ":", "-", "—", "'"]
    cleaned_text = text.lower()
    for char in punctuation:
        cleaned_text = cleaned_text.replace(char, "")
    return cleaned_text.split()

def compute_term_frequency(document_words: list) -> dict:
    """Вычисляет локальную частоту (TF) каждого слова в конкретном абзаце."""
    tf_dict = {}
    total_words = len(document_words)
    if total_words == 0:
        return tf_dict

    for word in document_words:
        tf_dict[word] = tf_dict.get(word, 0) + 1

    for word in tf_dict:
        tf_dict[word] = tf_dict[word] / total_words
    return tf_dict

def compute_inverse_document_frequency(all_documents_words: list) -> dict:
    """Вычисляет глобальную редкость (IDF) каждого уникального слова в базе."""
    idf_dict = {}
    total_documents = len(all_documents_words)

    # Собираем единый реестр уникальных слов всей нашей базы знаний
    all_unique_words = set(word for doc in all_documents_words for word in doc)

    for word in all_unique_words:
        # Подсчитываем, в скольких фрагментах документов встречается данное слово
        doc_count_with_word = sum(1 for doc in all_documents_words if word in doc)
        # Классическая формула логарифмирования глобальной обратной частоты
        idf_dict[word] = math.log2(total_documents / doc_count_with_word)
    return idf_dict

def build_tfidf_vector(doc_words: list, global_vocabulary: list, idf_registry: dict) -> list:
    """Строит многомерный семантический вектор документа на основе весов TF-IDF."""
    tf_measures = compute_term_frequency(doc_words)
    vector = []

    # Строго соблюдаем геометрию: порядок чисел жестко привязан к осям словаря
    for word in global_vocabulary:
        tf_value = tf_measures.get(word, 0.0)
        idf_value = idf_registry.get(word, 0.0)
        vector.append(tf_value * idf_value)
    return vector

def calculate_cosine_similarity(vector_a: list, vector_b: list) -> float:
    """Вычисляет нормированное косинусное сходство между двумя многомерными векторами."""
    scalar_product = sum(a * b for a, b in zip(vector_a, vector_b))
    length_a = sum(x ** 2 for x in vector_a) ** 0.5
    length_b = sum(x ** 2 for x in vector_b) ** 0.5

    if length_a == 0 or length_b == 0:
        return 0.0
    return scalar_product / (length_a * length_b)

# --- ИСПОЛНЯЕМЫЙ ТЕСТОВЫЙ КОНТУР НА ЖИВЫХ ДАННЫХ МАГАЗИНА БОБА ---
if __name__ == "__main__":
    # Сырая мини-база знаний, содержащая три полярных документа
    raw_documents = [
        "Инструкция: Смартфон ФотоЭксперт имеет аккумулятор. Батарея работает стабильно.",
        "Регламент: Неисправная батарея и неработающее устройство возвращаются на склад.",
        "Каталог: Диван кожаный Милан бытовой комфорт."
    ]

    # 1. Проводим синтаксический анализ и нарезку слов
    tokenized_docs = [clean_and_tokenize(doc) for doc in raw_documents]

    # 2. Формируем эталонные оси многомерного пространства (глобальный алфавит)
    global_vocabulary = sorted(list(set(word for doc in tokenized_docs for word in doc)))
    print(f"📐 Размерность латентного скрытого пространства: {len(global_vocabulary)} осей координат.")

    # 3. Рассчитываем глобальные фильтры шума слов (IDF)
    global_idf = compute_inverse_document_frequency(tokenized_docs)

    # 4. Превращаем сырые тексты документов в цифровые многомерные семантические векторы
    vectors_database = [build_tfidf_vector(doc, global_vocabulary, global_idf) for doc in tokenized_docs]

    # 5. Эмулируем хаотичный, синонимичный поисковый запрос от клиента
    raw_query_client = "Где моя новая батарея, телефон не работает!"
    tokenized_query = clean_and_tokenize(raw_query_client)

    # Переводим запрос клиента в ту же систему координат многомерного пространства
    vector_query = build_tfidf_vector(tokenized_query, global_vocabulary, global_idf)

    print(f"\n[Журнал] Токены очищенного запроса клиента: {tokenized_query}")
    print("⏳ Запуск геометрического сканирования углов базы знаний...")

    print("\n=== ВЕРДИКТ СЕМАНТИЧЕСКОГО АУДИТОРА ДЛЯ СЫРЫХ ДОКУМЕНТОВ ===")
    for idx, doc_vector in enumerate(vectors_database, 1):
        # Вычисляем косинусное сходство между вектором вопроса и вектором документа
        similarity = calculate_cosine_similarity(vector_query, doc_vector)
        print(f"📄 Документ №{idx} [Косинусное сходство смыслов: {similarity:.4f}]")
        print(f"   Текст фрагмента: '{raw_documents[idx-1]}'")
