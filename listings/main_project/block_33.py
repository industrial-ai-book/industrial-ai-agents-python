# Блок кода №33: производственная инициализация сетевого шлюза на чистом Python
import os
import sys
import time
print("=== ЗАПУСК СЕТЕВОГО ШЛЮЗА НА ЧИСТОМ PYTHON ===")

ngrok_token = None
# Эшелон 1: извлекаем маркер из панели секретов Google Colab
try:
    from google.colab import userdata
    ngrok_token = userdata.get('NGROK_AUTHTOKEN')
    print("СЕКРЕТНЫЙ КОНТУР: маркер NGROK_AUTHTOKEN успешно извлечен из панели секретов.")
except Exception:
    # Эшелон 2: резервный шлюз при отсутствии перезапуска сеанса ядра
    print("УВЕДОМЛЕНИЕ: ключ не найден в активном реестре ядра.")
    ngrok_token = input("Введите ваш маркер из личного кабинета ngrok: ").strip()
if not ngrok_token:
    print("\nКРИТИЧЕСКАЯ АВАРИЯ DEVSECOPS: введен пустой маркер!")
    sys.exit()
print("\nИнтегрируем собственный Python-транспорт и расширенные MCP-компоненты...")

# Обеспечиваем установку pyngrok, актуального mcp v2.x и веб-сервера uvicorn
!pip install pyngrok "mcp>=2.0.0" fastapi uvicorn --quiet --no-warn-conflicts
from pyngrok import ngrok, conf

# Помещаем маркер прямо в конфигурацию среды выполнения
conf.get_default().auth_token = ngrok_token
print("Активируем собственный неблокирующий TLS-туннель на порту 8000...")
try:
    # Очищаем ОЗУ от возможных зависших сокетов прошлых сеансов
    ngrok.kill()
    time.sleep(1)
    # Поднимаем высокоскоростной защищенный HTTP-туннель
    http_tunnel = ngrok.connect(8000, "http")
    public_url = http_tunnel.public_url
    if public_url:
        print("\n" + "="*70)
        print("СЕТЕВОЙ МОСТ УСПЕШНО РАЗВЕРНУТ В ГЛОБАЛЬНОЙ СЕТИ!")
        print(f"Публичный веб-адрес для Claude Desktop: {public_url}")
        print("="*70)
        print("Важно! Скопируйте этот адрес целиком. Он понадобится позже.")
except Exception as e:
    print(f"\nКРИТИЧЕСКАЯ АВАРИЯ СЕТЕВОГО КОНТУРА: {e}")
