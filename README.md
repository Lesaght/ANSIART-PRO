# 🎨 ANSIART-PRO | Image to ASCII Art Converter

<div align="center">

[🇷🇺 Русский](#russian-version) • [🇬🇧 English](#english-version)

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

**Мощный инструмент для конвертации изображений, GIF и видео в TrueColor ASCII-арт** 🎬

</div>

---

## Russian Version

### 🎬 Демонстрация в действии

<div align="center">

![ANSIART-PRO Demo](video/video.gif)

**Посмотрите как работает ANSIART-PRO в реальном времени** ↑

(p.s. извините то что лагает к сожелению .gif не подъерживает 60 fps сори)

</div>

---

### ✨ Возможности

<details open>
<summary><strong>🖼️ Поддерживаемые форматы</strong></summary>

- Статические изображения (PNG, JPG, BMP, и др.)
- Анимированные GIF файлы
- Видео файлы (MP4, AVI, MOV, и др.)
- Вебкамера в реальном времени

</details>

<details>
<summary><strong>🎨 Режимы вывода</strong></summary>

- Тексто́вый формат (TXT)
- ANSI цветной вывод (с поддержкой TrueColor)
- HTML страница (самодостаточная)
- Масштабируемая векторная графика (SVG)
- Монохромный ASCII (без цвета)

</details>

<details>
<summary><strong>⚙️ Настройки преобразования</strong></summary>

- Пользовательская ширина вывода (20-500 символов)
- Автоматическая подстройка ширины под терминал
- Множество градиентов символов (standard, dense, blocks, braille, simple, binary)
- Кастомные строки символов для градиента
- Управление яркостью и контрастом

</details>

<details>
<summary><strong>🎥 Поддержка видео и анимации</strong></summary>

- Конвертация видеофайлов с сохранением движения
- Анимированные GIF в ASCII-арт
- Управление частотой кадров (FPS)
- Режим цикла или однократное воспроизведение
- Потоковая обработка для оптимизации памяти

</details>

<details>
<summary><strong>🎛️ Эффекты обработки изображений</strong></summary>

- Инверсия яркости для другого вида
- Коэффициент пиксельного соотношения (font-ratio)
- Floyd–Steinberg дизеринг для плавных градиентов
- Регулировка яркости (0.1-3.0)
- Регулировка контраста (0.1-3.0)

</details>

<details>
<summary><strong>📺 Интерактивный режим TUI</strong></summary>

- Полнофункциональный терминальный интерфейс
- Интерактивное управление параметрами
- Предпросмотр в реальном времени
- Удобная навигация

</details>

### 🏗 Архитектура проекта

```
ANSIART-PRO/
├── main.py                     # Точка входа, парсинг CLI аргументов
├── requirements.txt            # Зависимости проекта
├── venv/                       # Виртуальное окружение (автоматически создаётся)
├── ansiart/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── converter.py        # Основной конвертер изображений в ASCII
│   │   ├── media_loader.py     # Загрузчик медиафайлов
│   │   ├── config.py           # Конфигурация преобразования
│   │   └── gradients.py        # Предустановленные градиенты
│   ├── tui/
│   ���   ├── app.py              # Интерактивный TUI интерфейс
│   │   └── components.py       # Компоненты интерфейса
│   ├── output/
│   │   ├── html_generator.py   # Генератор HTML
│   │   ├── svg_generator.py    # Генератор SVG
│   │   └── formatters.py       # Форматирующие утилиты
│   └── utils/
│       └── image_utils.py      # Утилиты обработки изображений
└── video/                      # Примеры видеодемонстраций
```

### 🚀 Установка и запуск

#### 1. Клонировать репозиторий
```bash
git clone https://github.com/Lesaght/ANSIART-PRO
cd ANSIART-PRO
```

#### 2. Запустить скрипт (виртуальное окружение создаётся автоматически)
```bash
python3 main.py
```

#### 3. Примеры использования

**Конвертировать изображение в ASCII-арт с выводом в терминал:**
```bash
python3 main.py image.jpg
```

**Конвертировать с пользовательской шириной:**
```bash
python3 main.py image.jpg --width 80
```

**Сохранить результат в файл (HTML):**
```bash
python3 main.py image.jpg --output output.html
```

**Сохранить в ANSI цветном формате:**
```bash
python3 main.py video.mp4 --output output.ansi
```

**Конвертировать видео с 30 FPS:**
```bash
python3 main.py video.mp4 --fps 30
```

**Использовать пользовательский градиент:**
```bash
python3 main.py image.jpg --gradient " .oO0@"
```

**Монохромный вывод без цвета:**
```bash
python3 main.py image.jpg --no-color
```

**Автоматическая подстройка ширины под терминал:**
```bash
python3 main.py image.jpg --auto-width
```

**Вебкамера в реальном времени:**
```bash
python3 main.py --webcam
```

### 🛠 Технологический стек

| Компонент | Версия | Назначение |
|-----------|--------|-----------|
| Python | 3.8+ | Язык программирования |
| textual | ≥50.0 | TUI фреймворк для интерфейса |
| Pillow (PIL) | ≥10.0.0 | Обработка изображений |
| OpenCV | ≥4.8.0 | Работа с видео и вебкамерой |
| Rich | ≥13.0.0 | Красивый вывод в терминал |

### 📡 Основные опции команды

```bash
usage: ansiart-pro [-h] [--width N] [--auto-width] [--no-color] 
                    [--gradient PRESET] [--invert] [--fps N] 
                    [--font-ratio F] [--brightness F] [--contrast F]
                    [--dither] [--no-loop] [--webcam] [--output FILE]
                    [file]

Gradient presets:  standard  dense  blocks  braille  simple  binary
```

**Параметры:**
- `file` — Путь к изображению, GIF или видео файлу
- `--width, -w N` — Целевая ширина вывода в символах (по умолчанию: 120, диапазон: 20–500)
- `--auto-width` — Автоматическая подстройка ширины под терминал
- `--no-color` — Монохромный вывод (без цвета)
- `--gradient, -g PRESET` — Предустановка градиента или кастомная строка (по умолчанию: standard)
- `--invert` — Инвертировать яркость
- `--fps N` — Частота кадров для GIF/видео (по умолчанию: 15.0, диапазон: 1–60)
- `--font-ratio F` — Коэффициент сжатия (по умолчанию: 0.55)
- `--brightness F` — Множитель яркости (по умолчанию: 1.0, диапазон: 0.1–3.0)
- `--contrast F` — Множитель контраста (по умолчанию: 1.0, диапазон: 0.1–3.0)
- `--dither` — Применить Floyd–Steinberg дизеринг
- `--no-loop` — Воспроизвести один раз без цикла
- `--webcam` — Прямая трансляция с вебкамеры
- `--output, -o FILE` — Сохранить результат в файл (формат определяется по расширению: .txt .ansi .html .svg)

### ⚙️ Технические детали

- **TrueColor поддержка** — Полная поддержка 24-bit RGB цветов в терминале
- **Эффективная обработка видео** — Потоковая обработка видеофреймов для минимизации памяти
- **Гибкие градиенты** — 6 встроенных предустановок + возможность кастомизации
- **Интерактивный интерфейс** — Powered by Textual для плавного взаимодействия
- **Множественные форматы вывода** — Сохранение в TXT, ANSI, HTML или SVG
- **Поддержка вебкамеры** — Через OpenCV для реального времени

### 📋 Ограничения и производительность

| Параметр | Значение |
|----------|---------|
| Минимальная ширина | 20 символов |
| Максимальная ширина | 500 символов |
| Минимальная частота кадров | 1 FPS |
| Максимальная частота кадров | 60 FPS |
| Коэффициент яркости | 0.1 - 3.0 |
| Коэффициент контраста | 0.1 - 3.0 |

---

## English Version

### 🎬 Live Demo

<div align="center">

![ANSIART-PRO Demo](video/video.gif)

**See ANSIART-PRO in action in real time** ↑

(p.s. sorry for the lag, unfortunately .gif doesn't support 60 fps)

</div>

---

### ✨ Features

<details open>
<summary><strong>🖼️ Supported Formats</strong></summary>

- Static images (PNG, JPG, BMP, etc.)
- Animated GIF files
- Video files (MP4, AVI, MOV, etc.)
- Webcam streaming in real-time

</details>

<details>
<summary><strong>🎨 Output Modes</strong></summary>

- Plain text format (TXT)
- ANSI colored output (with TrueColor support)
- Self-contained HTML page
- Scalable Vector Graphics (SVG)
- Monochrome ASCII (no color)

</details>

<details>
<summary><strong>⚙️ Conversion Settings</strong></summary>

- Custom output width (20-500 characters)
- Auto-fit width to terminal
- Multiple gradient presets (standard, dense, blocks, braille, simple, binary)
- Custom character strings for gradients
- Brightness and contrast control

</details>

<details>
<summary><strong>🎥 Video & Animation Support</strong></summary>

- Convert video files while preserving motion
- Animated GIF to ASCII art
- Adjustable frame rate (FPS)
- Loop or single playback mode
- Streaming processing for memory optimization

</details>

<details>
<summary><strong>🎛️ Image Processing Effects</strong></summary>

- Brightness inversion for different appearance
- Pixel aspect ratio coefficient (font-ratio)
- Floyd–Steinberg dithering for smooth gradients
- Brightness adjustment (0.1-3.0)
- Contrast adjustment (0.1-3.0)

</details>

<details>
<summary><strong>📺 Interactive TUI Mode</strong></summary>

- Full-featured terminal user interface
- Interactive parameter control
- Real-time preview
- Convenient navigation

</details>

### 🏗 Architecture

```
ANSIART-PRO/
├── main.py                     # Entry point, CLI argument parsing
├── requirements.txt            # Project dependencies
├── venv/                       # Virtual environment (auto-created)
├── ansiart/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── converter.py        # Main image-to-ASCII converter
│   │   ├── media_loader.py     # Media file loader
│   │   ├── config.py           # Conversion configuration
│   │   └── gradients.py        # Preset gradients
│   ├── tui/
│   │   ├── app.py              # Interactive TUI interface
│   │   └── components.py       # UI components
│   ├── output/
│   │   ├── html_generator.py   # HTML generator
│   │   ├── svg_generator.py    # SVG generator
│   │   └── formatters.py       # Formatting utilities
│   └── utils/
│       └── image_utils.py      # Image processing utilities
└── video/                      # Demo video examples
```

### 🚀 Installation & Setup

#### 1. Clone Repository
```bash
git clone https://github.com/Lesaght/ANSIART-PRO
cd ANSIART-PRO
```

#### 2. Run Script (virtual environment is auto-created)
```bash
python3 main.py
```

#### 3. Usage Examples

**Convert image to ASCII art in terminal:**
```bash
python3 main.py image.jpg
```

**Convert with custom width:**
```bash
python3 main.py image.jpg --width 80
```

**Save result to file (HTML):**
```bash
python3 main.py image.jpg --output output.html
```

**Save in ANSI color format:**
```bash
python3 main.py video.mp4 --output output.ansi
```

**Convert video at 30 FPS:**
```bash
python3 main.py video.mp4 --fps 30
```

**Use custom gradient:**
```bash
python3 main.py image.jpg --gradient " .oO0@"
```

**Monochrome output without color:**
```bash
python3 main.py image.jpg --no-color
```

**Auto-fit width to terminal:**
```bash
python3 main.py image.jpg --auto-width
```

**Webcam real-time stream:**
```bash
python3 main.py --webcam
```

### 🛠 Tech Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.8+ | Programming language |
| textual | ≥50.0 | TUI framework for interface |
| Pillow (PIL) | ≥10.0.0 | Image processing |
| OpenCV | ≥4.8.0 | Video and webcam support |
| Rich | ≥13.0.0 | Beautiful terminal output |

### 📡 Main Command Options

```bash
usage: ansiart-pro [-h] [--width N] [--auto-width] [--no-color] 
                    [--gradient PRESET] [--invert] [--fps N] 
                    [--font-ratio F] [--brightness F] [--contrast F]
                    [--dither] [--no-loop] [--webcam] [--output FILE]
                    [file]

Gradient presets:  standard  dense  blocks  braille  simple  binary
```

**Parameters:**
- `file` — Path to an image, GIF, or video file
- `--width, -w N` — Target output width in characters (default: 120, range: 20–500)
- `--auto-width` — Auto-fit width to terminal columns
- `--no-color` — Monochrome output (no color)
- `--gradient, -g PRESET` — Gradient preset or custom string (default: standard)
- `--invert` — Invert brightness mapping
- `--fps N` — Frame rate for GIF/video (default: 15.0, range: 1–60)
- `--font-ratio F` — Vertical compression factor (default: 0.55)
- `--brightness F` — Brightness multiplier (default: 1.0, range: 0.1–3.0)
- `--contrast F` — Contrast multiplier (default: 1.0, range: 0.1–3.0)
- `--dither` — Apply Floyd–Steinberg dithering
- `--no-loop` — Play once without looping
- `--webcam` — Stream live video from webcam
- `--output, -o FILE` — Save result to file (format by extension: .txt .ansi .html .svg)

### ⚙️ Technical Details

- **TrueColor Support** — Full 24-bit RGB color support in terminals
- **Efficient Video Processing** — Streaming video frame processing to minimize memory
- **Flexible Gradients** — 6 built-in presets + customization options
- **Interactive Interface** — Powered by Textual for smooth interaction
- **Multiple Output Formats** — Save as TXT, ANSI, HTML, or SVG
- **Webcam Support** — Via OpenCV for real-time streaming

### 📋 Limits & Performance

| Parameter | Value |
|-----------|-------|
| Minimum width | 20 characters |
| Maximum width | 500 characters |
| Minimum frame rate | 1 FPS |
| Maximum frame rate | 60 FPS |
| Brightness coefficient | 0.1 - 3.0 |
| Contrast coefficient | 0.1 - 3.0 |

---

<div align="center">

### 🚀 Готов начать? Используй `python3 main.py --help`

### 🚀 Ready to start? Use `python3 main.py --help`

---

Made with ❤️ by [hak0shka](https://github.com/hak0shka)

</div>
