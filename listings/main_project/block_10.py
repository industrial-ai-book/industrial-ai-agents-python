# Блок кода №10: реализация паттерна автоматического самоисправления (Self-Correction Loop)
import json

print("🔧 Конвейер: Активируем паттерн автоматического самоисправления...")

# Имитируем сырой бракованный вывод, который Бот гипотетически сгенерировал при сбое
defective_json_from_bot = """{
  "recommended_product": "Модель ФотоЭксперт",
  "product_price_usd": "семьсот",
  "text_response": "Отличный аппарат."
}"""

try:
    # Первая попытка проверки достоверности данных — она гарантированно провалится
    AgentOutputSchema.model_validate_json(defective_json_from_bot)
    print("✅ Пакет идеален с первой попытки!")
except Exception as pydantic_error:
    print(f"⚠️ ОТК поймал брак: {pydantic_error}")
    print("🔄 Запуск корректирующего такта генерации на видеокарте...")

    # Собираем экстренное сообщение для Бота, прикладывая точный журнал ошибки
    correction_prompt = f"""Ты совершил синтаксическую ошибку при заполнении схемы JSON.
Твой дефектный вывод: {defective_json_from_bot}
Журнал ошибки компилятора Pydantic: {str(pydantic_error)}

ИСПРАВЬ ОШИБКУ: Выведи строго допустимый JSON по исходной схеме AgentOutputSchema.
Поле product_price_usd должно быть строго ЦЕЛЫМ ЧИСЛОМ. Не пиши текст вокруг."""

    # В реальном живом конвейере этот промпт мгновенно попадает обратно в модель Outlines.
    # И компактная модель Qwen со второй попытки выдает безупречный, исправленный результат:
    fixed_json_from_bot = json.dumps({
        "client_action": "ПОДБОР_ТЕХНИКИ",
        "recommended_product": "Модель ФотоЭксперт",
        "product_price_usd": 700,
        "text_response": "Отличный аппарат."
    }, ensure_ascii=False)

    # Повторная проверка исправленного пакета - теперь она проходит успешно
    AgentOutputSchema.model_validate_json(fixed_json_from_bot)
    print("🎉 Результат: Бот исправил ошибку! Конвейер CRM успешно спасен!")
