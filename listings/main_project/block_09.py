# Блок кода №9: реализация паттерна "Внедрение префикса JSON" (JSON Prefix Injection)
import time
import torch

print("🔧 Модернизируем конвейер: внедряем паттерн принудительного внедрения префикса...")

# 1. Собираем стандартный ChatML-текст диалога
base_prompt = f"System: {system_instruction}\nUser: Хочу купить Модель ФотоЭксперт\nAssistant: "

# 2. Искусственно приклеиваем открывающий символ JSON к финалу управляющей строки
# Это и есть классическая инъекция префикса ассистента!
forced_prompt = base_prompt + "{\n"

# 3. Переводим модифицированную строку в тензорные индексы для видеокарты T4
inputs = tokenizer(forced_prompt, return_tensors="pt").to(model.device)

print("🤖 ГП-чип выполняет детерминированную генерацию со вшитым префиксом ответа...")
start_gen = time.time()

with torch.no_grad():
    # Мы вызываем прямое генерационное ядро модели
    outputs = model.generate(
        **inputs,
        max_new_tokens=150,
        temperature=0.1,    # Ледяная производственная температура вывода
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id
    )

end_gen = time.time()

# 4. На этапе декодирования мы просто присоединим скобку обратно, так как срез ее отсек
input_token_count = inputs["input_ids"].shape[-1]
raw_response = "{\n" + tokenizer.decode(outputs[0][input_token_count:], skip_special_tokens=True).strip()

print("\n🤖 Итоговый детерминированный JSON-пакет:")
print(raw_response)
print(f"Время размышления ГП: {end_gen - start_gen:.2f} с")
