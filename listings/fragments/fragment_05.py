import json
from openai import OpenAI

# Безопасно извлекаем API-ключ OpenRouter из секретов среды Google Colab
try:
    from google.colab import userdata
    openrouter_key = userdata.get('OPENROUTER_API_KEY')
except ImportError:
    openrouter_key = None

# Инициализируем клиент с заголовками одобренного агентского приложения
client = OpenAI(
    api_key=openrouter_key if openrouter_key else "YOUR_OPENROUTER_API_KEY",
    base_url="https://openrouter.ai/api/v1"
)

try:
    print("Отправка запроса к anthropic/claude-5.5-sonnet...")

    response = client.chat.completions.create(
        model="anthropic/claude-5.5-sonnet",
        messages=[
            {"role": "user", "content": "Привет! Каковы твои главные преимущества?"}
        ],
        temperature=0.7,
        max_tokens=200    # Ограничение буфера для успешного прохождения лимитов OpenRouter
    )

    print("\nОтвет от anthropic/claude-5.5-sonnet:")
    print(response.choices[0].message.content)

except Exception as e:
    print(f"\nОшибка при вызове модели: {e}")
