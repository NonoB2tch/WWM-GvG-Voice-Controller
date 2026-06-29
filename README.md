# WWM GvG Voice Controller

Готовый проект под твой сценарий:
- desktop-приложение в стиле игрового control panel;
- 6 voice-ботов, по одному на канал;
- countdown боя 30:00 -> 00:00;
- 5 минут подготовки;
- спавны на 25 / 20 / 15 / 10 / 5;
- предупреждения за 40 / 30 / 10 секунд и в момент спавна;
- hybrid Discord-команды для резервного управления.

## Что внутри

- `main.py` — запуск desktop-приложения.
- `desktop/app.py` — интерфейс управления.
- `discord_bot/manager.py` — voice workers и Discord-команды.
- `core/timeline.py` — таймлайн матча.
- `core/state.py` — текущее состояние таймера.
- `config/config.example.json` — пример конфига.
- `.env.example` — пример env.

## Перед запуском

1. Установи Python 3.11.
2. Установи FFmpeg и добавь его в PATH.
3. Создай 6 Discord-ботов или минимум столько, сколько каналов будешь использовать.
4. Выдай ботам права:
   - View Channels
   - Connect
   - Speak
   - Use Application Commands
   - Send Messages
5. Скопируй:
   - `.env.example` -> `.env`
   - `config/config.example.json` -> `config/config.json`
6. Вставь свои токены, `guild_id`, `channel_id`, `role_id`.
7. Положи mp3-файлы в `assets/audio/`.

## Имена аудиофайлов

Нужно подготовить 20 файлов:

- `forest_25_40.mp3`
- `forest_25_30.mp3`
- `forest_25_10.mp3`
- `forest_25_spawn.mp3`
- `forest_20_40.mp3`
- `forest_20_30.mp3`
- `forest_20_10.mp3`
- `forest_20_spawn.mp3`
- `forest_15_40.mp3`
- `forest_15_30.mp3`
- `forest_15_10.mp3`
- `forest_15_spawn.mp3`
- `forest_10_40.mp3`
- `forest_10_30.mp3`
- `forest_10_10.mp3`
- `forest_10_spawn.mp3`
- `forest_5_40.mp3`
- `forest_5_30.mp3`
- `forest_5_10.mp3`
- `forest_5_spawn.mp3`

## Запуск

```bash
pip install -r requirements.txt
python main.py
```

## Как пользоваться desktop app

### 1. Подготовка
Если до старта боя ещё есть время, введи в блоке `Подготовка` значение вроде `05:00`, `04:00` или `01:30`, потом нажми `Старт подготовки`.

### 2. Подхват уже идущего боя
Если бой уже идёт, введи текущее значение игрового таймера, например `27:35`, `18:10` или `06:42`, потом нажми `Подхватить бой`.

### 3. Тест звука
Выбери ключ в выпадающем списке и нажми `Тест звука`.

### 4. Пауза / продолжение / стоп
Используй кнопки справа.

## Discord-команды

Командная группа: `gvg`

### Slash или текстом

- `/gvg prep 05:00`
- `/gvg live 27:35`
- `/gvg stop`
- `/gvg pause`
- `/gvg resume`
- `/gvg status`
- `/gvg test forest_25_40`

Текстовые аналоги:

- `!gvg prep 05:00`
- `!gvg live 27:35`
- `!gvg stop`
- `!gvg pause`
- `!gvg resume`
- `!gvg status`
- `!gvg test forest_25_40`

## Важно

Сейчас control bot использует `BOT_TOKEN_1`. Для production лучше вынести control bot в отдельный токен.

## Сборка в exe

Базовый вариант через PyInstaller:

```bash
py -m PyInstaller --noconfirm --onedir --windowed --collect-data customtkinter main.py
```

Если захочешь, следующим этапом можно вынести voice workers в отдельные процессы и сделать нормальный installer/portable build.
