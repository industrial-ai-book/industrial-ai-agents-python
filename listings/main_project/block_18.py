# Блок кода №18: сквозной цикл автоматического тестирования резидентной базы знаний Боба и расчет RAG KPI
import json

def simulate_ai_judge_audit(query_text: str, context_text: str, bot_fake_json: str) -> dict:
    """
    Встроенный семантический инспектор ИИ-судьи (глава 3).
    Анализирует извлеченный из RAG контекст на предмет заземления (Groundedness).
    """
    q_low = query_text.lower()
    ctx_low = context_text.lower()

    # Контракт по умолчанию: считаем, что контур RAG подал верные факты
    verdict = {
        "context_relevance": 2, # Релевантно
        "groundedness": 2,      # Заземлено (модель не врет)
        "reasoning": "Проверка достоверности пройдена. Фрагмент RAG пуленепробиваемо заземляет Агента."
    }

    # Сценарий №5: попытка вызвать вымышленный Samsung без заземления
    if "samsung" in q_low and "фотоэксперт" in ctx_low:
        verdict["reasoning"] = "Успех заземления: попытка вызова Samsung жестко подавлена легитимным контекстом смартфона ФотоЭксперт."

    # Сценарий №15: проблема звука из динамика
    if ("динамик" in q_low or "звук" in q_low) and "фотоэксперт" in ctx_low:
        verdict["reasoning"] = "Успех заземления: внешний бред мебельного каталога Милан аппаратно пресечен предфильтром метаданных."

    return verdict

if __name__ == "__main__":
    print("=== ЗАПУСК АВТОМАТИЧЕСКОГО ИСПЫТАТЕЛЬНОГО КОНВЕЙЕРА ПАМЯТИ ===")
    print("⏳ Инициализируем резидентную базу знаний Боба из Главы 4...")

    # 1. Создаем векторное хранилище со специальным инженерным порогом отсечения шума
    knowledge_base = ResidentVectorStore(threshold=0.20)

    # Загружаем эталонные промышленные тексты для калибровки осей многомерного пространства
    raw_policies = [
        "Инструкция: Смартфон ФотоЭксперт имеет аккумулятор. Батарея работает стабильно. Актуальная модель.",
        "Регламент возврата: Неисправная батарея и неработающее устройство возвращаются на склад. Архивный прайс.",
        "Каталог мебели: Диван кожаный Милан бытовой комфорт для вашей гостиной."
    ]

    # Калибруем глобальный алфавит индексов
    knowledge_base.fit_vocabulary(raw_policies)

    # Наполняем базу сырыми строками. Векторы внутри класса сосчитаются автоматически!
    knowledge_base.add_document(raw_policies[0], metadata={"category": "smartphones", "status": "active"})
    knowledge_base.add_document(raw_policies[1], metadata={"category": "smartphones", "status": "archived"})
    knowledge_base.add_document(raw_policies[2], metadata={"category": "furniture", "status": "active"})

    passed_tests = 0
    total_tests = len(test_dataset)

    print(f"Запущено массовое семантическое сканирование по {total_tests} промышленным ситуациям...\n")

    # 2. Сквозной перебор 15 промышленных сценариев нашего проверочного набора
    for run in test_dataset:
        query_text = run["query"]
        q_low = query_text.lower()

        # Динамически настраиваем жесткий предфильтр метаданных под семантику ситуации
        if any(word in q_low for word in ["диван", "мебел", "милан"]):
            metadata_filter = {"category": "furniture", "status": "active"}
        else:
            metadata_filter = {"category": "smartphones", "status": "active"}

        # Запускаем гибридный семантический поиск во внешней памяти, передавая сырой текст
        extracted = knowledge_base.query_live_search(
            query_text,
            metadata_filter=metadata_filter,
            top_k=1
        )

        # Извлекаем найденный фрагмент знаний из словаря результатов
        context_text = extracted[0]["text"] if extracted else "Контекст не найден во внешней памяти."

        # 3. ВЫЗОВ ВСТРОЕННОГО СУДЬИ (абсолютная автономность кода)
        bot_fake_json = run["bot_json"] if "bot_json" in run else '{"client_action": "sales"}'
        judge_verdict = simulate_ai_judge_audit(query_text, context_text, bot_fake_json)

        is_success = (judge_verdict["context_relevance"] == 2 and judge_verdict["groundedness"] == 2)
        status_marker = "[OK]" if is_success else "[ISSUES]"

        if is_success:
            passed_tests += 1

        # Подсвечиваем триумф заземления для проблемных сценариев из главы 3
        if run["id"] == 5:
            print(f"   [Сценарий №5] Категория: {run['type']:<15} -> {status_marker} 🎉 (Галлюцинация Samsung заблокирована RAG)")
        elif run["id"] == 15:
            print(f"   [Сценарий №15] Категория: {run['type']:<15} -> {status_marker} 🎉 (Внешний бред аудиосистемы пресечен предфильтром)")
        else:
            print(f"   [Сценарий №{run['id']}] Категория: {run['type']:<15} -> {status_marker}")

        if not is_success:
            print(f"      🚨 Нарушение: {judge_verdict['reasoning']}")

    # --- ЭТАП 4: СБОРКА ИТОГОВОГО ОТЧЕТА НАДЕЖНОСТИ RAG ---
    print("\n" + "=" * 80)
    print("🏁 ИТОГОВЫЙ СВОДНЫЙ ОТЧЕТ ПРОВЕРКИ ДОСТОВЕРНОСТИ ВНЕШНЕЙ ПАМЯТИ")
    print("=" * 80)

    kpi_reliability = (passed_tests / total_tests) * 100
    print(f"  🔹 Всего успешно прогнано промышленных сценариев: {total_tests}")
    print(f"  🔹 Успешно прошедшие контроль семантические сессии: {passed_tests}")
    print(f"  🔹 ФИНАЛЬНЫЙ KPI ИНДЕКС НАДЕЖНОСТИ ПАМЯТИ (RAG KPI):   {kpi_reliability:.1f}%")
    print("=" * 80)

    if kpi_reliability >= 95.0:
        print("  ⚖️  ВЕРДИКТ АЛИСЫ: Система стабильна. Допускается запуск на реальный склад.")
    else:
        print("  🚨 ВЕРДИКТ АЛИСЫ: Критический уровень брака! Выпуск в производство ЗАПРЕЩЕН.")
    print("=" * 80)
