# Блок кода №20: реализация агента-классификатора намерений на базе Outlines v1 API
import json
import outlines
from pydantic import BaseModel, Field
from enum import Enum

print("\n=== ФАБРИКА АГЕНТОВ: РАЗВЕРТЫВАНИЕ ВХОДНОГО МАРШРУТИЗАТОРА ===")
print("⏳ Инициализируем схемы данных для жесткой маршрутизации...")

# Создаем строгую схему выбора режима маршрутизации трафика
class RouteEnum(str, Enum):
    SALES = "ROUTE_TO_SALES"          # Направление в торговый отдел
    SERVICE = "ROUTE_TO_SERVICE"      # Направление в сервисный центр
    FALLBACK = "ROUTE_TO_FALLBACK"    # Аварийный контур сброса мусорного шума

class RoutingDecisionSchema(BaseModel):
    """Схема жесткого детерминированного выбора маршрута."""
    route: RouteEnum = Field(description="Выбранный системный токен маршрутизации трафика.")

print("✅ Схемы успешно подготовлены в памяти. Модуль готов к обработке трафика.")

def agent_intent_router(client_raw_text: str) -> str:
    """
    Принимает сырую речь клиента, анализирует латентные намерения
    и возвращает JSON-строку со строго валидированным токеном маршрута.
    """
    # Сверхкомпактный, агрессивный производственный промпт для малых ядер 1.5B
    system_router_prompt = (
        "Вы — Маршрутизатор ИИ торговой компании Боба.\n"
        "Классифицируйте текст строго по ключевым триггерам:\n"
        "- Купить, цена, ФотоExpert, заказ, каталог, чехол -> ROUTE_TO_SALES\n"
        "- Сломалось, не работает, ремонт, батарея, дым, экран -> ROUTE_TO_SERVICE\n"
        "- Спам, погода, бред, Paris, шутка, любой посторонний шум -> ROUTE_TO_FALLBACK\n"
        "Выдайте ответ строго в формате JSON по схеме RoutingDecisionSchema."
    )

    full_prompt = f"<|im_start|>system\n{system_router_prompt}<|im_end|>\n<|im_start|>user\n{client_raw_text}<|im_end|>\n<|im_start|>assistant\n"

    try:
        # Для локальных моделей Hugging Face параметр ограничения длины называется max_new_tokens.
        # Передаем значение 20, чтобы заглушить предупреждения и ускорить генерацию.
        json_output = model_ol(
            full_prompt,
            outlines.json_schema(RoutingDecisionSchema),
            max_new_tokens=20
        )
        return json_output
    except NameError:
        print("🚨 КРИТИЧЕСКИЙ ОСТАНОВ: В ОЗУ нет объекта model_ol! Сначала запустите блок кода №7 из главы 2.")
        return '{"route": "ROUTE_TO_FALLBACK"}'

# --- ДИНАМИЧЕСКОЕ СТРЕСС-ТЕСТИРОВАНИЕ КЛАССИФИКАТОРА В КОНСОЛИ GOOGLE COLAB ---
if __name__ == "__main__":
    print("\n--- Проверяем работу ИИ-классификатора на живых фразах ---")

    test_phrases = [
        "Привет, я хочу купить ФотоExpert и какой-нибудь чехол к нему!",
        "Мой телефон раскалился и батарея тает на глазах, что делать?",
        "Какая сегодня погода в Париже? Трава зеленая копыта хвост."
    ]

    for phrase in test_phrases:
        raw_json = agent_intent_router(phrase)
        print(f"📥 Вход чата: '{phrase}'")
        print(f"   🚦 Вычисленный JSON маршрута: {raw_json}\n")
