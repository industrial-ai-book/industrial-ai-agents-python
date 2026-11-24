# Блок кода №31: финализированная интеграция слоя инструментов, слоя шаблонов и упреждающей фильтрации аргументов
import json
import asyncio
import mcp.types as types

print("=== 🛠️ КОМПИЛЯЦИЯ ПРОИЗВОДСТВЕННОГО КОНТУРА ОБРАБОТКИ RPC-КОМАНД ===")
print("⏳ Интегрируем слой шаблонов инструкций и упреждающие защитные конструкции...")

# ==============================================================================
# 🐳 КИТ №3: СЛОЙ ШАБЛОНОВ ИНСТРУКЦИЙ (PROMPTS)
# ==============================================================================

async def handle_list_prompts() -> list[types.Prompt]:
    """Автоматически регистрирует в журнале и передает клиенту список шаблонов инструкций."""
    print("📡 [СИГНАЛ MCP] Получен RPC-запрос на листинг шаблонов инструкций (list_prompts).")
    return [
        types.Prompt(
            name="warehouse_compliance_report",
            description="Должностная инструкция для генерации регламентных отчетов по складским остаткам Боба.",
            arguments=[
                types.PromptArgument(
                    name="reporter_role",
                    description="Официальная ролевая модель аудитора (например, Главный Аналитик).",
                    required=True
                )
            ]
        )
    ]

async def handle_get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    """Динамически формирует системный регламент поведения для удаленного ИИ."""
    print(f"📡 [СИГНАЛ MCP] Поступила команда на извлечение шаблона инструкций: '{name}'")

    if name != "warehouse_compliance_report":
        return types.GetPromptResult(
            description="Ошибка: Запрошенный шаблон отсутствует на сервере Боба!",
            messages=[]
        )

    role = arguments.get("reporter_role", "Аудитор") if arguments else "Аудитор"
    compliance_instruction = (
        f"Вы выступаете в строгой роли: {role}.\n"
        f"При анализе данных СУБД, извлеченных через инструмент query_warehouse, "
        f"вы обязаны соблюдать жесткий корпоративный этикет склада Боба.\n"
        f"Запрещено разглашать внутреннюю структуру таблиц (DDL) конечным пользователям."
    )

    return types.GetPromptResult(
        description="Регламентный системный контекст безопасности",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=compliance_instruction)
            )
        ]
    )

# ==============================================================================
# 🐳 ОБНОВЛЕННЫЙ СЛОЙ ВЫПОЛНЕНИЯ ИНСТРУМЕНТОВ С ФИЛЬТРАЦИЕЙ АРГУМЕНТОВ
# ==============================================================================

async def handle_call_tool(
    name: str,
    arguments: dict | None
) -> list[types.TextContent]:
    """Центральный асинхронный диспетчер выполнения инструментов коннектора."""
    print(f"\n📥 [ВХОДЯЩИЙ RPC-СИГНАЛ] Ведение журнала: Поступил запрос на вызов: '{name}'")

    if name == "calculate_delivery":
        # Перенаправляем управление нашему логистическому асинхронному шлюзу из Блока кода №29
        return await handle_delivery_tool(name, arguments)

    if name != "query_warehouse":
        return [types.TextContent(type="text", text=json.dumps({"status": "REJECTED", "reason": f"Инструмент '{name}' отсутствует на сервере!"}, ensure_ascii=False))]

    # --- УПРЕЖДАЮЩАЯ ЗАЩИТА ПЕРИМЕТРА (GUARD CLAUSES) ---
    if not arguments or "user_request" not in arguments:
        return [types.TextContent(type="text", text=json.dumps({"status": "REJECTED", "reason": "Сбой контракта: отсутствует аргумент 'user_request'!"}, ensure_ascii=False))]

    client_query = str(arguments["user_request"]).strip()

    # Верификация длины строки: отсекаем пустые запросы и DOS-атаки экстремального объёма
    if len(client_query) == 0:
        return [types.TextContent(type="text", text=json.dumps({"status": "REJECTED", "reason": "Упреждающий фильтр: Запрещен пустой поисковый сигнал!"}, ensure_ascii=False))]

    if len(client_query) > 500:
        return [types.TextContent(type="text", text=json.dumps({"status": "REJECTED", "reason": "Упреждающий фильтр: Длина запроса превышает лимит 500 символов!"}, ensure_ascii=False))]

    print(f"🛡️ Периметр чист. Передаем сигнал '{client_query}' безопасному исполнителю СУБД...")
    try:
        loop = asyncio.get_running_loop()
        execution_verdict = await loop.run_in_executor(
            None,
            warehouse_pipeline.execute_agent_transaction,
            client_query
        )

        # Фиксируем транзакцию в системном журнале
        print(f"🏆 Регистрация транзакции завершена. Статус: {execution_verdict.get('status')}")

        # Смысл полей структуры:
        # - status: инфраструктурный статус прохождения эшелонов защиты (SUCCESS / BLOCKED)
        # - payload: двумерный массив строк, извлеченных из ОЗУ базы данных SQLite
        # - reason: четкое текстовое обоснование вердикта для инспекции ОТК
        formatted_response_text = json.dumps({
            "status": execution_verdict.get("status"),
            "payload": execution_verdict.get("payload", []),
            "reason": "Транзакция успешно верифицирована на соответствие источнику данных в СУБД SQLite." if execution_verdict.get("status") == "SUCCESS" else execution_verdict.get("reason")
        }, indent=3, ensure_ascii=False)

        return [types.TextContent(type="text", text=formatted_response_text)]

    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"status": "CRITICAL_ERROR", "reason": str(e)}, ensure_ascii=False))]

# Явно переназначаем ссылки на функции в объекте сервера
server.list_prompts = handle_list_prompts
server.get_prompt = handle_get_prompt
server.call_tool = handle_call_tool

print("✨ Все три слоя протокола MCP успешно интегрированы и защищены.")
