# ==========================================
# ФАЙЛ МОСТА: C:\mcp_project\mcp_bridge.py
# ==========================================
import os
import sys
import asyncio
import logging
from mcp.client.sse import sse_client

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Направляем диагностические журналы в stderr, чтобы не нарушать JSON-RPC в stdout
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("mcp_bridge")

tunnel_url = os.environ.get("NGROK_TUNNEL_URL", "").strip("/")

async def bridge_logic():
    if not tunnel_url:
        logger.error("КРИТИЧЕСКАЯ ОШИБКА: переменная NGROK_TUNNEL_URL не установлена!")
        sys.exit(1)

    logger.info(f"Запуск моста. Подключение к удаленному SSE: {tunnel_url}/sse")
    
    # 1. Устанавливаем сетевое соединение с сервером в Google Colab
    async with sse_client(f"{tunnel_url}/sse") as (sse_read, sse_write):
        logger.info("Сетевой канал SSE с облаком установлен.")
        
        # 2. Подключаемся к стандартному вводу (stdin) от Claude Desktop
        loop = asyncio.get_running_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        
        async def forward_to_sse():
            while True:
                line = await reader.readline()
                if not line:
                    break
                # Пересылаем низкоуровневый запрос JSON-RPC от Claude в облако
                await sse_write.send(line.decode('utf-8'))
                
        async def forward_to_stdio():
            async for message in sse_read:
                # Преобразуем входящий объект ответа в строку для stdout в Claude
                raw_data = message.json() if hasattr(message, "json") else str(message)
                sys.stdout.write(raw_data + "\n")
                sys.stdout.flush()
                
        # Запускаем параллельную двунаправленную пересылку пакетов
        await asyncio.gather(forward_to_sse(), forward_to_stdio())

if __name__ == "__main__":
    try:
        asyncio.run(bridge_logic())
    except Exception as e:
        logger.error(f"Авария сетевого моста: {e}", exc_info=True)
        sys.exit(1)
