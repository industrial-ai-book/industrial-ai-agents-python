# Блок кода №4: инициализация токенизатора и модели половинной точности
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

print("✓ Начинаем конвейерную сборку ИИ-агента...")

# Загружаем модуль разбиения текста (токенизатор) для архитектуры Qwen
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Загружаем вычислительное ядро модели, принудительно сжимая веса в формат половинной точности
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"    # Автоматический монтаж слоев нейросети на ядра ГП
)

print("✓ Цифровой мозг успешно развернут в видеопамяти!")
print(f"✓ Вычислительное устройство зафиксировано: {model.device}")
