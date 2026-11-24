# Блок кода №30: интеграция асинхронного сетевого инструмента calculate_delivery на основе aiohttp
import aiohttp
import json
import mcp.types as types

print("=== 🚚 РАСШИРЕНИЕ СЛОЯ ИНСТРУМЕНТОВ: ИНТЕГРАЦИЯ КОНТУРА AIOHTTP ===")
print("⏳ Регистрируем асинхронный инструмент сетевой логистики calculate_delivery...")

async def handle_delivery_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """
    Принимает асинциированный RPC-запрос на расчет логистики,
    совершает неблокирующий HTTP-вызов к внешнему API и возвращает тариф.
    """
    if name == "query_warehouse":
        # Перенаправляем управление нашему базовому реляционному исполнителю из подраздела 7.4.1
        return await handle_call_tool(name, arguments)

    if name != "calculate_delivery":
        return [types.TextContent(type="text", text=json.dumps({"status": "REJECTED", "reason": f"Инструмент '{name}' не поддерживается сервером Боба!"}, ensure_ascii=False))]

    # Проверка достоверности контракта аргументов встроенными средствами Python
    if not arguments or "weight" not in arguments or "zone" not in arguments:
        return [types.TextContent(type="text", text=json.dumps({"status": "REJECTED", "reason": "Сбой синтаксического контракта: отсутствуют аргументы weight или zone!"}, ensure_ascii=False))]

    try:
        weight = float(arguments["weight"])
        zone = str(arguments["zone"]).strip()
    except (ValueError, TypeError):
        return [types.TextContent(type="text", text=json.dumps({"status": "REJECTED", "reason": "Сбой проверки достоверности типов: неверный формат веса или зоны!"}, ensure_ascii=False))]

    print(f"📡 [ЛОГИСТИКА] Запуск асинхронного тарификатора для веса {weight} кг, Зона: '{zone}'")

    # Эмулируем обращение к реальному удаленному логистическому API через асинхронный клиент aiohttp
    mock_api_url = "https://httpbin.org"

    try:
        async with aiohttp.ClientSession() as session:
            # Формируем тело полезной нагрузки для внешней службы доставки
            payload = {"cargo_weight": weight, "delivery_zone": zone, "partner_id": "BOB-WAREHOUSE-ID"}

            async with session.post(mock_api_url, json=payload, timeout=5) as response:
                if response.status != 200:
                    return [types.TextContent(type="text", text=json.dumps({"status": "API_ERROR", "reason": "Сбой внешней службы тарифов"}, ensure_ascii=False))]

                raw_response_text = await response.text()

                # Внутренняя детерминированная математика расчета стоимости логистики склада Боба
                base_rate = 10.0 if zone == "Зона 1" else (20.0 if zone == "Зона 2" else 35.0)
                final_cost = base_rate + (weight * 1.5)

                # Формируем и комментируем латинизированный JSON-манифест ответа
                logistics_verdict = {
                    "status": "SUCCESS",                               # Статус проведения асинхронной сетевой операции
                    "delivery_cost": final_cost,                       # Итоговая рассчитанная стоимость доставки груза Боба
                    "currency": "USD",                                 # Международный трехзначный буквенный код валюты расчета
                    "estimated_delivery": "24-48 часов",               # Расчетный временной интервал (окно) прибытия погрузчика
                    "infrastructure_marker": "Verified via aiohttp"    # Техническая метка использованного транспортного слоя
                }

                print(f"✨ [ЛОГИСТИКА] Стоимость успешно рассчитана: ${final_cost}")
                return [types.TextContent(type="text", text=json.dumps(logistics_verdict, indent=3, ensure_ascii=False))]

    except Exception as e:
        print(f"💥 Аварийный вылет сетевого контура aiohttp: {e}")
        return [types.TextContent(type="text", text=json.dumps({"status": "NETWORK_ERROR", "reason": str(e)}, ensure_ascii=False))]

# Явно переназначаем ссылки на функции в объекте сервера, расширяя контур
server.call_tool = handle_call_tool

print("✨ Инструмент calculate_delivery успешно интегрирован в асинхронный монолит сервера.")
