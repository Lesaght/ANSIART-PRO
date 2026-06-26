<!-- Language Selector -->
<div align="center">

# 🌐 Language / Язык

[![EN](https://img.shields.io/badge/English-blue?style=for-the-badge)](./README_EN.md) 
[![RU](https://img.shields.io/badge/Русский-red?style=for-the-badge)](./README.md)

---

</div>

# 📝 TXT-CLI

> Мощный и простой инструмент командной строки для работы с текстовыми файлами

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

</div>

---

## 📋 Содержание

- [Описание](#описание)
- [Возможности](#возможности)
- [Установка](#установка)
- [Использование](#использование)
- [Примеры](#примеры)
- [Документация](#документация)
- [Сотрудничество](#сотрудничество)
- [Лицензия](#лицензия)

---

## 📖 Описание

**TXT-CLI** — это универсальный инструмент командной строки для быстрой и удобной обработки текстовых файлов. Идеален для автоматизации задач, обработки логов и манипуляции с текстом.

---

## ⭐ Возможности

- ✅ **Быстрая обработка текста** - оптимизирована для больших файлов
- ✅ **Простой синтаксис** - легко учиться и использовать
- ✅ **Мощные фильтры** - поиск и замена по регулярным выражениям
- ✅ **Пакетная обработка** - работайте с несколькими файлами одновременно
- ✅ **Безопасность** - создание резервных копий перед изменениями
- ✅ **Гибкие опции** - настраиваемые параметры под ваши нужды

---

## 🚀 Установка

### Требования
- Python 3.8 или выше
- pip (менеджер пакетов Python)

### Быстрая установка

```bash
# Клонируйте репозиторий
git clone https://github.com/Lesaght/TXT-CLI.git
cd TXT-CLI

# Установите зависимости
pip install -r requirements.txt

# Запустите установку
python setup.py install
```

### Или через pip

```bash
pip install txt-cli
```

---

## 💻 Использование

### Основной синтаксис

```bash
txt-cli [команда] [опции] [файл]
```

### Общие команды

| Команда | Описание | Пример |
|---------|---------|---------|
| `info` | Получить информацию о файле | `txt-cli info file.txt` |
| `count` | Подсчитать строки/слова/символы | `txt-cli count file.txt` |
| `filter` | Фильтровать строки по критериям | `txt-cli filter -p "pattern" file.txt` |
| `replace` | Заменить текст | `txt-cli replace -f "old" -t "new" file.txt` |
| `extract` | Извлечь данные | `txt-cli extract -p "pattern" file.txt` |
| `sort` | Отсортировать строки | `txt-cli sort file.txt` |
| `merge` | Объединить файлы | `txt-cli merge file1.txt file2.txt` |

---

## 📚 Примеры

### Пример 1: Подсчёт статистики файла

```bash
txt-cli count myfile.txt
# Вывод:
# Строк: 1000
# Слов: 5000
# Символов: 25000
```

### Пример 2: Поиск и замена

```bash
txt-cli replace -f "ошибка" -t "улучшено" -b data.txt
# -b создает резервную копию перед изменением
```

### Пример 3: Фильтрация строк

```bash
txt-cli filter -p "^ERROR" -o output.txt logfile.log
# Извлекает все строки, начинающиеся с "ERROR"
```

### Пример 4: Объединение файлов

```bash
txt-cli merge file1.txt file2.txt file3.txt -o combined.txt
```

### Пример 5: Использование регулярных выражений

```bash
txt-cli extract -p "\b[\w.-]+@[\w.-]+\.\w+\b" emails.txt
# Извлекает все email адреса
```

---

## 📖 Подробная документация

### Опции команды `filter`

```bash
txt-cli filter [опции] <файл>

Опции:
  -p, --pattern    Регулярное выражение для поиска
  -v, --invert     Инвертировать результат (исключить совпадения)
  -i, --ignore-case Игнорировать регистр
  -o, --output     Файл для сохранения результата
  -c, --count      Только показать количество совпадений
```

### Опции команды `replace`

```bash
txt-cli replace [опции] <файл>

Опции:
  -f, --from       Текст для поиска
  -t, --to         Текст для замены
  -r, --regex      Использовать регулярные выражения
  -i, --ignore-case Игнорировать регистр
  -b, --backup     Создать резервную копию
  -o, --output     Файл для сохранения результата
  -a, --all        Заменить все вхождения (по умолчанию)
```

---

## 🤝 Сотрудничество

Мы приветствуем вклад в проект! 

### Как помочь:

1. **Форкируйте** репозиторий
2. **Создайте** ветку для вашей функции (`git checkout -b feature/AmazingFeature`)
3. **Коммитьте** ваши изменения (`git commit -m 'Add some AmazingFeature'`)
4. **Пушьте** в ветку (`git push origin feature/AmazingFeature`)
5. **Откройте** Pull Request

### Сообщение об ошибках

Если вы нашли баг, пожалуйста [создайте issue](https://github.com/Lesaght/TXT-CLI/issues) с описанием:
- Версия TXT-CLI
- Операционная система
- Шаги для воспроизведения
- Ожидаемое поведение
- Фактическое поведение

---

## 🛠️ Требования для разработки

```bash
# Установите зависимости для разработки
pip install -r requirements-dev.txt

# Запустите тесты
pytest tests/

# Проверьте качество кода
flake8 txt_cli/
```

---

## 📝 Лицензия

Этот проект распространяется под лицензией **MIT**. Подробнее смотрите в файле [LICENSE](LICENSE).

---

## 👨‍💻 Автор

**Lesaght** - [GitHub Profile](https://github.com/Lesaght)

---

## 💬 Связь и поддержка

- 🐛 **Сообщить об ошибке**: [Issues](https://github.com/Lesaght/TXT-CLI/issues)
- 💡 **Запросить функцию**: [Discussions](https://github.com/Lesaght/TXT-CLI/discussions)
- 📧 **Email**: contact@example.com

---

## 🗺️ Дорожная карта

- [ ] Добавить поддержку JSON файлов
- [ ] Реализовать параллельную обработку
- [ ] Создать GUI интерфейс
- [ ] Добавить поддержку плагинов
- [ ] Оптимизировать производительность

---

<div align="center">

### ⭐ Если проект вам нравится, пожалуйста поставьте звезду!

**Made with ❤️ by Lesaght**

</div>
