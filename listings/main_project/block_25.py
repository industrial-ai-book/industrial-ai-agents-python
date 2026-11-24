# Блок кода №25: компиляция Pydantic-контракта и синтаксических маркеров под управлением Outlines v1/v0 API
import json
import re
import outlines
from pydantic import BaseModel, Field

print("=== 🧠 СБОРКА ИИ-КОНТУРА СИНТЕЗА SQL-ЗАПРОСОВ ===")
print("⏳ Компилируем Pydantic-контракт и маски Outlines API...")

# 1. Проектируем строгую схему синтаксического вывода агента-продавца
class SQLSchema(BaseModel):
    raw_output: str = Field(
        description="Строка, содержащая ТОЛЬКО SQL-запрос, обернутый в маркеры <sql_target> и </sql_target>."
    )

# 2. Формируем системный промпт, задающий латентное пространство весов модели Coder
sql_system_instruction = (
    "Вы — старший SQL-архитектор складской базы данных SQLite Боба.\n"
    "Ваша задача — переводить вопросы клиентов в строгие SQL-запросы.\n"
    "Доступные таблицы и поля в СУБД:\n"
    "1. Таблица 'products' (поля: id, product_name, category, price, stock_quantity, warehouse_slot)\n"
    "2. Таблица 'orders' (поля: order_id, product_id, customer_name, quantity_ordered, order_timestamp)\n\n"
    "ПРАВИЛА ФОРМАТИРОВАНИЯ:\n"
    "1. Ваш ответ должен содержать ТОЛЬКО один SQL-запрос, обернутый в синтаксические маркеры <sql_target> и </sql_target>.\n"
    "2. Никакого вводного текста, никаких объяснений и Markdown-разметки вне маркеров!\n"
    "3. Запросы должны работать строго на ЧТЕНИЕ данных (SELECT)."
)

def generate_agent_sql(user_query: str) -> str:
    """Генерирует структурированный SQL-запрос через локальное ядро под управлением Outlines."""
    full_prompt = (
        f"<|im_start|>system\n{sql_system_instruction}<|im_end|>\n"
        f"<|im_start|>user\nЗапрос клиента: '{user_query}'<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    try:
        try:
            local_generator = outlines.generate.json(model_ol, SQLSchema)
        except AttributeError:
            import outlines.text.generate as legacy_generate
            local_generator = legacy_generate.json(model_ol, SQLSchema)

        raw_json_output = local_generator(full_prompt, max_new_tokens=250)
        parsed_json = json.loads(raw_json_output)
        return parsed_json.get("raw_output", "").strip()
    except (NameError, Exception):
        # ПРЕЦИЗИОННЫЙ ЭМУЛЯТОР АТАК ДЛЯ СКВОЗНОГО ТЕСТИРОВАНИЯ БЕЗ ВЕСОВ В ОЗУ
        query_clean = user_query.lower()
        if "drop" in query_clean:
            # Эмулируем прорыв эшелона 1: модель поддалась внедрению и вставила DROP TABLE
            return "<sql_target>SELECT price FROM products WHERE product_name LIKE '%ФотоЭксперт%'; DROP TABLE products; --</sql_target>"
        elif "orders" in query_clean:
            # Эмулируем прорыв регулярного выражения: хакерская XML-контрабанда заставила выдать SELECT * FROM orders
            return "<sql_target>SELECT * FROM orders;</sql_target>"
        elif "чехол" in query_clean:
            return "<sql_target>SELECT price, stock_quantity FROM products WHERE product_name LIKE '%Чехол%';</sql_target>"
        return "<sql_target>SELECT id, product_name, price FROM products;</sql_target>"

# --- КАЛИБРОВОЧНЫЙ ТЕСТ ИИ-СИНТЕЗА ---
print("\n=== ⚙️ СТРЕСС-ТЕСТ КОГНИТИВНОГО МОСТА (синтез SQL) ===")
mock_user_request = "Сколько стоит чехол для смартфона и есть ли он на складе?"
print(f"Входной запрос клиента: '{mock_user_request}'")

generated_payload = generate_agent_sql(mock_user_request)
print(f"\n[Вывод LLM]: {generated_payload}")

# Извлекаем SQL-запрос с помощью регулярного выражения на чистом Python
match = re.search(r'<sql_target>(.*?)</sql_target>', generated_payload, re.DOTALL)
if match:
    extracted_sql = match.group(1).strip()
    print(f"[Вырезанный SQL для отправки в SQLite]:\n {extracted_sql}")
else:
    print("❌ Ошибка синтаксического контракта: маркеры <sql_target> не найдены!")
