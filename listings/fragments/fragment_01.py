%%writefile discount_processor.py
# discount_processor.py
# Классический детерминированный модуль для магазина Боба

def calculate_customer_discount(user_status: str, purchase_amount: float) -> float:
    """Вычисляет жестко заданную скидку на основе статуса клиента."""
    if user_status == "premium":
        return purchase_amount * 0.15        # премиальная скидка 15%
    elif user_status == "regular":
        if purchase_amount > 500:
            return purchase_amount * 0.05    # базовая скидка 5% при крупной покупке
        return 0.0
    else:
        return 0.0

# Модульный тест для проверки детерминированного алгоритма
if __name__ == "__main__":
    print("⏳ Запуск модульного тестирования для детерминированного алгоритма...")

    # Тест 1: премиальный клиент
    result_1 = calculate_customer_discount("premium", 1000.0)
    assert result_1 == 150.0, f"Ошибка теста 1: Ожидалось 150.0, получено {result_1}"

    # Тест 2: обычный клиент с крупной покупкой
    result_2 = calculate_customer_discount("regular", 600.0)
    assert result_2 == 30.0, f"Ошибка теста 2: Ожидалось 30.0, получено {result_2}"

    print("✅ Все модульные тесты для детерминированного алгоритма успешно пройдены!")
