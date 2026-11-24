# Блок кода №24: инициализация реляционной базы данных SQLite в ОЗУ и генерация контрольного набора данных
import sqlite3

print("=== 🗄️ ИНИЦИАЛИЗАЦИЯ РЕЛЯЦИОННОГО ЯДРА СКЛАДА БОБА ===")
print("⏳ Создаем базу данных SQLite в оперативной памяти...")

# 1. Инициализируем резидентную базу данных SQLite непосредственно в ОЗУ.
# Важно: флаг check_same_thread=False отключает жесткую привязку дескриптора
# к главному потоку. Это подготовит базу данных к безопасным многопоточным
# запросам из фонового пула ThreadPoolExecutor, который мы развернем в главе 7
# для защиты асинхронного цикла событий от зависания!
db_connection = sqlite3.connect(":memory:", check_same_thread=False)
db_cursor = db_connection.cursor()

# 2. Создаем структуру таблиц склада по правилам реляционной целостности
print("📋 Проектируем структуру таблиц склада...")
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock_quantity INTEGER NOT NULL,
    warehouse_slot TEXT NOT NULL
);
""")

db_cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    customer_name TEXT NOT NULL,
    quantity_ordered INTEGER NOT NULL,
    order_timestamp TEXT NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(id)
);
""")

# 3. Формируем жесткий контрольный набор данных для проверки логики агента
print("📥 Загружаем контрольный набор данных в таблицы...")
mock_products = [
    ("Смартфон ФотоЭксперт", "смартфоны", 700.0, 45, "А-3"),
    ("Чехол-книжка для смартфона", "аксессуары", 20.0, 150, "Б-1"),
    ("Защитное стекло Premium", "аксессуары", 15.0, 0, "Б-2"),      # Товар полностью отсутствует (тест на излом)
    ("Быстрая беспроводная зарядка", "аксессуары", 45.0, 12, "А-1")
]

db_cursor.executemany("""
INSERT INTO products (product_name, category, price, stock_quantity, warehouse_slot)
VALUES (?, ?, ?, ?, ?);
""", mock_products)

db_connection.commit()

# --- КАЛИБРОВОЧНЫЙ ПУСК: проверяем доступность реляционного ядра ---
print("\n=== ⚙️ ПРОВЕРКА РАБОТОСПОСОБНОСТИ БАЗЫ ДАННЫХ (калибровочный SELECT) ===")
try:
    db_cursor.execute("SELECT id, product_name, category, price, stock_quantity FROM products;")
    rows = db_cursor.fetchall()
    print("Содержимое таблицы 'products' в ОЗУ:")
    # Прецизионная распаковка кортежа для безопасного форматирования строковых литералов
    for p_id, p_name, cat, pr, qty in rows:
        print(f" ID: {p_id} | Товар: {p_name:<28} | Категория: {cat:<10} | Цена: ${pr:<5.1f} | Остаток: {qty} шт.")
    print("\n✅ Реляционное ядро успешно развернуто и готово к приему транзакций!")
except Exception as e:
    print(f"❌ Ошибка калибровочного пуска базы данных: {e}")
