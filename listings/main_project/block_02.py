# Блок кода №2: инициализация инфраструктурного токенизатора модели
from transformers import AutoTokenizer

print("⏳ Загружаем и инициализируем инфраструктурный токенизатор...")

# Разворачиваем модуль синтаксического анализа букв для ядра Qwen
model_id = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)

print("✅ Токенизатор успешно развернут в ОЗУ сервера и готов к работе во всех последующих главах!")
