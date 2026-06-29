import asyncio
import json
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from core.timeline import format_mmss, parse_mmss
from core.state import MatchState

class VoiceWorker:
    def __init__(self, bot_index: int, token: str, guild_id: int, channel_id: int, ffmpeg_path: str, label: str):
        intents = discord.Intents.default()
        intents.guilds = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.token = token
        self.bot_index = bot_index
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.ffmpeg_path = ffmpeg_path
        self.label = label
        self.voice_client = None

        @self.bot.event
        async def on_ready():
            print(f"Worker {self.bot_index} online as {self.bot.user}")
            await self.ensure_connected()

    async def ensure_connected(self):
        guild = self.bot.get_guild(self.guild_id)
        if guild is None:
            return False
        channel = guild.get_channel(self.channel_id)
        if channel is None or not isinstance(channel, discord.VoiceChannel):
            return False
        vc = guild.voice_client
        if vc and vc.channel.id == self.channel_id:
            self.voice_client = vc
            return True
        if vc:
            await vc.move_to(channel)
            self.voice_client = vc
            return True
        self.voice_client = await channel.connect(reconnect=True)
        return True

    async def play_audio(self, audio_path: str):
        if not Path(audio_path).exists():
            raise FileNotFoundError(audio_path)
        ok = await self.ensure_connected()
        if not ok or self.voice_client is None:
            raise RuntimeError(f"Worker {self.bot_index}: voice connect failed")
        while self.voice_client.is_playing():
            await asyncio.sleep(0.2)
        source = discord.FFmpegPCMAudio(audio_path, executable=self.ffmpeg_path)
        self.voice_client.play(source)

    async def start(self):
        await self.bot.start(self.token)

class GVGController:
    def __init__(self, root_dir: Path):
        load_dotenv(root_dir / ".env")
        self.root_dir = root_dir
        self.config = self._load_config(root_dir / "config" / "config.json")
        self.state = MatchState()
        self.ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
        self.command_prefix = os.getenv("COMMAND_PREFIX", "!")
        self.workers = []
        self.control_bot = None
        self._scheduler_task = None
        self._build_workers()

    def _load_config(self, path: Path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_workers(self):
        guild_id = self.config["guild_id"]
        for target in self.config["voice_targets"]:
            bot_index = target["bot_index"]
            token = os.getenv(f"BOT_TOKEN_{bot_index}", "").strip()
            if not token:
                continue
            self.workers.append(VoiceWorker(bot_index, token, guild_id, target["channel_id"], self.ffmpeg_path, target["name"]))

    def _is_manager(self, member: discord.Member) -> bool:
        role_ids = set(self.config.get("manager_role_ids", []))
        return any(role.id in role_ids for role in member.roles)

    def _is_officer(self, member: discord.Member) -> bool:
        officer_ids = set(self.config.get("officer_role_ids", []))
        return any(role.id in officer_ids for role in member.roles) or self._is_manager(member)

    async def _play_event(self, event_key: str):
        audio_rel = self.config["audio_map"].get(event_key)
        if not audio_rel:
            self.state.log.append(f"Не найден audio_map для {event_key}")
            return
        audio_path = str((self.root_dir / audio_rel).resolve())
        await asyncio.gather(*[worker.play_audio(audio_path) for worker in self.workers], return_exceptions=True)
        self.state.log.append(f"Озвучено: {event_key}")

    async def _scheduler_loop(self):
        while True:
            await asyncio.sleep(0.5)
            if self.state.mode not in {"prep", "live"}:
                continue
            current = self.state.current_value()
            for event in self.state.events:
                if not event.played and current <= event.countdown_time:
                    event.played = True
                    await self._play_event(event.audio_key)
            if current <= 0:
                self.state.log.append("Матч завершён")
                self.state.stop()

    def setup_control_bot(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.message_content = True
        bot = commands.Bot(command_prefix=self.command_prefix, intents=intents)
        self.control_bot = bot

        @bot.event
        async def on_ready():
            await bot.tree.sync(guild=discord.Object(id=self.config["guild_id"]))
            print(f"Control bot online as {bot.user}")

        @bot.hybrid_group(name="gvg", fallback="status")
        async def gvg(ctx: commands.Context):
            current = format_mmss(min(self.state.current_value(), 30 * 60))
            await ctx.reply(f"Статус: {self.state.mode}, таймер: {current}")

        @gvg.command(name="prep")
        async def gvg_prep(ctx: commands.Context, time_value: str):
            if not self._is_manager(ctx.author):
                await ctx.reply("Нет прав")
                return
            seconds = parse_mmss(time_value)
            self.state.start_prep(seconds)
            await ctx.reply(f"Подготовка запущена: осталось {time_value}")

        @gvg.command(name="live")
        async def gvg_live(ctx: commands.Context, timer_value: str):
            if not self._is_manager(ctx.author):
                await ctx.reply("Нет прав")
                return
            seconds = parse_mmss(timer_value)
            self.state.start_live(seconds)
            await ctx.reply(f"Бой подхвачен с таймера {timer_value}")

        @gvg.command(name="stop")
        async def gvg_stop(ctx: commands.Context):
            if not self._is_manager(ctx.author):
                await ctx.reply("Нет прав")
                return
            self.state.stop()
            await ctx.reply("Таймер остановлен")

        @gvg.command(name="pause")
        async def gvg_pause(ctx: commands.Context):
            if not self._is_manager(ctx.author):
                await ctx.reply("Нет прав")
                return
            self.state.pause()
            await ctx.reply("Таймер на паузе")

        @gvg.command(name="resume")
        async def gvg_resume(ctx: commands.Context):
            if not self._is_manager(ctx.author):
                await ctx.reply("Нет прав")
                return
            self.state.resume()
            await ctx.reply("Таймер продолжен")

        @gvg.command(name="test")
        async def gvg_test(ctx: commands.Context, event_key: str):
            if not self._is_officer(ctx.author):
                await ctx.reply("Нет прав")
                return
            await self._play_event(event_key)
            await ctx.reply(f"Тест озвучки: {event_key}")

    async def start_all(self):
        self.setup_control_bot()
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        tasks = [asyncio.create_task(worker.start()) for worker in self.workers]
        control_token = os.getenv("BOT_TOKEN_1", "").strip()
        if not control_token:
            raise RuntimeError("Для control bot используется BOT_TOKEN_1. Он не задан.")
        tasks.append(asyncio.create_task(self.control_bot.start(control_token)))
        await asyncio.gather(*tasks)
