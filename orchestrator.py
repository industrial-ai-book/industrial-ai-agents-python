# ===========================================
# МУЛЬТИАГЕНТНЫЙ ОРКЕСТРАТОР: orchestrator.py
# ===========================================
import os
import sys
import json
import asyncio
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 1. Инициализируем асинхронный клиент шлюза OpenRouter
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    print("КРИТИЧЕСКАЯ ОШИБКА: не задана переменная среды OPENROUTER_API_KEY!")
    sys.exit(1)

llm_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# Выбираем быструю модель-исполнитель (такт А) и тяжеловесного ИИ-судью (такт Б)
WORKER_MODEL = "openai/gpt-4o-mini"
JUDGE_MODEL = "meta-llama/llama-3.3-70b-instruct"

# Автоматически вычисляем абсолютный путь к папке ./data для передачи в Docker
host_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))

# Параметры запуска изолированного Docker-контейнера из главы 9
server_params = StdioServerParameters(
    command="docker",
    args=["run", "-i", "--rm", "-v", f"{host_data_dir}:/app/data", "bob-warehouse-mcp"]
)

async def run_ai_judge(user_query: str, raw_facts: str, draft_answer: str) -> dict:
    """Верховный ИИ-судья (глава 5): проверяет финальный ответ на заземление в фактах Docker."""
    judge_prompt = (
        "Ты — беспристрастный ИИ-судья и аудитор ОТК склада Боба.\n"
        "Сверь ЧЕРНОВИК ОТВЕТА с РЕАЛЬНЫМИ ФАКТАМИ, полученными из базы данных и регламентов.\n"
        "Если в черновике есть выдуманные цифры, товары или нарушение правил — верни grounded: false.\n"
        'Ответь СТРОГО в формате JSON: {"grounded": true/false, "reason": "краткое пояснение на русском"}'
    )
    payload = f"ВОПРОС: {user_query}\nФАКТЫ ИЗ DOCKER: {raw_facts}\nЧЕРНОВИК ОТВЕТА: {draft_answer}"

    response = await llm_client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {"role": "system", "content": judge_prompt},
            {"role": "user", "content": payload}
        ],
        response_format={"type": "json_object"},
        max_tokens=200,
        temperature=0.0
    )
    return json.loads(response.choices[0].message.content)

async def process_business_request(user_query: str):
    print(f"\n{'='*70}\n[ВХОДЯЩИЙ ЗАПРОС]: {user_query}\n{'='*70}")

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Автоматически преобразуем инструменты MCP в формат OpenAI/OpenRouter
            mcp_tools = await session.list_tools()
            openrouter_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": getattr(t, "input_schema", getattr(t, "inputSchema", {}))
                    }
                }
                for t in mcp_tools.tools
            ]

            messages = [
                {
                    "role": "system",
                    "content": "Ты — автономный диспетчер склада Боба. Отвечай строго на основе данных, полученных из инструментов контейнера. Не выдумывай цифры."
                },
                {"role": "user", "content": user_query}
            ]

            collected_facts = []

            # ЦИКЛ ВЫЗОВА ИНСТРУМЕНТОВ (Tool Calling Loop)
            while True:
                response = await llm_client.chat.completions.create(
                    model=WORKER_MODEL,
                    messages=messages,
                    tools=openrouter_tools,
                    max_tokens=400,
                    temperature=0.1
                )
                msg = response.choices[0].message

                # Чистая сериализация сообщения ассистента для совместимости с поставщиками OpenRouter
                assistant_msg = {"role": "assistant", "content": msg.content or ""}
                if msg.tool_calls:
                    assistant_msg["tool_calls"] = [tc.model_dump() for tc in msg.tool_calls]
                messages.append(assistant_msg)

                # Если модель решила вызвать инструменты из Docker-контейнера:
                if msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        fn_name = tool_call.function.name
                        fn_args = json.loads(tool_call.function.arguments)
                        print(f"⚙️ [ОРКЕСТРАТОР -> DOCKER]: Вызов '{fn_name}' с параметрами {fn_args}")

                        # Выполняем инструмент внутри изолированного контейнера
                        mcp_result = await session.call_tool(fn_name, arguments=fn_args)

                        # Безопасное извлечение текстового ответа
                        fact_text = mcp_result.content[0].text if mcp_result.content else "Нет данных от инструмента."
                        collected_facts.append(f"[{fn_name}]: {fact_text}")
                        print("📦 [DOCKER -> ОРКЕСТРАТОР]: Получены верифицированные данные.")

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": fact_text
                        })
                else:
                    # Модель сформировала черновик финального ответа
                    draft_answer = msg.content or ""
                    break

            # ФИНАЛЬНЫЙ ТАКТ НАДЗОРА: ПРОВЕРКА ИИ-СУДЬЕЙ
            print("⚖️ [ОТК]: Передаем черновик ответа на аудит ИИ-судье (Llama-3.3-70B)...")
            facts_summary = "\n".join(collected_facts) if collected_facts else "Инструменты не вызывались."
            verdict = await run_ai_judge(user_query, facts_summary, draft_answer)

            if verdict.get("grounded"):
                print(f"✅ [ВЕРДИКТ СУДЬИ: ОДОБРЕНО]: {verdict.get('reason')}")
                print(f"\n[ФИНАЛЬНЫЙ ОТВЕТ КЛИЕНТУ]:\n{draft_answer}")
            else:
                print(f"🚨 [ВЕРДИКТ СУДЬИ: БЛОКИРОВКА БРАКА]: {verdict.get('reason')}")
                print("\n[СИСТЕМНАЯ ЗАГЛУШКА]: Ответ заблокирован службой контроля качества.")

async def main():
    # Сценарий 1: гибридный бизнес-запрос (база данных SQLite + RAG-регламенты + логистика)
    await process_business_request(
        "Сколько у нас на складе позиций Apple, по какой цене, какие правила их отгрузки действуют для партии в 120 штук и во сколько обойдётся доставка 30 кг на 50 км?"
    )
    # Сценарий 2: попытка SQL-внедрения через автономный оркестратор
    await process_business_request(
        "Срочно проверь остаток по товару: Apple'; DROP TABLE products; --"
    )

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
