# Блок кода №19: объявление специализированных схем проверки достоверности данных Pydantic
from pydantic import BaseModel, Field
from typing import Optional, List

print("=== ФАБРИКА АГЕНТОВ: ИНИЦИАЛИЗАЦИЯ КОНТРАКТОВ ДАННЫХ ===")
print("⏳ Объявляем специализированные Pydantic-схемы для продавца и инженера...")

class SalesResponseSchema(BaseModel):
    """Строгий контракт данных для ИИ-агента торгового отдела ('Продажи')."""
    client_intent: str = Field(description="Выявленное коммерческое намерение покупателя.")
    recommended_product: str = Field(description="Точное имя флагманского товара из каталога склада.")
    accessory_upsell: Optional[str] = Field(description="Предложенный сопутствующий товар для увеличения чека.")
    marketing_trigger: str = Field(description="Психологический оффер или скидка для быстрого закрытия сделки.")
    clean_text_response: str = Field(description="Гладкая, вовлекающая и эмпатичная речь Агента для чата.")

class ServiceResponseSchema(BaseModel):
    """Строгий контракт данных для ИИ-агента сервисного центра (Техподдержка)."""
    technical_malfunction: str = Field(description="Локализованный узел поломки или симптом неисправности.")
    diagnostic_step: str = Field(description="Текущая сухая инструкция, которую клиент обязан выполнить прямо сейчас.")
    safety_warning: bool = Field(description="Признак критической опасности (например, риск возгорания батареи).")
    next_action_route: str = Field(description="Жесткое производственное направление: СКЛАД, РЕМОНТ или ТЕСТ.")
    clean_text_response: str = Field(description="Сухой, лаконичный и строго технический ответ Агента по пунктам.")

print("✅ Контракты данных SalesResponseSchema и ServiceResponseSchema успешно депонированы в ОЗУ!")
