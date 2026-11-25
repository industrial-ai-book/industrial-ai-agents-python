# ИИ-агенты на Python: от прототипа до автономных систем
### Практическое руководство по RAG, MCP и мультиагентным архитектурам

[![Open Industrial-AI-agent.ipynb in Colab](https://img.shields.io/badge/Colab-Industrial--AI--agent.ipynb-F9AB00?logo=googlecolab&logoColor=white)](https://colab.research.google.com/github/industrial-ai-book/industrial-ai-agents-python/blob/main/Industrial-AI-agent.ipynb)

[![Open Individual-Code-Fragments.ipynb in Colab](https://img.shields.io/badge/Colab-Individual--Code--Fragments.ipynb-F9AB00?logo=googlecolab&logoColor=white)](https://colab.research.google.com/github/industrial-ai-book/industrial-ai-agents-python/blob/main/Individual-Code-Fragments.ipynb)

[![Live Demo on Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Live%20Demo-blue)](https://huggingface.co/spaces/you-ry/bob-warehouse-ai)


Официальный репозиторий с исходным кодом, интерактивными блокнотами Google Colab и производственными конфигурациями к книге **"ИИ-агенты на Python: от прототипа до автономных систем"**.

---

## Что внутри репозитория

* **`Industrial-AI-agent.ipynb`** — основной блокнот со сквозным проектом ИИ-агента (главы 1–7): пошаговая сборка ИИ-комплекса от базовых контрактов Pydantic и конечных автоматов Outlines до резидентного поиска RAG, двухтактного надзора через ИИ-судью (OpenRouter), трехэшелонной защиты SQLite и MCP-сервера.
* **`Individual-Code-Fragments.ipynb`** — вспомогательный блокнот с изолированными экспериментами и тестами моделей.
* **`listings/`** — все листинги кода из книги в виде отдельных готовых `.py`-файлов (без сокращений):
  * `listings/main_project/` — блоки кода основного конвейера (`block_01.py` — `block_34.py`, включая блоки `22-А`, `22-Б`, `25-А`).
  * `listings/fragments/` — отдельные тестовые фрагменты (`fragment_01.py` — `fragment_05.py`).
* **Производственный Docker-комплекс (главы 9–10):**
  * `init_db.py` и `init_docs.py` — сценарии генерации физической базы данных SQLite (`warehouse.db`) и базы корпоративных регламентов (`regulations.json`) в папке `data/`.
  * `server.py` — единый производственный MCP-сервер (стандарт v2.x, транспорт `stdio`, JSON-аудит в `sys.stderr` и `audit.log`).
  * `Dockerfile` — декларативная инструкция сборки изолированного Linux-образа.
  * `orchestrator.py` — автономный Python-оркестратор с циклом вызова инструментов через OpenRouter и финальной проверкой ответов ИИ-судьей.
  * `web_demo.py` — локальная веб-витрина проекта на базе Gradio.
* **`mcp_bridge.py`** — асинхронный мост-ретранслятор (`stdio` ↔ `SSE`) из главы 8 для экспериментов с сетевыми туннелями.
* **`hf_deploy/`** — готовый комплект файлов (`app.py`, `server.py`, `init_db.py`, `init_docs.py`, `requirements.txt`) для публикации облачной демо-витрины на платформе **Hugging Face Spaces**.

---

## Быстрый старт: запуск производственного комплекса в Docker

### 1. Подготовка данных на локальном диске
Клонируйте или загрузите файлы репозитория в рабочую папку (например, `C:\mcp_project`) и сгенерируйте локальные хранилища в подпапке `data/`:

```bash
python init_db.py
python init_docs.py
```

### 2. Сборка Docker-образа
Убедитесь, что запущен **Docker Desktop**, и выполните сборку образа (не забудьте точку в конце команды):

```bash
docker build -t bob-warehouse-mcp .
```

### 3. Запуск автономного оркестратора (глава 10)
Установите клиентские библиотеки и укажите свой API-ключ OpenRouter в переменных среды:

```bash
pip install openai "mcp>=2.0.0" --upgrade
```

**Windows (PowerShell):**
```powershell
\$env:OPENROUTER_API_KEY="sk-or-v1-ваш-ключ"
python orchestrator.py
```

**Linux / macOS:**
```bash
export OPENROUTER_API_KEY="sk-or-v1-ваш-ключ"
python orchestrator.py
```

---

## Живая онлайн-демонстрация

Протестировать работу ИИ-диспетчера склада (поиск остатков в SQLite + регламенты RAG + расчет логистики + блокировка SQL-инъекций ИИ-судьей) можно прямо в браузере без установки ПО:

👉 **[Открыть демо-стенд на Hugging Face Spaces](https://huggingface.co/spaces/you-ry/bob-warehouse-ai)**
