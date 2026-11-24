# Блок кода №3: демонстрационный запуск классического чат-бота
import time
import torch
from transformers import AutoModelForCausalLM

print("=== ЗАПУСК КЛАССИЧЕСКОГО ЧАТ-БОТА В GOOGLE COLAB ===")
print("Шаг 1. Загрузка цифрового ядра модели во внешнюю память...")
start_load = time.time()

# Модель и токенизатор используют общий идентификатор model_id
model_id = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

# Инициализируем модель в формате половинной точности
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

end_load = time.time()
print(f"Компоненты успешно загружены в VRAM за {end_load - start_load:.2f} с")
print(f"Активный вычислительный чип: {model.device}\n")

# Хаотичный, смешанный запрос клиента Боба без системной роли
chatbot_prompt = """Привет! Мне нужен смартфон, чтобы снимать качественные фото и видео для блога.
Бюджет свободный. Или постой, подожди, у меня еще старый телефон разряжается за два часа со 100% до нуля,
что мне делать с батареей? И сколько у вас стоит модель ФотоЭксперт в долларах?"""

print(f"[Журнал работы] Входной запрос клиента:\n{chatbot_prompt}\n")
print("Запуск генерации ответа...")

# Проводим токенизацию строки через переменную, созданную в блоке кода №2
inputs = tokenizer(chatbot_prompt, return_tensors="pt").to(model.device)
start_gen = time.time()

with torch.no_grad():
    # Распаковываем словарь **inputs, передавая и input_ids, и attention_mask
    # Это гарантирует стабильную генерацию без немых сбоев на ГП
    outputs = model.generate(
        **inputs,
        max_new_tokens=150,
        temperature=0.7,    # Повышенный хаос для обычного чат-бота
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id
    )

end_gen = time.time()

# Извлекаем только сгенерированные токены ответа
input_token_count = inputs["input_ids"].shape[-1]
new_tokens = outputs[0][input_token_count:]
response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

print("\n=== ОТВЕТ КЛАССИЧЕСКОГО ЧАТ-БОТА ===")
print(response)
print("=" * 36)
print(f"Время генерации: {end_gen - start_gen:.2f} с")
print(f"Сгенерировано дискретных единиц текста (токенов): {len(new_tokens)}")
