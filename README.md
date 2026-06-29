# WWM GvG Voice Controller

Готовый проект под твой сценарий:
- desktop-приложение в стиле игрового control panel;
- 6 voice-ботов, по одному на канал;
- countdown боя 30:00 -> 00:00;
- 5 минут подготовки;
- спавны на 25 / 20 / 15 / 10 / 5;
- предупреждения за 40 / 30 / 10 секунд и в момент спавна;
- hybrid Discord-команды для резервного управления.

## Перед запуском
1. Установи Python 3.11.
2. Установи FFmpeg и добавь его в PATH.
3. Скопируй `.env.example` -> `.env`.
4. Скопируй `config/config.example.json` -> `config/config.json`.
5. Вставь свои токены, `guild_id`, `channel_id`, `role_id`.
6. Положи mp3-файлы в `assets/audio/`.

## Имена аудиофайлов
Нужно подготовить 20 файлов:
- forest_25_40.mp3
- forest_25_30.mp3
- forest_25_10.mp3
- forest_25_spawn.mp3
- forest_20_40.mp3
- forest_20_30.mp3
- forest_20_10.mp3
- forest_20_spawn.mp3
- forest_15_40.mp3
- forest_15_30.mp3
- forest_15_10.mp3
- forest_15_spawn.mp3
- forest_10_40.mp3
- forest_10_30.mp3
- forest_10_10.mp3
- forest_10_spawn.mp3
- forest_5_40.mp3
- forest_5_30.mp3
- forest_5_10.mp3
- forest_5_spawn.mp3

## Запуск
```bash
pip install -r requirements.txt
python main.py
```

## Команды
- /gvg prep 05:00
- /gvg live 27:35
- /gvg stop
- /gvg pause
- /gvg resume
- /gvg status
- /gvg test forest_25_40

Текстовые аналоги:
- !gvg prep 05:00
- !gvg live 27:35
- !gvg stop
- !gvg pause
- !gvg resume
- !gvg status
- !gvg test forest_25_40
