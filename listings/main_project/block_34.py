# Блок кода №34: создание и запуск сетевого MCP-сервера склада на базе стандарта v2.x
import os
import sys
import logging
from mcp.server.mcpserver import MCPServer

print("=== ЗАПУСК СЕТЕВОГО ТРАНСПОРТА MCP V2 И ПЕРЕВОД СЕРВЕРА В АКТИВНЫЙ РЕЖИМ ===")
logging.basicConfig(level=logging.INFO)

# Инициализируем сетевой MCPServer v2.x
mcp_net = MCPServer("bob-warehouse-connector")

# Регистрируем пассивный слой ресурсов СУБД SQLite для сетевого доступа
@mcp_net.resource("warehouse://schema")
async def get_warehouse_schema() -> str:
    """Пассивный DDL-код структуры таблиц товаров и заказов склада."""
    return """=== ЭТАЛОННАЯ СТРУКТУРА РЕЛЯЦИОННОЙ ПАМЯТИ СКЛАДА БОБА ===

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock_quantity INTEGER NOT NULL,
    warehouse_slot TEXT NOT NULL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    customer_name TEXT NOT NULL,
    quantity_ordered INTEGER NOT NULL,
    order_timestamp TEXT NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(id)
);

Правило для ИИ: При конструировании запросов опирайтесь строго на эти имена колонок!"""

# Регистрируем инструмент выполнения запросов с интеграцией защиты
@mcp_net.tool()
async def query_warehouse(user_request: str) -> str:
    """Сетевой инструмент выполнения запросов к складу Боба."""
    if "DROP" in user_request.upper() or "DELETE" in user_request.upper():
        return "[БЛОКИРОВКА ПЕРИМЕТРА] Обнаружена деструктивная ИИ-инъекция! Запрос отклонен."
    return f"Сетевой запрос '{user_request}' принят коннектором склада Боба."

# Генерируем готовое веб-приложение SSE средствами стандарта MCP v2.x
app = mcp_net.sse_app()
print("\nДиспетчеризация конвейера. Коннектор переводится в режим ожидания сетевых JSON-RPC транзакций...")
print("Внимание: ячейка перейдет в режим бесконечного фонового прослушивания сокета (порт 8000).")
print("НЕ ОСТАНАВЛИВАЙТЕ выполнение этой ячейки! Она должна оставаться активной")
print("во время попытки подключения Claude Desktop на вашем локальном компьютере.")

# Интегрируем поддержку вложенных циклов событий
!pip install nest_asyncio --quiet
import nest_asyncio
nest_asyncio.apply()
import uvicorn

# Запускаем асинхронный веб-сервер uvicorn на локальном порту 8000
config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="info")
server_instance = uvicorn.Server(config)

# Бесшовно запускаем сервер внутри текущего работающего цикла блокнота
await server_instance.serve()
