# Блок кода №28: создание асинхронного MCP-сервера WarehouseMCPServer с интеграцией слоя ресурсов
import asyncio
import sys
import json
import sqlite3
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types

print("=== 🔌 ИНИЦИАЛИЗАЦИЯ ПРОИЗВОДСТВЕННОГО ЯДРА MCP-СЕРВЕРА СЛОЯ РЕСУРСОВ ===")
print("⏳ Компилируем асинхронный StdioServerTransport и пассивные URI...")

# 1. Инициализируем базовый экземпляр сервера
server = Server("WarehouseMCPServer")

# Интегруем наш безопасный исполнитель базы данных из главы 6
try:
    warehouse_pipeline = SecureSQLPipeline(db_connection)
    print("✨ Семантическая броня SecureSQLPipeline успешно припаяна к ядру сервера.")
except NameError:
    print("❌ КРИТИЧЕСКАЯ АВАРИЯ: Объект db_connection или класс SecureSQLPipeline не найдены в ОЗУ!")

# ==============================================================================
# 🐳 КИТ №1: СЛОЙ ПАССИВНЫХ РЕСУРСОВ (RESOURCES)
# ==============================================================================

async def handle_list_resources() -> list[types.Resource]:
    """Автоматически сообщает удаленному MCP-клиенту список доступных текстовых ресурсов."""
    print("📡 [СИГНАЛ MCP] Получен RPC-запрос на листинг ресурсов (list_resources).")
    return [
        types.Resource(
            uri="warehouse://schema",
            name="Схема реляционных таблиц склада Боба",
            description="Текстовое DDL-описание структуры колонок, типов данных и связей таблиц products и orders в ОЗУ.",
            mimeType="text/plain"
        )
    ]

async def handle_read_resource(uri: str) -> str:
    """Динамически извлекает из системного каталога базы данных SQLite актуальную DDL-структуру таблиц."""
    print(f"📡 [СИГНАЛ MCP] Поступила команда на чтение ресурса по URI: '{uri}'")
    if uri != "warehouse://schema":
        raise ValueError(f"Запрошенный ресурс по адресу '{uri}' отсутствует на сервере Боба!")
    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name IN ('products', 'orders');")
        rows = cursor.fetchall()
        ddl_schemas = [row[0] for row in rows if row and row[0]]
        resource_payload = (
            "=== ЭТАЛОННАЯ СТРУКТУРА РЕЛЯЦИОННОЙ ПАМЯТИ СКЛАДА БОБА ===\n\n" +
            "\n\n".join(ddl_schemas) +
            "\n\nПравило для ИИ: При конструировании запросов опирайтесь строго на эти имена колонок!"
        )
        return resource_payload
    except Exception as e:
        return f"Критический сбой СУБД при синтаксическом анализе метаданных: {e}"

# ==============================================================================
# 🐳 КИТ №2: СЛОЙ ИНСТРУМЕНТОВ (TOOLS)
# ==============================================================================

async def handle_list_tools() -> list[types.Tool]:
    """Передает удаленному MCP-клиенту жесткий манифест наших активных инструментов."""
    print("📡 [СИГНАЛ MCP] Получен RPC-запрос на предоставление манифеста инструментов (list_tools).")
    return [
        types.Tool(
            name="query_warehouse",
            description=(
                "Универсальный безопасный инструмент для поиска товаров, проверки цен и "
                "складских остатков на предприятии Боба. На вход принимает живой язык клиента."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "user_request": {"type": "string", "description": "Текст входящего вопроса покупателя на русском языке."}
                },
                "required": ["user_request"]
            }
        ),
        types.Tool(
            name="calculate_delivery",
            description="Асинхронный инструмент сетевой логистики для расчета стоимости грузоперевозок.",
            inputSchema={
                "type": "object",
                "properties": {
                    "weight": {"type": "number", "description": "Вес груза в килограммах."},
                    "zone": {"type": "string", "description": "Тарифная зона доставки."}
                },
                "required": ["weight", "zone"]
            }
        )
    ]

# Явно привязываем функции к внутреннему реестру обработчиков сервера по спецификации SDK
server.list_resources = handle_list_resources
server.read_resource = handle_read_resource
server.list_tools = handle_list_tools

print("✨ Асинхронный сервер со слоем ресурсов успешно скомпилирован.")
