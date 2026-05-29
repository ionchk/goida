
## Что тут?

- Сайт-портфолио Мозгалова Даниила
- Игра Ping Pong на C++
- 7 лабораторных работ по C++
- 6 лабораторных работ по Python
- Бот для оптовых заказов
- 17 заданий по HTML

## Проекты

### Ping Pong (C++)

Аркадная игра в терминале.

    cd ping-pong
    make
    ./pong


# Telegram-бот «Приём заказов»

Простой и удобный бот для приёма заказов от клиентов. Позволяет пользователю быстро оформить заказ через диалог: выбор категории → комментарий/пожелания → прикрепление файлов (фото, документы) → подтверждение.

После подтверждения заказ автоматически отправляется менеджеру.

## Возможности

- `/start` — приветствие и список команд
- `/neworder` — оформить новый заказ (пошаговый диалог)
- `/myorders` — показать мои последние заказы
- `/help` — справка
- `/cancel` — отменить текущее действие
- Автоматическая пересылка заказа менеджеру
- Сохранение всех заказов в `orders.json`

## Стек

- Python 3.10+
- Хранение данных — JSON

## Установка

```bash
cd order-bot
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
Запуск:

    cd telegram-bot
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Нужно создать файл .env и вписать туда BOT_TOKEN (получить у @BotFather)
и TEACHER_CHAT_ID (узнать через @userinfobot).

    cp .env.example .env

Потом:

    export BOT_TOKEN="..."
    export TEACHER_CHAT_ID="..."
    python3 bot.py

Команды: /start, /submit, /list, /help, /cancel

Подробнее: telegram-bot/README.md

## Лабораторные работы по C++

1. Линейные алгоритмы (ввод-вывод C-style и C++-style) - C++/lab1/main.cpp
2. Ветвление (точка относительно круга) - C++/lab2/main.cpp
3. Циклы while / do-while (сумма ряда) - C++/lab3/main.cpp
4. Цикл for + одномерный массив - C++/lab4/main.cpp
5. Двумерный массив + указатели - C++/lab5/main.cpp
6. Строки - C++/lab6/main.cpp
7. Функции (факториал + сочетания) - C++/lab7/main.cpp

Собрать все:

    cd C++
    make

Запустить:

    ./lab1/lab
    ./lab2/lab
    ...

## Лабораторные работы по Python

1. ANSI и вывод в консоль - python-labs/lab1/main.py
2. CSV и XML - python-labs/lab2/main.py
3. Tkinter (генератор ключей) - python-labs/lab3/main.py
4. Задача о рюкзаке (жадный + динамическое программирование) - python-labs/lab4/main.py
5. Регулярные выражения - python-labs/lab5/main.py
6. ООП (Person -> Student/Teacher, класс Group) - python-labs/lab6/main.py

Запуск:

    python3 python-labs/lab1/main.py
    python3 python-labs/lab2/main.py
    ...

## Задания по HTML

17 практических работ


## Резюме

PDF в корне репозитория:
- Resume Mozgalov D.E.pdf (английский)
- Резюме Мозгалов Д.Е.pdf (русский)

## Источники заданий

- Литвинская О.С. и др. "Основы программирования на языке C++". Методичка к лабораторным. Пенза, 2017. (файл metodichpipo (1).pdf)
- Лабораторный практикум 1-6 по Python (файл .docx)
- Практические работы по HTML (файл html_tasks.pdf)
