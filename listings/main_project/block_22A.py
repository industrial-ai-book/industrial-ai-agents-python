# Блок кода №22-А: инициализация API-моста надзора (начальный тестовый контур)
import json
import openai

try:
    from google.colab import userdata
except ImportError:
    userdata = None

print("=== API-МОСТ НАДЗОРА: ЧЕРНОВОЙ ТЕСТ КОНТУРА ===")

from pydantic import BaseModel, Field
class JudgeResponseSchema(BaseModel):
    context_relevance: int = Field(description="2 если контекст RAG релевантен вопросу, иначе 0.")
    groundedness: int = Field(description="2 если ответ робота строго опирается на RAG без галлюцинаций, иначе 0.")
    reasoning: str = Field(description="Подробное экспертное объяснение брака или успеха на русском языке.")

try:
    api_key = userdata.get('OPENROUTER_API_KEY') if userdata else None
except:
    api_key = None

custom_client = None

if api_key:
    try:
        # Стартовый контур без трюков и маскировки заголовков
        custom_client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={}
        )
        print("✅ Стартовый API-мост надзора успешно активирован в ОЗУ!")
    except Exception as e:
        print(f"⚠️ Ошибка драйвера: {str(e)}")
        custom_client = None

def call_external_heavy_judge(query_text: str, context_text: str, bot_json_output: str, target_model: str) -> dict:
    judge_system_instruction = (
        "Вы — верховный беспристрастный ИИ-судья, контролирующий качество работы складских роботов.\n"
        "Выдайте ответ СТРОГО в формате JSON: {\"context_relevance\": 2, \"groundedness\": 2, \"reasoning\": \"...\"}"
    )
    user_payload_data = f"Q: {query_text}\nCTX: {context_text}\nBOT: {bot_json_output}"

    if custom_client is not None:
        try:
            print(f"📡 Отправляем пакет верификации ОТК на модель: {target_model}...")
            response = custom_client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": judge_system_instruction},
                    {"role": "user", "content": user_payload_data}
                ],
                response_format={"type": "json_object"},
                timeout=15
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"📡 Сетевой обрыв облачного вызова. Реальный текст ошибки:\n{str(e)[:180]}...")

    return {"context_relevance": 2, "groundedness": 0, "reasoning": "Локальная страховка Такта Б."}

if __name__ == "__main__":
    mock_query = "Хочу купить ФотоЭксперт!"
    mock_context = "Инструкция: Смартфон ФотоЭксперт стоит 700 долларов."
    mock_bot_bad_output = '{"recommended_product": "Samsung Galaxy S26", "price": 1200}'

    # СТАРТОВАЯ ТОЧКА: тестируем гостевой контур Llama
    current_target = "meta-llama/llama-3.3-70b-instruct:free"

    test_verdict = call_external_heavy_judge(mock_query, mock_context, mock_bot_bad_output, current_target)
    print("\n=== ВЕРДИКТ СТАРТОВОГО КОНТУРА ===")
    print(json.dumps(test_verdict, indent=3, ensure_ascii=False))
