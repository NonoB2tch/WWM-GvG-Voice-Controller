from dataclasses import dataclass, field
from time import monotonic
from core.timeline import PREP_SECONDS, MATCH_SECONDS, build_events

@dataclass
class MatchState:
    mode: str = "idle"
    prep_remaining: int = PREP_SECONDS
    current_countdown: int = MATCH_SECONDS
    started_monotonic: float | None = None
    pause_value: int | None = None
    events: list = field(default_factory=build_events)
    log: list[str] = field(default_factory=list)

    def reset(self):
        self.mode = "idle"
        self.prep_remaining = PREP_SECONDS
        self.current_countdown = MATCH_SECONDS
        self.started_monotonic = None
        self.pause_value = None
        self.events = build_events()
        self.log.clear()

    def start_prep(self, remaining_seconds: int):
        self.reset()
        self.mode = "prep"
        self.prep_remaining = remaining_seconds
        self.started_monotonic = monotonic()
        self.log.append(f"Подготовка запущена: осталось {remaining_seconds} сек")

    def start_live(self, countdown_seconds: int):
        self.reset()
        self.mode = "live"
        self.current_countdown = countdown_seconds
        self.started_monotonic = monotonic()
        self.log.append(f"Бой подхвачен с таймера {countdown_seconds} сек")

    def stop(self):
        self.log.append("Матч остановлен")
        self.mode = "idle"
        self.started_monotonic = None

    def pause(self):
        if self.mode not in {"prep", "live"}:
            return
        self.pause_value = self.current_value()
        self.mode = "paused"
        self.started_monotonic = None
        self.log.append("Матч поставлен на паузу")

    def resume(self):
        if self.pause_value is None:
            return
        if self.pause_value > MATCH_SECONDS:
            self.mode = "prep"
            self.prep_remaining = self.pause_value - MATCH_SECONDS
        else:
            self.mode = "live"
            self.current_countdown = self.pause_value
        self.started_monotonic = monotonic()
        self.log.append("Матч продолжен")

    def current_value(self) -> int:
        if self.mode == "idle":
            return MATCH_SECONDS
        if self.mode == "paused":
            return self.pause_value or MATCH_SECONDS
        if self.started_monotonic is None:
            return MATCH_SECONDS
        elapsed = int(monotonic() - self.started_monotonic)
        if self.mode == "prep":
            remaining_prep = max(0, self.prep_remaining - elapsed)
            if remaining_prep == 0:
                live_elapsed = max(0, elapsed - self.prep_remaining)
                return max(0, MATCH_SECONDS - live_elapsed)
            return MATCH_SECONDS + remaining_prep
        return max(0, self.current_countdown - elapsed)

    def next_event(self):
        current = self.current_value()
        for event in self.events:
            if not event.played and current <= event.countdown_time:
                return event
        return None
