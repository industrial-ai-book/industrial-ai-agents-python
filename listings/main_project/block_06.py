# Блок кода №6: проектирование схемы проверки достоверности в Pydantic
from pydantic import BaseModel, Field
from typing import Optional

print("⏳ Проектируем контур проверки достоверности данных...")

class AgentOutputSchema(BaseModel):
    client_action: str = Field(
        description="Режим работы Агента. Строго 'ТЕХПОДДЕРЖКА' или 'ПОДБОР_ТЕХНИКИ'."
    )
    recommended_product: Optional[str] = Field(
        default=None,
        description="Системное имя смартфона из каталога. Если режим 'ТЕХПОДДЕРЖКА' — вернуть null."
    )
    product_price_usd: Optional[int] = Field(
        default=None,
        description="Чистая цена устройства строго в долларах. Если режим 'ТЕХПОДДЕРЖКА' — вернуть null."
    )
    text_response: str = Field(
        description="Финальный лаконичный ответ покупателю. В разделе ТЕХПОДДЕРЖКА — до 2 предложений."
    )

print("✅ Схема AgentOutputSchema успешно развернута и готова к конвейерной проверке!")
