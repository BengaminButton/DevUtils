# 🛠️ DevUtils - Ultimate Developer Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PyPI Version](https://img.shields.io/pypi/v/devutils)](https://pypi.org/project/devutils/)

Мощный набор инструментов для разработчиков с поддержкой CLI и GUI. Включает генератор QR-кодов, HTTP ping, Base64 конвертер и поисковик дубликатов файлов.

![DevUtils GUI Screenshot](<img width="1920" height="1080" alt="изображение" src="https://github.com/user-attachments/assets/29dec3c4-c6f6-4dec-be65-27ba51eb2ecd" />
) <!-- Добавь реальный скриншот позже -->

## ✨ Особенности
- **QR Generator**: Создание QR-кодов из текста/файлов с ASCII превью
- **HTTP Ping**: Проверка доступности сайтов с детальной статистикой
- **Base64 Tools**: Кодирование/декодирование текста и файлов
- **Duplicate Finder**: Поиск дубликатов файлов по хешу (MD5/SHA1/SHA256)
- **Modern GUI**: Темная тема, интуитивный интерфейс (PySide6)
- **Rich CLI**: Цветной вывод, интерактивные таблицы (Rich/Typer)

## ⚙️ Установка
```bash
# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/MacOS
.venv\Scripts\activate    # Windows

# Установка пакета
pip install -e .

🖥️ Использование CLI


# Генерация QR-кода
devutils qr --text "Hello World" --preview

# Проверка сайта
devutils ping https://example.com -c 5

# Base64 кодирование
devutils b64 encode --text "DevUtils rocks!" 

# Поиск дубликатов
devutils dupes ~/Documents --min-size 1024


🖼️ Использование GUI

devutils-gui

🧩 Технологический стек

    Core: Python 3.10+

    CLI: Typer + Rich

    GUI: PySide6 (Qt6)

    QR: qrcode[pil]

    Networking: requests


# Установка dev-зависимостей
pip install -e .[dev]

# Запуск тестов
pytest tests/

# Сборка пакета
python -m build

📜 Лицензия

MIT License - подробности в LICENSE
