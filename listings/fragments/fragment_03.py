%%writefile ai_agent_test_legacy.py
# ai_agent_test_legacy.py
# Попытка применить классический модульный тест к стохастическому ИИ-агенту
import json

def simulate_ai_bot_inference(user_message: str) -> str:
    """
    Имитация вероятностного ответа локальной языковой модели.
    Даже при минимальной температуре модель склонна использовать синонимы.
    """
    msg_lower = user_message.lower()

    # Если в запросе есть маркеры времени и поломки батареи
    if "вчера" in msg_lower and "разряжается" in msg_lower:
        return '{"client_action": "support", "diagnostic_step": "Пожалуйста, откройте настройки аккумулятора устройства и посмотрите на график энергопотребления."}'

    return '{"client_action": "unknown", "diagnostic_step": null}'

if __name__ == "__main__":
    print("⏳ Запуск модульного теста для ИИ-агента по старой методике...")

    incoming_query = "Мой новый телефон разряжается со 100% до нуля буквально за два часа, что делать? Вчера при ледяной температуре он вообще выключился."

    # Жесткий текстовый эталон, который ожидает увидеть программист в тесте
    expected_diagnostic = "Проверьте раздел Батарея"

    # Извлекаем ответ ИИ и проводим десериализацию JSON-строки
    raw_response = simulate_ai_bot_inference(incoming_query)
    response_data = json.loads(raw_response)
    actual_diagnostic = response_data["diagnostic_step"]

    print(f"\n[Журнал работы] Входящий запрос: '{incoming_query}'")
    print(f"[Журнал работы] Фактический ответ Бота: '{actual_diagnostic}'")

    print("\nВыполнение проверки: assert actual_diagnostic == expected_diagnostic...")
    try:
        assert actual_diagnostic == expected_diagnostic, "Критический сбой: ответ не совпадает с эталоном!"
        print("✅ Тест пройден успешно!")
    except AssertionError as error:
        print(f"❌ Модульный тест ПРОВАЛЕН! Причина: {error}")
        print("[Бизнес-анализ Боба]: Стойте, но ведь Бот ответил идеально по смыслу! Клиент получил вежливую и глубокую помощь!")
