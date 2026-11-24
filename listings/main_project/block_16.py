# Блок кода №16: реализация рекурсивного разделителя контекста со скользящим окном перекрытия

def recursive_context_splitter(text: str, chunk_size: int = 250, overlap: int = 60) -> list:
    """
    Разбивает длинный неструктурированный текст на смысловые фрагменты
    заданного размера со скользящим окном перекрытия.
    Динамически выравнивает как правые, так и левые границы срезов по пробелам и точкам.
    Содержит встроенный предохранитель от зацикливания и перегрузки ОЗУ.
    """
    chunks = []
    start_idx = 0
    text_length = len(text)

    while start_idx < text_length:
        # Рассчитываем предварительную жесткую границу текущего текстового выреза
        end_idx = start_idx + chunk_size

        # Если это финальный фрагмент, забираем остаток текста целиком и завершаем цикл
        if end_idx >= text_length:
            chunks.append(text[start_idx:].strip())
            break

        # Выделяем кандидатный кусок для анализа семантических границ
        candidate_chunk = text[start_idx:end_idx]

        # Поочередно ищем маркеры завершения человеческой мысли по правому краю отсечения
        for separator in [". ", "\n", " "]:
            best_cut_relative = candidate_chunk.rfind(separator)
            if best_cut_relative != -1:
                if separator in [". ", "\n"]:
                    end_idx = start_idx + best_cut_relative + len(separator)
                else:
                    end_idx = start_idx + best_cut_relative
                break

        # Вырезаем фрагмент знаний
        chunk_text = text[start_idx:end_idx].strip()
        chunks.append(chunk_text)

        # Вычисляем индекс старта следующего шага с учетом скользящего окна перекрытия
        next_start_idx = end_idx - overlap

        # ЛЕВАЯ КАЛИБРОВКА (защита от разрыва слов на старте окна перекрытия)
        # Если указатель упал на середину слова, плавно смещаем его влево до ближайшего пробела
        if next_start_idx > start_idx and next_start_idx < text_length:
            while next_start_idx > start_idx and text[next_start_idx] != " ":
                next_start_idx -= 1

        # ИНДУСТРИАЛЬНЫЙ ПРЕДОХРАНИТЕЛЬ: защита от бесконечных циклов
        if next_start_idx <= start_idx:
            start_idx = end_idx
        else:
            start_idx = next_start_idx

    return chunks

# --- ОНЛАЙН-ИСПЫТАНИЯ МОДЕРНИЗИРОВАННОГО АЛГОРИТМА В GOOGLE COLAB ---
if __name__ == "__main__":
    print("=== ТЕСТИРОВАНИЕ РЕКУРСИВНОГО СТРУКТУРИЗАТОРА КОНТЕКСТА ===")

    bob_raw_policy = (
        "Инструкция: Смартфон ФотоЭксперт оснащен литий-ионным аккумулятором емкостью 4500 мАч. "
        "При признаках быстрого разряда проверьте настройки контроллера энергии in меню. "
        "Регламент возврата: Покупатель имеет право вернуть неисправную батарею или неработающее "
        "устройство на склад в течение 14 дней с момента оплаты заказа. Каталог мебели: Диван "
        "премиальный кожаный 'Милан' обеспечивает бытовой комфорт для вашей гостиной."
    )

    print(f"Журнал: Общая длина сырого документа: {len(bob_raw_policy)} символов.\n")

    # Запускаем нарезку с компактными параметрами для контроля вывода
    target_chunks = recursive_context_splitter(bob_raw_policy, chunk_size=160, overlap=50)

    print(f"=== ОТЧЕТ НАВИГАТОРА: Сформировано смысловых фрагментов: {len(target_chunks)} ===")
    for idx, chunk in enumerate(target_chunks, 1):
        print(f"📦 Смысловой фрагмент №{idx} (Размер: {len(chunk)} симв.):")
        print(f"   [{chunk}]\n")
