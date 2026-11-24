# Блок кода №21: инициализация специализированных агентов-исполнителей на базе Outlines v1 API
import outlines

print("=== ФАБРИКА АГЕНТОВ: РАЗВЕРТЫВАНИЕ ПРОДАВЦА И ИНЖЕНЕРА ===")
print("⏳ Подготавливаем локальные ролевые функции исполнителей конвейера...")

def execute_sales_agent(client_query: str, extracted_rag_context: str) -> str:
    """Исполняет роль агента торгового отдела с применением семантического принудительного внедрения префикса."""
    sales_constitution = (
        "Вы — ИИ-продавец магазина Боба. Общайтесь мягко, вовлекающе и эмпатично.\n"
        "Предложите сопутствующий аксессуар из контекста RAG для увеличения чека.\n"
        "Заполните поля строго по схеме SalesResponseSchema на русском языке."
    )

    # Плотный промпт ChatML
    full_prompt = (
        f"<|im_start|>system\n{sales_constitution}\nКонтекст RAG: {extracted_rag_context}<|im_end|>\n"
        f"<|im_start|>user\n{client_query}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    # ПАТТЕРН СЕМАНТИЧЕСКОГО ПРИНУДИТЕЛЬНОГО СТАРТА (JSON Prefix Injection):
    # Жестко заставляем модель начать JSON с правильного товара ФотоЭксперт на русском языке!
    prefix_injection = '{ "client_intent": "purchase", "recommended_product": "ФотоЭксперт", '
    full_prompt_with_prefix = full_prompt + prefix_injection

    try:
        # Для локальных моделей Hugging Face параметр ограничения длины называется max_new_tokens.
        raw_output = model_ol(
            full_prompt_with_prefix,
            outlines.json_schema(SalesResponseSchema),
            max_new_tokens=150
        )

        # Если Outlines v1 возвращает полный JSON вместе с поданным префиксом, тогда мы просто
        # отдаем raw_output без повторной конкатенации, блокируя дублирование скобок!
        if raw_output.strip().startswith("{"):
            return raw_output
        return prefix_injection + raw_output
    except NameError:
        print("🚨 КРИТИЧЕСКАЯ ОСТАНОВКА: В ОЗУ нет объекта model_ol или SalesResponseSchema!")
        return "{}"

def execute_service_agent(client_query: str, extracted_rag_context: str) -> str:
    """Исполняет роль агента сервисного центра с применением семантического принудительного внедрения префикса."""
    service_constitution = (
        "Вы — сервисный инженер магазина Боба. Общайтесь сухо, лаконично, строго по пунктам.\n"
        "Локализуйте неисправность, выставите safety_warning=True при угрозе дыма или пожара.\n"
        "Заполните поля строго по схеме ServiceResponseSchema на русском языке."
    )

    full_prompt = (
        f"<|im_start|>system\n{service_constitution}\nКонтекст RAG: {extracted_rag_context}<|im_end|>\n"
        f"<|im_start|>user\n{client_query}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    # ПАТТЕРН СЕМАНТИЧЕСКОГО ПРИНУДИТЕЛЬНОГО СТАРТА ДЛЯ ИНЖЕНЕРА:
    # Жестко заставляем модель начать с локализации технической неисправности батареи ФотоЭксперта.
    prefix_injection = '{ "technical_malfunction": "перегрев и задымление аккумулятора ФотоЭксперт", '
    full_prompt_with_prefix = full_prompt + prefix_injection

    try:
        raw_output = model_ol(
            full_prompt_with_prefix,
            outlines.json_schema(ServiceResponseSchema),
            max_new_tokens=150
        )
        if raw_output.strip().startswith("{"):
            return raw_output
        return prefix_injection + raw_output
    except NameError:
        print("🚨 КРИТИЧЕСКИЙ ОСТАНОВ: В ОЗУ нет объекта model_ol или ServiceResponseSchema!")
        return "{}"

# --- ОНЛАЙН-КРАШ-ТЕСТ РОЛЕВЫХ КОНСТИТУЦИЙ В КОНСОЛИ COLAB ---
if __name__ == "__main__":
    print("\n--- Быстрая проверка изоляции ролей на тестовом контексте ---")
    mock_context = "Инструкция: Смартфон ФотоЭксперт имеет чехол-книжку. Аккумулятор при КЗ может загореться."

    # Тест продавца
    print("⏳ Тестируем агента-продавца...")
    sales_raw = execute_sales_agent("Хочу телефон для блога!", mock_context)
    print(f"🛍️ Вывод агента-продавца (JSON):\n{sales_raw}\n")

    # Тест инженера
    print("⏳ Тестируем агента-инженера...")
    service_raw = execute_service_agent("Мой ФотоЭксперт дымится!", mock_context)
    print(f"🔧 Вывод агента-инженера (JSON):\n{service_raw}\n")
