# Блок кода №5: запуск сквозного ИИ-агента в режиме управляемого контекста
import time
import torch

# 1. Задаем системную инструкцию (цифровая конституция агента)
system_instruction = """Ты — изолированный производственный ИИ-агент магазина Боба.
Ты работаешь строго в двух режимах:
1. ТЕХПОДДЕРЖКА: Если у клиента проблема, выдай один короткий ремонтный шаг (до 2 предложений).
2. ПОДБОР ТЕХНИКИ: Если клиент ищет смартфон, предложи модель строго из каталога:
   - Нужна камера/линза -> рекомендуй "Модель ФотоЭксперт" (цена $700).
   - Нужно много памяти/хранилища -> рекомендуй "Модель МегаХранилище 1 Тбайт" (цена $500).
Отвечай лаконично, вежливо и строго в долларах ($)."""

# 2. Массив реальных хаотичных запросов клиентов с разным контекстом
customer_requests = [
    "Мой новый телефон разряжается со 100% до нуля буквально за два часа, что мне делать?",
    "Здравствуйте! Мне нужен смартфон, чтобы снимать качественные фото и видео для блога. Бюджет свободный.",
    "Привет! Ищу надежный аппарат, чтобы закачать туда терабайты сериалов и музыки в дорогу. Что посоветуете?"
]

total_tokens_generated = 0
global_start_time = time.time()

print("=== ЗАПУСК СКВОЗНОГО КОНВЕЙЕРА ОБРАБОТКИ ЗАПРОСОВ ===")

# 3. Основной циклический контур работы агента
for idx, user_query in enumerate(customer_requests, 1):
    print(f"\n[Входящий поток] Обработка запроса №{idx}: '{user_query}'")

    # Формируем диалоговую разметку ролей по стандарту ChatML
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_query}
    ]

    # Применяем шаблон разметки и токенизируем текст
    formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)

    start_gen = time.time()
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs.get("attention_mask"),
            max_new_tokens=100,
            temperature=0.1,     # Замораживаем хаос для идеальной точности вывода
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    end_gen = time.time()

    # Извлекаем только вновь сгенерированные дискретные единицы текста
    input_token_count = inputs["input_ids"].shape[-1]
    new_tokens = outputs[0][input_token_count:]
    total_tokens_generated += len(new_tokens)

    # Декодируем числа обратно в понятные человеку слова
    response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    print("  [Вердикт агента]:")
    print(f"  [{response}]")
    print(f"  Время размышления: {end_gen - start_gen:.2f} с")

global_end_time = time.time()
total_time = global_end_time - global_start_time
avg_speed = total_tokens_generated / total_time if total_time > 0 else 0

# 4. Вывод сводного отчета для финансового отдела Боба
print("\n" + "="*60)
print("  СВОДНЫЙ МОНИТОРИНГ РАБОТЫ ЦИФРОВОГО ОТДЕЛА ПОДДЕРЖКИ БОБА")
print("="*60)
print(f"  Успешно обработано обращений клиентов: {len(customer_requests)}")
print(f"  Суммарно сгенерировано токенов ответа: {total_tokens_generated}")
print(f"  Общее время работы конвейера в ОЗУ:    {total_time:.2f} с")
print(f"  Средняя скорость мышления ИИ-агента:   {avg_speed:.2f} токенов/с")
print("="*60)
