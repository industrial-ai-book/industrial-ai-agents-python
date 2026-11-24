# ===============================================================
# СЦЕНАРИЙ ИНИЦИАЛИЗАЦИИ БД: init_db.py (межплатформенная версия)
# ===============================================================
from pathlib import Path
import sqlite3

# Автоматически определяем каталог, в котором находится сценарий, и создаем папку data
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

db_path = DATA_DIR / "warehouse.db"

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    # Создаем таблицу товаров склада
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL
        );
    """)
    # Очищаем таблицу перед наполнением эталонными данными
    cursor.execute("DELETE FROM products;")
    cursor.executemany(
        "INSERT INTO products (product_name, category, price, stock_quantity) VALUES (?, ?, ?, ?);",
        [
            ("Apple", "Фрукты и продукты", 1.5, 150),
            ("Смартфон ФотоЭксперт", "Электроника", 450.0, 24),
            ("Чехол для смартфона", "Аксессуары", 20.0, 150)
        ]
    )
    conn.commit()

print(f"✔ Физическая база данных склада успешно создана: {db_path}")
