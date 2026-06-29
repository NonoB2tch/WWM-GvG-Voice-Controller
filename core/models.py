from dataclasses import dataclass

@dataclass
class ScheduledEvent:
    key: str
    countdown_time: int
    label: str
    audio_key: str
    played: bool = False
