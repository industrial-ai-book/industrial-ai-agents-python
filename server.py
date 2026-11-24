# =============================================================================
# ЕДИНЫЙ ПРОИЗВОДСТВЕННЫЙ СЕРВЕР: server.py (версия для развертывания в Docker)
# =============================================================================
import sys
import json
import logging
import sqlite3
from datetime import datetime, timezone
from mcp.server.mcpserver import MCPServer

# 1. НАСТРОЙКА ПРОИЗВОДСТВЕННОГО JSON-АУДИТА (LLMOps, см. главу 10)
class JsonAuditFormatter(logging.Formatter):
    """Форматирует системные события в строгий машиночитаемый JSON."""
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "bob-warehouse-mcp",
            "event": record.getMessage()
        }
        return json.dumps(log_record, ensure_ascii=False)

# Настраиваем двойной вывод: в поток stderr контейнера и в файл на смонтированном томе
logger = logging.getLogger("bob-warehouse-audit")
logger.setLevel(logging.INFO)

# Очищаем стандартные обработчики во избежание дублирования
if logger.hasHandlers():
    logger.handlers.clear()

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(JsonAuditFormatter())
logger.addHandler(stderr_handler)

# Подключаем запись в файл, только если смонтирована папка /app/data
try:
    file_handler = logging.FileHandler("/app/data/audit.log", encoding="utf-8")
    file_handler.setFormatter(JsonAuditFormatter())
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning(f"Не удалось открыть /app/data/audit.log (запуск вне Docker?): {e}")

# 2. ИНИЦИАЛИЗАЦИЯ ЯДРА MCP-СЕРВЕРА
server = MCPServer("bob-warehouse-connector")

# Пути к физическим данным внутри изолированной файловой системы контейнера
DB_PATH = "/app/data/warehouse.db"
DOCS_PATH = "/app/data/regulations.json"

# 3. ПАССИВНЫЙ СЛОЙ РЕСУРСОВ (перенесено из главы 7)
@server.resource("warehouse://schema")
async def get_warehouse_schema() -> str:
    """Пассивный DDL-код структуры таблиц продуктов и остатков склада."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
            # Извлекаем строковый элемент row[0] из кортежа
            schemas = [row[0] for row in cursor.fetchall() if row and row[0]]
            logger.info("Resource 'warehouse://schema' successfully read.")
            return "=== ЖИВАЯ СТРУКТУРА БАЗЫ ДАННЫХ СКЛАДА БОБА ===\n" + "\n".join(schemas)
    except Exception as e:
        logger.error(f"Database schema read error: {e}")
        return f"[ОШИБКА КОНТЕЙНЕРА] Не удалось прочитать схему: {e}"

# 4. ИНСТРУМЕНТ №1: защищенный поиск остатков в СУБД (адаптировано из главы 6)
@server.tool()
async def query_warehouse_production(product_name: str) -> str:
    """Поиск актуальных остатков и цен товаров в физической базе данных склада Боба."""
    # Упреждающий DevSecOps-фильтр против SQL-внедрений
    forbidden_tokens = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "--", ";"]
    if any(token in product_name.upper() for token in forbidden_tokens):
        logger.warning(f"SECURITY ALERT: SQL injection blocked -> '{product_name}'")
        return "[БЛОКИРОВКА ПЕРИМЕТРА] Обнаружено деструктивное ИИ-внедрение! Запрос отклонен."

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT product_name, category, price, stock_quantity FROM products WHERE product_name LIKE ?;",
                (f"%{product_name.strip()}%",)
            )
            result = cursor.fetchone()
            logger.info(f"SQLite query executed for product: '{product_name}'")

            if result:
                name, cat, price, qty = result
                return (
                    f"[Связь с базой данных установлена]\n"
                    f"Товар '{name}' (категория: {cat}) найден в базе данных Боба.\n"
                    f"Розничная цена: ${price}. Текущий остаток на стеллаже: {qty} шт."
                )
            return f"Товар по запросу '{product_name}' не найден в базе данных Боба."
    except Exception as e:
        logger.error(f"SQLite query execution error: {e}")
        return f"[ОШИБКА СУБД] Сбой выполнения транзакции: {e}"

# 5. ИНСТРУМЕНТ №2: поиск по корпоративным регламентам RAG (Адаптировано из Главы 4)
@server.tool()
async def search_regulations(query: str) -> str:
    """Поиск правил возврата, условий хранения и регламентов в базе знаний предприятия."""
    try:
        with open(DOCS_PATH, "r", encoding="utf-8") as f:
            regulations = json.load(f)

        query_words = set(query.lower().replace(",", "").replace(".", "").split())
        matched_docs = []

        for doc in regulations:
            keywords = set(k.lower() for k in doc.get("keywords", []))
            topic_words = set(doc.get("topic", "").lower().split())
            if query_words & (keywords | topic_words):
                matched_docs.append(f"[{doc['id']} — {doc['topic']}]: {doc['content']}")

        logger.info(f"RAG regulations search executed for query: '{query}' (matches: {len(matched_docs)})")

        if matched_docs:
            return "=== НАЙДЕННЫЕ КОРПОРАТИВНЫЕ РЕГЛАМЕНТЫ ===\n" + "\n\n".join(matched_docs)
        return "По вашему запросу точных совпадений в регламентах не найдено. Уточните ключевые слова (например: возврат, хранение, доставка)."
    except Exception as e:
        logger.error(f"RAG regulations read error: {e}")
        return f"[ОШИБКА RAG-МОДУЛЯ] Не удалось прочитать файл регламентов: {e}"

# 6. ИНСТРУМЕНТ №3: логистический калькулятор (перенесено из главы 7)
@server.tool()
async def calculate_delivery(weight_kg: float, distance_km: int) -> str:
    """Расчет стоимости доставки груза со склада на основе веса и расстояния."""
    if weight_kg <= 0 or distance_km <= 0:
        logger.warning(f"Invalid arguments for calculate_delivery: weight={weight_kg}, distance={distance_km}")
        return "[ОШИБКА АРГУМЕНТОВ] Вес и расстояние должны быть положительными числами!"

    base_price = 25.0
    total_cost = round(base_price + (weight_kg * 0.5) + (distance_km * 0.15), 2)
    logger.info(f"Delivery calculated: weight={weight_kg}kg, dist={distance_km}km -> ${total_cost}")
    return f"Расчет выполнен. Стоимость доставки груза весом {weight_kg} кг на расстояние {distance_km} км составляет ${total_cost}."

if __name__ == "__main__":
    logger.info("Starting production MCP server v2.x in stdio mode...")
    server.run()
