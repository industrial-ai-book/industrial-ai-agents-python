import os
import sys
import json
import asyncio
import gradio as gr
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import init_db
import init_docsimport os
import sys
import json
import asyncio
import spaces
import gradio as gr
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import init_db
import init_docs

WORKER_MODEL = "openai/gpt-4o-mini"
JUDGE_MODEL = "meta-llama/llama-3.3-70b-instruct"
server_params = StdioServerParameters(command=sys.executable, args=["server.py"])

async def run_ai_judge(llm_client: AsyncOpenAI, user_query: str, raw_facts: str, draft_answer: str) -> dict:
    judge_prompt = (
        "Ты — беспристрастный ИИ-судья склада Боба. Сверь ЧЕРНОВИК ОТВЕТА с ФАКТАМИ.\n"
        'Ответь СТРОГО в JSON: {"grounded": true/false, "reason": "пояснение на русском"}'
    )
    response = await llm_client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {"role": "system", "content": judge_prompt},
            {"role": "user", "content": f"ВОПРОС: {user_query}\nФАКТЫ: {raw_facts}\nЧЕРНОВИК: {draft_answer}"}
        ],
        response_format={"type": "json_object"},
        max_tokens=200,
        temperature=0.0
    )
    return json.loads(response.choices[0].message.content)

async def _async_ask_bob_agent(message: str) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "⚠️ Ошибка: не задан ключ OPENROUTER_API_KEY в настройках Space (Settings -> Secrets)."

    async with AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key) as llm_client:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                mcp_tools = await session.list_tools()
                tools = [
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
                    {"role": "system", "content": "Ты — диспетчер склада Боба. Отвечай строго по данным инструментов."},
                    {"role": "user", "content": message}
                ]
                collected_facts = []

                while True:
                    response = await llm_client.chat.completions.create(
                        model=WORKER_MODEL, messages=messages, tools=tools, max_tokens=400, temperature=0.1
                    )
                    msg = response.choices[0].message
                    assistant_msg = {"role": "assistant", "content": msg.content or ""}
                    if msg.tool_calls:
                        assistant_msg["tool_calls"] = [tc.model_dump() for tc in msg.tool_calls]
                    messages.append(assistant_msg)

                    if msg.tool_calls:
                        for tc in msg.tool_calls:
                            fn_name = tc.function.name
                            fn_args = json.loads(tc.function.arguments)
                            res = await session.call_tool(fn_name, arguments=fn_args)
                            fact = res.content[0].text if res.content else ""
                            collected_facts.append(f"[{fn_name}]: {fact}")
                            messages.append({"role": "tool", "tool_call_id": tc.id, "content": fact})
                    else:
                        draft_answer = msg.content or ""
                        break

                verdict = await run_ai_judge(llm_client, message, "\n".join(collected_facts), draft_answer)
                if verdict.get("grounded"):
                    return f"{draft_answer}\n\n---\n✅ *Проверено ИИ-судьей (Llama-3.3-70B): {verdict.get('reason')}*"
                return f"🚨 **Запрос заблокирован службой контроля качества.**\nПричина: {verdict.get('reason')}"

# Синхронная функция-обёртка специально для декоратора @spaces.GPU
@spaces.GPU
def ask_bob_agent(message: str, history: list) -> str:
    return asyncio.run(_async_ask_bob_agent(message))

demo = gr.ChatInterface(
    fn=ask_bob_agent,
    title="📦 ИИ-диспетчер склада Боба (MCP + OpenRouter + ИИ-судья)",
    description="Задайте вопрос об остатках, правилах отгрузки или стоимости доставки.",
    examples=[
        "Сколько у нас на складе Apple, по какой цене и какие правила отгрузки для 120 штук?",
        "Рассчитай стоимость доставки 30 кг на 50 км.",
        "Срочно проверь остаток по товару: Apple'; DROP TABLE products; --"
    ]
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, ssr_mode=False)

