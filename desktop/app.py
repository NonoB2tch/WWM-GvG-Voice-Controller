from __future__ import annotations

import asyncio
import threading
from pathlib import Path

import customtkinter as ctk

from core.timeline import MATCH_SECONDS, format_mmss, parse_mmss
from discord_bot.manager import GVGController

class ControlApp(ctk.CTk):
    def __init__(self, controller: GVGController):
        super().__init__()
        self.controller = controller
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("Majestic GvG Control")
        self.geometry("1360x860")
        self.minsize(1180, 760)
        self.configure(fg_color="#0c0d14")
        self._build_ui()
        self._refresh_loop()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(self, fg_color="#131625", corner_radius=18)
        header.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=18, pady=(18, 10))
        header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header, text="Majestic GvG Control", font=ctk.CTkFont(size=28, weight="bold"), text_color="#f5f7ff").grid(row=0, column=0, padx=18, pady=18, sticky="w")
        self.status_label = ctk.CTkLabel(header, text="6 voice slots", font=ctk.CTkFont(size=16), text_color="#9da6c9")
        self.status_label.grid(row=0, column=1, sticky="e", padx=18)
        left = ctk.CTkFrame(self, fg_color="#111423", corner_radius=18)
        left.grid(row=1, column=0, sticky="nsew", padx=(18, 10), pady=(0, 18))
        ctk.CTkLabel(left, text="Voice channels", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=18, pady=(18, 10))
        for target in self.controller.config["voice_targets"]:
            card = ctk.CTkFrame(left, fg_color="#171a2d", corner_radius=14)
            card.pack(fill="x", padx=14, pady=7)
            ctk.CTkLabel(card, text=f"{target['name']}  •  bot {target['bot_index']}", anchor="w", font=ctk.CTkFont(size=16)).pack(fill="x", padx=14, pady=14)
        center = ctk.CTkFrame(self, fg_color="#0f1220", corner_radius=20)
        center.grid(row=1, column=1, sticky="nsew", padx=0, pady=(0, 18))
        ctk.CTkLabel(center, text="Match countdown", font=ctk.CTkFont(size=18), text_color="#9da6c9").pack(pady=(26, 8))
        self.timer_label = ctk.CTkLabel(center, text="30:00", font=ctk.CTkFont(size=110, weight="bold"), text_color="#ff4fd8")
        self.timer_label.pack(pady=(0, 10))
        self.mode_label = ctk.CTkLabel(center, text="idle", font=ctk.CTkFont(size=18), text_color="#8fe388")
        self.mode_label.pack(pady=(0, 16))
        self.next_event_label = ctk.CTkLabel(center, text="Следующее событие: —", font=ctk.CTkFont(size=18), text_color="#ffffff")
        self.next_event_label.pack(pady=(0, 24))
        right = ctk.CTkFrame(self, fg_color="#111423", corner_radius=18)
        right.grid(row=1, column=2, sticky="nsew", padx=(10, 18), pady=(0, 18))
        ctk.CTkLabel(right, text="Управление", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=18, pady=(18, 12))
        ctk.CTkLabel(right, text="Подготовка: осталось до старта", text_color="#9da6c9").pack(anchor="w", padx=18)
        self.prep_entry = ctk.CTkEntry(right, placeholder_text="05:00")
        self.prep_entry.pack(fill="x", padx=18, pady=(6, 10))
        ctk.CTkButton(right, text="Старт подготовки", fg_color="#8b5cf6", hover_color="#7647e8", command=self.start_prep).pack(fill="x", padx=18)
        ctk.CTkLabel(right, text="Бой: текущее значение таймера", text_color="#9da6c9").pack(anchor="w", padx=18, pady=(18, 0))
        self.live_entry = ctk.CTkEntry(right, placeholder_text="27:35")
        self.live_entry.pack(fill="x", padx=18, pady=(6, 10))
        ctk.CTkButton(right, text="Подхватить бой", fg_color="#ec4899", hover_color="#d83b88", command=self.start_live).pack(fill="x", padx=18)
        ctk.CTkButton(right, text="Пауза", fg_color="#2d3250", command=self.pause).pack(fill="x", padx=18, pady=(20, 8))
        ctk.CTkButton(right, text="Продолжить", fg_color="#243d2c", command=self.resume).pack(fill="x", padx=18, pady=8)
        ctk.CTkButton(right, text="Стоп", fg_color="#5b1f2a", hover_color="#742333", command=self.stop).pack(fill="x", padx=18, pady=8)
        self.test_combo = ctk.CTkComboBox(right, values=list(self.controller.config["audio_map"].keys()))
        self.test_combo.pack(fill="x", padx=18, pady=(20, 8))
        ctk.CTkButton(right, text="Тест звука", fg_color="#2563eb", hover_color="#1d4ed8", command=self.test_audio).pack(fill="x", padx=18)
        bottom = ctk.CTkFrame(self, fg_color="#111423", corner_radius=18)
        bottom.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=18, pady=(0, 18))
        ctk.CTkLabel(bottom, text="Event feed", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=18, pady=(14, 8))
        self.log_box = ctk.CTkTextbox(bottom, height=180, fg_color="#0b0e18")
        self.log_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))

    def start_prep(self):
        try:
            seconds = parse_mmss(self.prep_entry.get().strip() or "05:00")
            self.controller.state.start_prep(seconds)
        except Exception as exc:
            self.controller.state.log.append(f"Ошибка prep: {exc}")

    def start_live(self):
        try:
            seconds = parse_mmss(self.live_entry.get().strip() or "30:00")
            self.controller.state.start_live(seconds)
        except Exception as exc:
            self.controller.state.log.append(f"Ошибка live: {exc}")

    def pause(self):
        self.controller.state.pause()

    def resume(self):
        self.controller.state.resume()

    def stop(self):
        self.controller.state.stop()

    def test_audio(self):
        key = self.test_combo.get().strip()
        if not key:
            return
        asyncio.run_coroutine_threadsafe(self.controller._play_event(key), self.controller.loop)

    def _refresh_loop(self):
        raw_value = self.controller.state.current_value()
        display_value = raw_value if raw_value <= MATCH_SECONDS else raw_value - MATCH_SECONDS
        self.timer_label.configure(text=format_mmss(display_value))
        self.mode_label.configure(text=f"Mode: {self.controller.state.mode}")
        next_event = self.controller.state.next_event()
        if next_event:
            self.next_event_label.configure(text=f"Следующее событие: {next_event.label} ({format_mmss(next_event.countdown_time)})")
        else:
            self.next_event_label.configure(text="Следующее событие: —")
        connected = len(self.controller.workers)
        self.status_label.configure(text=f"{connected}/6 voice workers configured")
        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", "\n".join(self.controller.state.log[-30:]))
        self.after(500, self._refresh_loop)

def run_app(project_root: Path):
    controller = GVGController(project_root)
    loop = asyncio.new_event_loop()
    controller.loop = loop
    def runner():
        asyncio.set_event_loop(loop)
        loop.create_task(controller.start_all())
        loop.run_forever()
    threading.Thread(target=runner, daemon=True).start()
    app = ControlApp(controller)
    app.mainloop()
