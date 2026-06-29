from core.models import ScheduledEvent

PREP_SECONDS = 5 * 60
MATCH_SECONDS = 30 * 60
SPAWNS = [25 * 60, 20 * 60, 15 * 60, 10 * 60, 5 * 60]
WARNINGS = [40, 30, 10, 0]

def build_events() -> list[ScheduledEvent]:
    events = []
    for spawn in SPAWNS:
        for warning in WARNINGS:
            if warning == 0:
                key = f"forest_{spawn // 60}_spawn"
                label = f"Лес {spawn // 60}:00 появился"
                countdown_time = spawn
            else:
                key = f"forest_{spawn // 60}_{warning}"
                label = f"Лес {spawn // 60}:00 через {warning} сек"
                countdown_time = spawn + warning
            events.append(ScheduledEvent(key=key, countdown_time=countdown_time, label=label, audio_key=key))
    events.sort(key=lambda e: e.countdown_time, reverse=True)
    return events

def parse_mmss(value: str) -> int:
    parts = value.strip().split(":")
    if len(parts) != 2:
        raise ValueError("Используй формат мм:сс")
    minutes = int(parts[0])
    seconds = int(parts[1])
    total = minutes * 60 + seconds
    if minutes < 0 or seconds < 0 or seconds > 59:
        raise ValueError("Неверное время")
    return total

def format_mmss(total_seconds: int) -> str:
    total_seconds = max(0, int(total_seconds))
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"
