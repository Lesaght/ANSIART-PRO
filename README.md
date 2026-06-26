# 📝 TXT-CLI | Текстовый инструмент командной строки

<div align="center">

[🇷🇺 Русский](#russian-version) • [🇬🇧 English](#english-version)

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

**Мощный инструмент командной строки для работы с текстовыми файлами** ⚡

</div>

---

## Russian Version

### 🎬 Демонстрация в действии

<div align="center">

![TXT-CLI Demo](video.gif)

**Посмотрите как работает TXT-CLI в реальном времени** ↑

</div>

---

### ✨ Возможности

<details open>
<summary><strong>📊 Статистика файла</strong></summary>

- Подсчёт строк, слов, символов
- Вывод информации о файле и метаданных
- Анализ сложности текста и плотности
- Генерация детальных отчётов статистики

</details>

<details>
<summary><strong>🔍 Продвинутый поиск и фильтрация</strong></summary>

- Поиск по регулярным выражениям
- Поиск без учёта регистра
- Инвертирование результатов (исключение совпадений)
- Фильтрация по критериям построчно
- Извлечение контента по шаблонам

</details>

<details>
<summary><strong>✏️ Замена и трансформация текста</strong></summary>

- Поиск и замена с поддержкой regex
- Замена без учёта регистра
- Пакетная замена в нескольких файлах
- Автоматическое создание резервных копий
- Безопасные операции с файлами

</details>

<details>
<summary><strong>📂 Пакетная обработка</strong></summary>

- Одновременная обработка нескольких файлов
- Применение операций к целым директориям
- Рекурсивный обход директорий
- Параллельная обработка файлов

</details>

<details>
<summary><strong>🔐 Функции безопасности</strong></summary>

- Автоматическое создание резервных копий
- Функция отката последних изменений
- Безопасный режим с подтверждениями
- Валидация перед модификацией
- Обработка ошибок и восстановление

</details>

<details>
<summary><strong>📋 Объединение и разделение файлов</strong></summary>

- Объединение нескольких файлов в один
- Разделение больших файлов по количеству строк
- Сохранение форматирования и кодировки
- Добавление пользовательских разделителей

</details>

<details>
<summary><strong>🎯 Извлечение данных</strong></summary>

- Извлечение строк по шаблонам
- Извлечение столбцов из структурированных данных
- Сохранение извлечённых данных
- Поддержка различных разделителей
- Работа с CSV и TSV

</details>

<details>
<summary><strong>📈 Сортировка и организация</strong></summary>

- Сортировка строк по алфавиту
- Сортировка по длине строки
- Числовая сортировка
- Обратная сортировка
- Удаление дубликатов
- Пользовательские критерии сортировки

</details>

### 🏗 Архитектура проекта

```
TXT-CLI/
├── main.py                  # Точка входа, маршрутизация CLI
├── config.py                # Конфигурация и умолчания
├── requirements.txt         # Зависимости проекта
├── setup.py                 # Скрипт установки
├── cli/
│   ├── __init__.py
│   ├── commands/
│   │   ├── info.py          # Информация о файле
│   │   ├── count.py         # Статистика и подсчеты
│   │   ├── filter.py        # Фильтрация по шаблонам
│   │   ├── replace.py       # Поиск и замена
│   │   ├── extract.py       # Извлечение данных
│   │   ├── sort.py          # Операции сортировки
│   │   ├── merge.py         # Объединение файлов
│   │   └── split.py         # Разделение файлов
│   ├── utils/
│   │   ├── file_handler.py  # Обёртка операций с файлами
│   │   ├── regex_engine.py  # Утилиты regex
│   │   └── formatters.py    # Форматирование вывода
│   ├── validators.py        # Валидация входных данных
│   └── backup.py            # Управление резервными копиями
├── tests/
│   ├── test_commands.py
│   ├── test_utils.py
│   └── test_integration.py
└── docs/
    ├── COMMANDS.md          # Подробный справочник команд
    └── EXAMPLES.md          # Примеры использования
```

### 🚀 Установка и запуск

#### 1. Клонировать репозиторий
```bash
git clone https://github.com/Lesaght/TXT-CLI.git
cd TXT-CLI
```

#### 2. Создать виртуальное окружение
```bash
python3 -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Установить TXT-CLI
```bash
# Через setup.py
python setup.py install

# Или запустить напрямую
python main.py [команда] [опции] [файл]
```

#### 4. Проверить установку
```bash
txt-cli --version
txt-cli --help
```

### 🛠 Технологический стек

| Компонент | Версия | Назначение |
|-----------|--------|-----------|
| Python | 3.8+ | Язык программирования |
| argparse | встроен | Парсинг аргументов CLI |
| re | встроен | Регулярные выражения |
| os/pathlib | встроен | Операции с файлами |
| shutil | встроен | Утилиты файловых операций |

### 📡 Основные команды

**Базовые операции**
- `info` — Показать информацию о файле
- `count` — Подсчитать строки, слова, символы
- `filter` — Фильтровать строки по шаблону
- `replace` — Поиск и замена текста
- `extract` — Извлечение совпадающего контента

**Управление файлами**
- `sort` — Сортировка строк файла
- `merge` — Объединение нескольких файлов
- `split` — Разделение больших файлов
- `backup` — Создание/восстановление резервных копий

### ⚙️ Технические детали

- **Эффективный I/O** — Потоковая обработка больших файлов для минимизации использования памяти
- **Поддержка Regex** — Полные возможности Python regex для мощного поиска по шаблонам
- **Пакетная обработка** — `os.walk()` и многопоточность для параллельных операций
- **Безопасные операции** — Автоматические резервные копии перед модификацией
- **Обработка кодировок** — Поддержка UTF-8 и мультикодировок
- **Восстановление после ошибок** — Корректная обработка ошибок с информативными сообщениями

### 📋 Ограничения и производительность

| Параметр | Значение |
|----------|---------|
| Максимальный размер файла | Ограничено доступной RAM |
| Потоки пакетной обработки | 4 (настраивается) |
| Timeout regex | 5 секунд |
| Хранение резервных копий | 10 версий |
| Безопасный режим | Включён по умолчанию |

---

## English Version

### 🎬 Live Demo

<div align="center">

![TXT-CLI Demo](video.gif)

**See TXT-CLI in action in real time** ↑

</div>

---

### ✨ Features

<details open>
<summary><strong>📊 File Statistics</strong></summary>

- Count lines, words, characters
- Display file information and metadata
- Analyze text complexity and density
- Generate detailed statistics reports

</details>

<details>
<summary><strong>🔍 Advanced Search & Filter</strong></summary>

- Pattern matching with regex support
- Case-insensitive search
- Invert search results (exclude matches)
- Line-by-line filtering with criteria
- Extract specific content by patterns

</details>

<details>
<summary><strong>✏️ Text Replacement & Transformation</strong></summary>

- Find and replace with regex support
- Case-insensitive replacements
- Batch replacements across multiple files
- Automatic backup creation before changes
- Safe file operations with validation

</details>

<details>
<summary><strong>📂 Batch Processing</strong></summary>

- Process multiple files simultaneously
- Apply operations to entire directories
- Recursive directory traversal
- Parallel file handling for efficiency

</details>

<details>
<summary><strong>🔐 Safety Features</strong></summary>

- Automatic backup creation
- Undo functionality for recent changes
- Safe mode with confirmation prompts
- Validation before file modifications
- Error handling and recovery

</details>

<details>
<summary><strong>📋 File Merging & Splitting</strong></summary>

- Merge multiple files into one
- Split large files by line count
- Preserve formatting and encoding
- Add custom separators between merged content

</details>

<details>
<summary><strong>🎯 Data Extraction</strong></summary>

- Extract lines matching patterns
- Extract columns from structured data
- Save extracted data to new files
- Support for different delimiters
- CSV and TSV handling

</details>

<details>
<summary><strong>📈 Sorting & Organizing</strong></summary>

- Sort lines alphabetically
- Sort by line length
- Numeric sorting
- Reverse sorting
- Remove duplicate lines
- Custom sort criteria

</details>

### 🏗 Architecture

```
TXT-CLI/
├── main.py                  # Entry point, CLI router
├── config.py                # Configuration and defaults
├── requirements.txt         # Project dependencies
├── setup.py                 # Installation script
├── cli/
│   ├── __init__.py
│   ├── commands/
│   │   ├── info.py          # File information
│   │   ├── count.py         # Statistics & counting
│   │   ├── filter.py        # Pattern filtering
│   │   ├── replace.py       # Find and replace
│   │   ├── extract.py       # Data extraction
│   │   ├── sort.py          # Sorting operations
│   │   ├── merge.py         # File merging
│   │   └── split.py         # File splitting
│   ├── utils/
│   │   ├── file_handler.py  # File operations wrapper
│   │   ├── regex_engine.py  # Regex utilities
│   │   └── formatters.py    # Output formatting
│   ├── validators.py        # Input validation
│   └── backup.py            # Backup management
├── tests/
│   ├── test_commands.py
│   ├── test_utils.py
│   └── test_integration.py
└── docs/
    ├── COMMANDS.md          # Detailed command reference
    └── EXAMPLES.md          # Usage examples
```

### 🚀 Installation & Setup

#### 1. Clone Repository
```bash
git clone https://github.com/Lesaght/TXT-CLI.git
cd TXT-CLI
```

#### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Install TXT-CLI
```bash
# Via setup.py
python setup.py install

# Or directly run
python main.py [command] [options] [file]
```

#### 4. Verify Installation
```bash
txt-cli --version
txt-cli --help
```

### 🛠 Tech Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.8+ | Programming language |
| argparse | built-in | CLI argument parsing |
| re | built-in | Regular expressions |
| os/pathlib | built-in | File operations |
| shutil | built-in | File utilities |

### 📡 Core Commands

**Basic Operations**
- `info` — Display file information
- `count` — Count lines, words, characters
- `filter` — Filter lines by pattern
- `replace` — Find and replace text
- `extract` — Extract matching content

**File Management**
- `sort` — Sort file lines
- `merge` — Combine multiple files
- `split` — Split large files
- `backup` — Create/restore backups

### ⚙️ Technical Details

- **Efficient I/O** — Streaming large files to minimize memory usage
- **Regex Support** — Full Python regex capabilities for powerful pattern matching
- **Batch Processing** — `os.walk()` and threading for parallel operations
- **Safe Operations** — Automatic backups before modifications
- **Encoding Handling** — UTF-8 and multi-encoding support
- **Error Recovery** — Graceful error handling with informative messages

### 📋 Limits & Performance

| Parameter | Value |
|-----------|-------|
| Max file size | Limited by available RAM |
| Batch process threads | 4 (configurable) |
| Regex timeout | 5 seconds |
| Backup retention | 10 versions |
| Safe mode | Enabled by default |

---

<div align="center">

### 🚀 Готов к использованию? Начните с `txt-cli --help`

### 🚀 Ready to use? Start with `txt-cli --help`

---

Made with ❤️ by [Lesaght](https://github.com/Lesaght)

</div>
