import sys
import json
import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = str(DATA_DIR / "warehouse.db")
DOCS_PATH = str(DATA_DIR / "regulations.json")
LOG_PATH = str(DATA_DIR / "audit.log")

class JsonAuditFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "bob-warehouse-mcp",
            "event": record.getMessage()
        }, ensure_ascii=False)

logger = logging.getLogger("bob-warehouse-audit")
logger.setLevel(logging.INFO)
if logger.hasHandlers():
    logger.handlers.clear()

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(JsonAuditFormatter())
logger.addHandler(stderr_handler)

try:
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(JsonAuditFormatter())
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning(f"Log file error: {e}")

server = FastMCP("bob-warehouse-connector")

@server.resource("warehouse://schema")
async def get_warehouse_schema() -> str:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
            schemas = [row[0] for row in cursor.fetchall() if row and row[0]]
            return "=== СТРУКТУРА БД СКЛАДА БОБА ===\n" + "\n".join(schemas)
    except Exception as e:
        return f"[ОШИБКА] Не удалось прочитать схему: {e}"

@server.tool()
async def query_warehouse_production(product_name: str) -> str:
    forbidden_tokens = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "--", ";"]
    if any(token in product_name.upper() for token in forbidden_tokens):
        logger.warning(f"SECURITY ALERT: SQL injection blocked -> '{product_name}'")
        return "[БЛОКИРОВКА ПЕРИМЕТРА] Обнаружена деструктивная ИИ-инъекция! Запрос отклонён."

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
                    f"Товар '{name}' (категория: {cat}) найден в физической СУБД склада Боба.\n"
                    f"Розничная цена: ${price}. Текущий остаток на стеллаже: {qty} шт."
                )
            return f"Товар по запросу '{product_name}' не найден в физической базе данных Боба."
    except Exception as e:
        return f"[ОШИБКА СУБД] Сбой выполнения транзакции: {e}"

@server.tool()
async def search_regulations(query: str) -> str:
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
        logger.info(f"RAG search executed for: '{query}' (matches: {len(matched_docs)})")
        if matched_docs:
            return "=== НАЙДЕННЫЕ КОРПОРАТИВНЫЕ РЕГЛАМЕНТЫ ===\n" + "\n\n".join(matched_docs)
        return "По вашему запросу точных совпадений в регламентах не найдено."
    except Exception as e:
        return f"[ОШИБКА RAG-МОДУЛЯ] Не удалось прочитать регламенты: {e}"

@server.tool()
async def calculate_delivery(weight_kg: float, distance_km: int) -> str:
    if weight_kg <= 0 or distance_km <= 0:
        return "[ОШИБКА АРГУМЕНТОВ] Вес и расстояние должны быть положительными числами!"
    total_cost = round(25.0 + (weight_kg * 0.5) + (distance_km * 0.15), 2)
    logger.info(f"Delivery calculated: weight={weight_kg}kg, dist={distance_km}km -> ${total_cost}")
    return f"Расчет выполнен. Стоимость доставки груза весом {weight_kg} кг на расстояние {distance_km} км составляет ${total_cost}."

if __name__ == "__main__":
    logger.info("Starting production MCP server in stdio mode...")
    server.run()
