from __future__ import annotations

import json
import math
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen, QPolygonF, QRadialGradient
from PyQt5.QtWidgets import QApplication, QWidget


class SnakeGame(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.base_window_width = 980
        self.base_window_height = 660
        self.base_cell_size = 24
        self.grid_cols = 28
        self.grid_rows = 24

        self.base_board_x = 26
        self.base_board_y = 42
        self.base_panel_gap = 28
        self.base_panel_width = 228
        self.base_right_margin = 26
        self.base_bottom_margin = 28

        self.display_scales = [85, 95, 100, 110, 120, 130, 140]
        self.display_scale = 100

        self.window_width = self.base_window_width
        self.window_height = self.base_window_height
        self.cell_size = self.base_cell_size
        self.board_x = self.base_board_x
        self.board_y = self.base_board_y
        self.board_width = self.grid_cols * self.cell_size
        self.board_height = self.grid_rows * self.cell_size
        self.panel_x = self.board_x + self.board_width + self.base_panel_gap
        self.panel_y = self.base_board_y
        self.panel_width = self.window_width - self.panel_x - self.base_right_margin
        self.panel_height = self.window_height - self.panel_y - self.base_bottom_margin

        self.languages = ["en", "zh", "ja"]
        self.difficulty_levels = ["easy", "mixed", "hard"]
        self.play_modes = ["normal", "invincible"]
        self.snake_color_styles = ["neon", "forest", "sunset", "glacier"]
        self.snake_shape_styles = ["rounded", "square", "circle", "diamond"]
        self.food_styles = ["orb", "crystal", "star", "ring"]

        self.language = "en"
        self.difficulty = "mixed"
        self.play_mode = "normal"
        self.speed_level = 5
        self.snake_color_style = "neon"
        self.snake_shape_style = "rounded"
        self.food_style = "orb"

        self.texts = {
            "en": {
                "window_title": "Neon Snake",
                "game_title": "NEON SNAKE",
                "score": "Score",
                "best_score": "Best Score",
                "length": "Length",
                "best_length": "Best Length",
                "speed": "Speed",
                "difficulty": "Difficulty",
                "mode": "Mode",
                "games": "Games",
                "last": "Last",
                "controls": "Controls",
                "start": "Start",
                "pause": "Pause",
                "resume": "Resume",
                "restart": "Restart",
                "settings": "Settings",
                "close": "Close",
                "language": "Language",
                "snake_color": "Snake Color",
                "snake_shape": "Snake Shape",
                "food_style": "Food Style",
                "speed_level": "Speed",
                "display_scale": "Display Size",
                "scale_level": "Scale",
                "mouse_hint": "Mouse: click board or arrows to steer",
                "keys_hint": "Keys: WASD/Arrows, Space, R, O, Y/N, +/-",
                "settings_hint": "Setting Keys: L/D/M/C/H/F/V and +/-",
                "ready_title": "Ready?",
                "ready_subtitle": "Press Enter / Space / Arrow or Click Start",
                "paused_title": "Paused",
                "paused_subtitle": "Press Space or Click Resume",
                "over_title": "Game Over",
                "over_subtitle": "Press R / Enter or Click Restart",
                "revive_title": "Revive Here?",
                "revive_subtitle": "Invincible mode: continue from a safe spot?",
                "revive_yes": "Revive",
                "revive_no": "End Run",
                "settings_title": "Game Settings",
                "difficulty_easy": "Beginner",
                "difficulty_mixed": "Advanced",
                "difficulty_hard": "Hardcore",
                "mode_normal": "Normal",
                "mode_invincible": "Invincible",
                "lang_en": "English",
                "lang_zh": "Chinese",
                "lang_ja": "Japanese",
                "snake_color_neon": "Neon Cyan",
                "snake_color_forest": "Forest Green",
                "snake_color_sunset": "Sunset Orange",
                "snake_color_glacier": "Glacier Blue",
                "snake_shape_rounded": "Rounded",
                "snake_shape_square": "Square",
                "snake_shape_circle": "Circle",
                "snake_shape_diamond": "Diamond",
                "food_style_orb": "Orb",
                "food_style_crystal": "Crystal",
                "food_style_star": "Star",
                "food_style_ring": "Ring",
                "up": "UP",
                "down": "DOWN",
                "left": "LEFT",
                "right": "RIGHT",
            },
            "zh": {
                "window_title": "霓虹贪吃蛇",
                "game_title": "霓虹贪吃蛇",
                "score": "当前分数",
                "best_score": "历史最高分",
                "length": "当前蛇长",
                "best_length": "历史最长",
                "speed": "速度",
                "difficulty": "难度",
                "mode": "模式",
                "games": "累计局数",
                "last": "上局(分/长)",
                "controls": "操作",
                "start": "开始",
                "pause": "暂停",
                "resume": "继续",
                "restart": "重开",
                "settings": "设置",
                "close": "关闭",
                "language": "语言",
                "snake_color": "蛇身配色",
                "snake_shape": "蛇身形状",
                "food_style": "豆子样式",
                "speed_level": "速度",
                "display_scale": "画面大小",
                "scale_level": "缩放",
                "mouse_hint": "鼠标: 点击棋盘或方向按钮控制",
                "keys_hint": "键盘: WASD/方向键, 空格, R, O, Y/N, +/-",
                "settings_hint": "设置快捷键: L/D/M/C/H/F/V 及 +/-",
                "ready_title": "准备开始?",
                "ready_subtitle": "按 Enter/空格/方向键 或点击开始",
                "paused_title": "已暂停",
                "paused_subtitle": "按空格或点击继续",
                "over_title": "游戏结束",
                "over_subtitle": "按 R/Enter 或点击重开",
                "revive_title": "是否原地复活?",
                "revive_subtitle": "无敌模式失败后将从安全位置继续",
                "revive_yes": "复活继续",
                "revive_no": "结束本局",
                "settings_title": "游戏设置",
                "difficulty_easy": "入门",
                "difficulty_mixed": "进阶",
                "difficulty_hard": "困难",
                "mode_normal": "普通",
                "mode_invincible": "无敌复活",
                "lang_en": "英文",
                "lang_zh": "中文",
                "lang_ja": "日文",
                "snake_color_neon": "霓虹青",
                "snake_color_forest": "森林绿",
                "snake_color_sunset": "落日橙",
                "snake_color_glacier": "冰川蓝",
                "snake_shape_rounded": "圆角块",
                "snake_shape_square": "方块",
                "snake_shape_circle": "圆形",
                "snake_shape_diamond": "菱形",
                "food_style_orb": "光球",
                "food_style_crystal": "水晶",
                "food_style_star": "星芒",
                "food_style_ring": "光环",
                "up": "上",
                "down": "下",
                "left": "左",
                "right": "右",
            },
            "ja": {
                "window_title": "ネオンスネーク",
                "game_title": "ネオンスネーク",
                "score": "現在スコア",
                "best_score": "最高スコア",
                "length": "現在の長さ",
                "best_length": "最長記録",
                "speed": "速度",
                "difficulty": "難易度",
                "mode": "モード",
                "games": "プレイ回数",
                "last": "前回(点/長さ)",
                "controls": "操作",
                "start": "開始",
                "pause": "一時停止",
                "resume": "再開",
                "restart": "リスタート",
                "settings": "設定",
                "close": "閉じる",
                "language": "言語",
                "snake_color": "ヘビの色",
                "snake_shape": "ヘビの形",
                "food_style": "エサスタイル",
                "speed_level": "速度",
                "display_scale": "画面サイズ",
                "scale_level": "拡大率",
                "mouse_hint": "マウス: 盤面/矢印ボタンで操作",
                "keys_hint": "キー: WASD/矢印, Space, R, O, Y/N, +/-",
                "settings_hint": "設定キー: L/D/M/C/H/F/V と +/-",
                "ready_title": "準備OK?",
                "ready_subtitle": "Enter/Space/矢印 または 開始をクリック",
                "paused_title": "一時停止中",
                "paused_subtitle": "Space または 再開をクリック",
                "over_title": "ゲームオーバー",
                "over_subtitle": "R/Enter または リスタートをクリック",
                "revive_title": "その場で復活しますか?",
                "revive_subtitle": "無敵モードでは安全位置から継続可能",
                "revive_yes": "復活",
                "revive_no": "終了",
                "settings_title": "ゲーム設定",
                "difficulty_easy": "ビギナー",
                "difficulty_mixed": "アドバンス",
                "difficulty_hard": "ハード",
                "mode_normal": "通常",
                "mode_invincible": "無敵復活",
                "lang_en": "英語",
                "lang_zh": "中国語",
                "lang_ja": "日本語",
                "snake_color_neon": "ネオンシアン",
                "snake_color_forest": "フォレストグリーン",
                "snake_color_sunset": "サンセットオレンジ",
                "snake_color_glacier": "グレイシャーブルー",
                "snake_shape_rounded": "ラウンド",
                "snake_shape_square": "スクエア",
                "snake_shape_circle": "サークル",
                "snake_shape_diamond": "ダイヤ",
                "food_style_orb": "オーブ",
                "food_style_crystal": "クリスタル",
                "food_style_star": "スター",
                "food_style_ring": "リング",
                "up": "UP",
                "down": "DOWN",
                "left": "LEFT",
                "right": "RIGHT",
            },
        }

        self.snake_palettes = {
            "neon": (QColor("#7CF9FF"), QColor("#0E4F74")),
            "forest": (QColor("#86FFBE"), QColor("#1B6D46")),
            "sunset": (QColor("#FFD39A"), QColor("#CB5D34")),
            "glacier": (QColor("#B5E7FF"), QColor("#2C74A5")),
        }

        self.random = random.Random()
        self.state = "ready"
        self.snake: list[tuple[int, int]] = []
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = (0, 0)
        self.score = 0
        self.food_eaten = 0
        self.move_interval_ms = 130
        self.last_move_time = time.monotonic()
        self.effect_until = 0.0
        self.revive_prompt = False
        self.session_recorded = False
        self.game_start_time = time.monotonic()

        self.best_score = 0
        self.best_length = 4
        self.games_played = 0
        self.total_score = 0
        self.last_score = 0
        self.last_length = 4
        self.last_duration_sec = 0.0

        self.records_file = Path(__file__).with_name(".snake_records.json")
        self.legacy_best_file = Path(__file__).with_name(".snake_best_score")
        self.history: list[dict[str, object]] = []
        self.last_record: dict[str, object] = {
            "timestamp": "",
            "score": 0,
            "best_score": 0,
            "length": 4,
            "duration_sec": 0.0,
            "speed_level": self.speed_level,
            "display_scale": self.display_scale,
            "difficulty": self.difficulty,
            "play_mode": self.play_mode,
            "language": self.language,
        }

        self.settings_open = False
        self.settings_prev_state = "ready"
        self.click_regions: dict[str, QRectF] = {}

        self._load_records()
        self._apply_display_scale()
        self.setWindowTitle(self._t("window_title"))
        self.setFocusPolicy(Qt.StrongFocus)

        self.reset()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(16)

    def _t(self, key: str) -> str:
        selected = self.texts.get(self.language, self.texts["en"])
        if key in selected:
            return selected[key]
        return self.texts["en"].get(key, key)

    def _as_int(self, value: object, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _as_float(self, value: object, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _apply_display_scale(self) -> None:
        ratio = max(0.75, min(1.60, self.display_scale / 100.0))
        self.cell_size = max(18, int(round(self.base_cell_size * ratio)))

        self.board_x = self.base_board_x
        self.board_y = self.base_board_y
        self.board_width = self.grid_cols * self.cell_size
        self.board_height = self.grid_rows * self.cell_size

        content_width = (
            self.board_x
            + self.board_width
            + self.base_panel_gap
            + self.base_panel_width
            + self.base_right_margin
        )
        content_height = self.board_y + self.board_height + self.base_bottom_margin

        self.window_width = max(self.base_window_width, content_width)
        self.window_height = max(self.base_window_height, content_height)

        self.panel_x = self.board_x + self.board_width + self.base_panel_gap
        self.panel_y = self.base_board_y
        self.panel_width = self.window_width - self.panel_x - self.base_right_margin
        self.panel_height = self.window_height - self.panel_y - self.base_bottom_margin

        self.setFixedSize(self.window_width, self.window_height)

    def _normalize_record(self, raw: dict[str, object]) -> dict[str, object]:
        return {
            "timestamp": str(raw.get("timestamp", "")),
            "score": max(0, self._as_int(raw.get("score", 0))),
            "best_score": max(0, self._as_int(raw.get("best_score", raw.get("best", 0)))),
            "length": max(1, self._as_int(raw.get("length", 4))),
            "duration_sec": max(0.0, self._as_float(raw.get("duration_sec", 0.0))),
            "speed_level": min(9, max(1, self._as_int(raw.get("speed_level", self.speed_level)))),
            "display_scale": min(160, max(75, self._as_int(raw.get("display_scale", self.display_scale)))),
            "difficulty": str(raw.get("difficulty", self.difficulty)),
            "play_mode": str(raw.get("play_mode", self.play_mode)),
            "language": str(raw.get("language", self.language)),
        }

    def _load_records(self) -> None:
        payload: dict[str, object] = {}
        if self.records_file.exists():
            try:
                loaded = json.loads(self.records_file.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    payload = loaded
            except (OSError, json.JSONDecodeError):
                payload = {}

        settings = payload.get("settings", {})
        if isinstance(settings, dict):
            loaded_language = str(settings.get("language", self.language))
            if loaded_language in self.languages:
                self.language = loaded_language

            loaded_speed = self._as_int(settings.get("speed_level", self.speed_level))
            self.speed_level = min(9, max(1, loaded_speed))

            loaded_scale = self._as_int(settings.get("display_scale", self.display_scale))
            if loaded_scale in self.display_scales:
                self.display_scale = loaded_scale

            loaded_difficulty = str(settings.get("difficulty", self.difficulty))
            if loaded_difficulty in self.difficulty_levels:
                self.difficulty = loaded_difficulty

            loaded_mode = str(settings.get("play_mode", self.play_mode))
            if loaded_mode in self.play_modes:
                self.play_mode = loaded_mode

            loaded_color = str(settings.get("snake_color_style", self.snake_color_style))
            if loaded_color in self.snake_color_styles:
                self.snake_color_style = loaded_color

            loaded_shape = str(settings.get("snake_shape_style", self.snake_shape_style))
            if loaded_shape in self.snake_shape_styles:
                self.snake_shape_style = loaded_shape

            loaded_food = str(settings.get("food_style", self.food_style))
            if loaded_food in self.food_styles:
                self.food_style = loaded_food

        raw_history = payload.get("history", [])
        if isinstance(raw_history, list):
            for item in raw_history[-300:]:
                if isinstance(item, dict):
                    self.history.append(self._normalize_record(item))
        self.history = self.history[-200:]

        stats = payload.get("stats", {})
        stats = stats if isinstance(stats, dict) else {}

        legacy_best = 0
        if self.legacy_best_file.exists():
            try:
                legacy_best = int(self.legacy_best_file.read_text(encoding="utf-8").strip())
            except (OSError, ValueError):
                legacy_best = 0

        history_best_score = max((self._as_int(item.get("score", 0)) for item in self.history), default=0)
        history_best_length = max((self._as_int(item.get("length", 4)) for item in self.history), default=4)
        history_total_score = sum(self._as_int(item.get("score", 0)) for item in self.history)

        raw_best_score = max(
            self._as_int(stats.get("best_score", 0)),
            self._as_int(payload.get("best_score", 0)),
        )
        self.best_score = max(legacy_best, raw_best_score, history_best_score)

        raw_best_length = self._as_int(stats.get("best_length", payload.get("best_length", 4)))
        self.best_length = max(4, raw_best_length, history_best_length)

        raw_games = max(
            self._as_int(stats.get("games_played", 0)),
            self._as_int(payload.get("games_played", 0)),
        )
        self.games_played = max(len(self.history), raw_games)

        raw_total = self._as_int(stats.get("total_score", payload.get("total_score", 0)))
        self.total_score = max(history_total_score, raw_total)

        raw_last_record = payload.get("last_record")
        if isinstance(raw_last_record, dict):
            self.last_record = self._normalize_record(raw_last_record)
        elif self.history:
            self.last_record = self.history[-1]

        if self.history and not self.last_record.get("timestamp"):
            self.last_record = self.history[-1]

        self.last_score = self._as_int(
            stats.get("last_score", self.last_record.get("score", 0)),
            self._as_int(self.last_record.get("score", 0)),
        )
        self.last_length = self._as_int(
            stats.get("last_length", self.last_record.get("length", 4)),
            self._as_int(self.last_record.get("length", 4)),
        )
        self.last_duration_sec = self._as_float(
            stats.get("last_duration_sec", self.last_record.get("duration_sec", 0.0)),
            self._as_float(self.last_record.get("duration_sec", 0.0)),
        )

        needs_score_migration = False
        for item in self.history:
            item_length = max(1, self._as_int(item.get("length", 4), 4))
            item_score = max(0, self._as_int(item.get("score", 0), 0))
            if item_score > item_length:
                item["score"] = item_length
                needs_score_migration = True

            item_best = self._as_int(item.get("best_score", item_length), item_length)
            if item_best > item_length:
                item["best_score"] = item_length
                needs_score_migration = True

        if self.best_score > self.best_length:
            needs_score_migration = True
        if self.last_score > self.last_length:
            needs_score_migration = True
        if self._as_int(self.last_record.get("score", 0), 0) > self._as_int(
            self.last_record.get("length", self.last_length),
            self.last_length,
        ):
            needs_score_migration = True

        if needs_score_migration:
            self.best_score = self.best_length
            self.last_score = min(self.last_score, self.last_length)
            last_record_length = max(
                1,
                self._as_int(self.last_record.get("length", self.last_length), self.last_length),
            )
            self.last_record["length"] = last_record_length
            self.last_record["score"] = min(
                self._as_int(self.last_record.get("score", self.last_score), self.last_score),
                last_record_length,
            )
            self.last_record["best_score"] = self.best_score
            self.total_score = sum(self._as_int(item.get("score", 0), 0) for item in self.history)
            self._save_records()

    def _save_records(self) -> None:
        payload = {
            "version": 6,
            "stats": {
                "best_score": self.best_score,
                "best_length": self.best_length,
                "games_played": self.games_played,
                "total_score": self.total_score,
                "last_score": self.last_score,
                "last_length": self.last_length,
                "last_duration_sec": round(self.last_duration_sec, 2),
            },
            "last_record": self.last_record,
            "settings": {
                "language": self.language,
                "speed_level": self.speed_level,
                "display_scale": self.display_scale,
                "difficulty": self.difficulty,
                "play_mode": self.play_mode,
                "snake_color_style": self.snake_color_style,
                "snake_shape_style": self.snake_shape_style,
                "food_style": self.food_style,
            },
            "current": {
                "score": self.score,
                "length": len(self.snake),
                "state": self.state,
            },
            "history": self.history[-200:],
        }

        try:
            self.records_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

        try:
            self.legacy_best_file.write_text(str(self.best_score), encoding="utf-8")
        except OSError:
            pass

    def _cycle_option(self, attr: str, options: list[str], delta: int = 1) -> None:
        current = getattr(self, attr)
        try:
            index = options.index(current)
        except ValueError:
            index = 0
        setattr(self, attr, options[(index + delta) % len(options)])

    def _cycle_language(self, delta: int = 1) -> None:
        self._cycle_option("language", self.languages, delta)
        self.setWindowTitle(self._t("window_title"))
        self._save_records()

    def _cycle_difficulty(self, delta: int = 1) -> None:
        self._cycle_option("difficulty", self.difficulty_levels, delta)
        self._recalculate_interval()
        self._save_records()

    def _cycle_play_mode(self, delta: int = 1) -> None:
        self._cycle_option("play_mode", self.play_modes, delta)
        self.revive_prompt = False
        self._save_records()

    def _cycle_display_scale(self, delta: int = 1) -> None:
        try:
            index = self.display_scales.index(self.display_scale)
        except ValueError:
            index = self.display_scales.index(100)
        self.display_scale = self.display_scales[(index + delta) % len(self.display_scales)]
        self._apply_display_scale()
        self._save_records()

    def _cycle_snake_color(self, delta: int = 1) -> None:
        self._cycle_option("snake_color_style", self.snake_color_styles, delta)
        self._save_records()

    def _cycle_snake_shape(self, delta: int = 1) -> None:
        self._cycle_option("snake_shape_style", self.snake_shape_styles, delta)
        self._save_records()

    def _cycle_food_style(self, delta: int = 1) -> None:
        self._cycle_option("food_style", self.food_styles, delta)
        self._save_records()

    def _difficulty_speed_offset(self) -> int:
        if self.difficulty == "easy":
            return 22
        if self.difficulty == "hard":
            return -18
        return 0

    def _base_interval_for_speed(self) -> int:
        return 178 - (self.speed_level - 1) * 12

    def _recalculate_interval(self) -> None:
        base = self._base_interval_for_speed() + self._difficulty_speed_offset()
        self.move_interval_ms = max(54, base - self.food_eaten * 2)

    def _change_speed(self, delta: int) -> None:
        new_level = min(9, max(1, self.speed_level + delta))
        if new_level == self.speed_level:
            return
        self.speed_level = new_level
        self._recalculate_interval()
        self._save_records()

    def _free_neighbor_count(
        self,
        position: tuple[int, int],
        occupied: set[tuple[int, int]],
    ) -> int:
        x, y = position
        count = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx = x + dx
            ny = y + dy
            if 0 <= nx < self.grid_cols and 0 <= ny < self.grid_rows and (nx, ny) not in occupied:
                count += 1
        return count

    def _nearby_body_count(self, position: tuple[int, int]) -> int:
        x, y = position
        count = 0
        for body_x, body_y in self.snake[1:]:
            if abs(body_x - x) + abs(body_y - y) <= 2:
                count += 1
        return count

    def _easy_food_score(
        self,
        position: tuple[int, int],
        occupied: set[tuple[int, int]],
    ) -> float:
        x, y = position
        wall_distance = min(x, self.grid_cols - 1 - x, y, self.grid_rows - 1 - y)
        free_neighbors = self._free_neighbor_count(position, occupied)
        nearby_body = self._nearby_body_count(position)
        head_x, head_y = self.snake[0]
        head_distance = abs(x - head_x) + abs(y - head_y)
        return (
            wall_distance * 3.8
            + free_neighbors * 3.0
            - nearby_body * 2.8
            - abs(head_distance - 9) * 0.35
        )

    def _hard_food_score(
        self,
        position: tuple[int, int],
        occupied: set[tuple[int, int]],
    ) -> float:
        x, y = position
        wall_distance = min(x, self.grid_cols - 1 - x, y, self.grid_rows - 1 - y)
        free_neighbors = self._free_neighbor_count(position, occupied)
        nearby_body = self._nearby_body_count(position)
        head_x, head_y = self.snake[0]
        head_distance = abs(x - head_x) + abs(y - head_y)
        wall_pressure = 6 - min(6, wall_distance)
        return (
            wall_pressure * 3.6
            + nearby_body * 3.0
            + max(0, 9 - head_distance) * 1.4
            - free_neighbors * 1.8
        )

    def _pick_scored_position(
        self,
        free_positions: list[tuple[int, int]],
        score_fn,
        occupied: set[tuple[int, int]],
        top_ratio: float,
    ) -> tuple[int, int]:
        scored = [(score_fn(pos, occupied), pos) for pos in free_positions]
        scored.sort(key=lambda item: item[0], reverse=True)
        take = max(1, int(len(scored) * top_ratio))
        pool = [position for _, position in scored[:take]]
        return self.random.choice(pool)

    def _spawn_food(self) -> tuple[int, int]:
        free_positions = [
            (x, y)
            for x in range(self.grid_cols)
            for y in range(self.grid_rows)
            if (x, y) not in self.snake
        ]
        if not free_positions:
            return 0, 0
        if len(free_positions) == 1:
            return free_positions[0]

        occupied = set(self.snake)
        if self.difficulty == "easy":
            return self._pick_scored_position(
                free_positions,
                self._easy_food_score,
                occupied,
                top_ratio=0.50,
            )
        if self.difficulty == "hard":
            return self._pick_scored_position(
                free_positions,
                self._hard_food_score,
                occupied,
                top_ratio=0.23,
            )

        roll = self.random.random()
        if roll < 0.45:
            return self._pick_scored_position(
                free_positions,
                self._easy_food_score,
                occupied,
                top_ratio=0.45,
            )
        if roll < 0.72:
            return self.random.choice(free_positions)
        return self._pick_scored_position(
            free_positions,
            self._hard_food_score,
            occupied,
            top_ratio=0.26,
        )

    def _record_current_session(self, reason: str, force: bool = False) -> None:
        if self.session_recorded:
            return

        duration = max(0.0, time.monotonic() - self.game_start_time)
        current_length = len(self.snake)
        if not force and self.score <= 0 and current_length <= 4 and duration < 1.0:
            return

        self.best_score = max(self.best_score, self.score)
        self.best_length = max(self.best_length, current_length)
        self.games_played += 1
        self.total_score += self.score
        self.last_score = self.score
        self.last_length = current_length
        self.last_duration_sec = round(duration, 2)

        self.last_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": self.score,
            "best_score": self.best_score,
            "length": current_length,
            "duration_sec": self.last_duration_sec,
            "speed_level": self.speed_level,
            "display_scale": self.display_scale,
            "difficulty": self.difficulty,
            "play_mode": self.play_mode,
            "language": self.language,
            "reason": reason,
        }
        self.history.append(self.last_record.copy())
        self.history = self.history[-200:]
        self.session_recorded = True
        self._save_records()

    def reset(self) -> None:
        center_x = self.grid_cols // 2
        center_y = self.grid_rows // 2
        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
            (center_x - 3, center_y),
        ]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self._spawn_food()
        self.state = "ready"
        self.score = 0
        self.food_eaten = 0
        self._recalculate_interval()
        self.last_move_time = time.monotonic()
        self.effect_until = 0.0
        self.revive_prompt = False
        self.game_start_time = time.monotonic()
        self.session_recorded = False
        self._save_records()

    def start(self) -> None:
        if self.state in {"ready", "game_over"}:
            if self.state == "game_over":
                self.reset()
            self.state = "running"
            self.last_move_time = time.monotonic()
            self._save_records()

    def _set_game_over(self) -> None:
        self.revive_prompt = False
        self.state = "game_over"
        self.best_score = max(self.best_score, self.score)
        self.best_length = max(self.best_length, len(self.snake))
        self._record_current_session("game_over", force=True)
        self._save_records()

    def _trigger_failure(self) -> None:
        if self.play_mode == "invincible":
            self.revive_prompt = True
            self.state = "paused"
            self.last_move_time = time.monotonic()
            self._save_records()
            return
        self._set_game_over()

    def _safe_revive_snake(self) -> None:
        original_length = max(4, len(self.snake))
        target_length = min(original_length, max(self.grid_cols, self.grid_rows) - 4)
        previous_head = self.snake[0] if self.snake else (self.grid_cols // 2, self.grid_rows // 2)
        candidates: list[tuple[float, list[tuple[int, int]], tuple[int, int]]] = []

        def add_candidate(segments: list[tuple[int, int]], direction: tuple[int, int]) -> None:
            occupied = set(segments)
            head_x, head_y = segments[0]
            wall_distance = min(
                head_x,
                self.grid_cols - 1 - head_x,
                head_y,
                self.grid_rows - 1 - head_y,
            )
            free_neighbors = self._free_neighbor_count((head_x, head_y), occupied)
            head_distance = abs(head_x - previous_head[0]) + abs(head_y - previous_head[1])
            score = wall_distance * 4.0 + free_neighbors * 3.0 + head_distance * 0.2
            candidates.append((score, segments, direction))

        for length in range(target_length, 3, -1):
            row_choices = [self.grid_rows // 2, self.grid_rows // 2 - 4, self.grid_rows // 2 + 4]
            col_choices = [self.grid_cols // 2, self.grid_cols // 2 - 4, self.grid_cols // 2 + 4]

            if length <= self.grid_cols - 4:
                left = (self.grid_cols - length) // 2
                for y in row_choices:
                    if 1 <= y <= self.grid_rows - 2:
                        line = [(left + i, y) for i in range(length)]
                        add_candidate(list(reversed(line)), (1, 0))
                        add_candidate(line, (-1, 0))

            if length <= self.grid_rows - 4:
                top = (self.grid_rows - length) // 2
                for x in col_choices:
                    if 1 <= x <= self.grid_cols - 2:
                        line = [(x, top + i) for i in range(length)]
                        add_candidate(list(reversed(line)), (0, 1))
                        add_candidate(line, (0, -1))

            if candidates:
                break

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            pool = candidates[: min(6, len(candidates))]
            _, segments, direction = self.random.choice(pool)
            self.snake = segments
            self.direction = direction
            self.next_direction = direction
        else:
            center_x = self.grid_cols // 2
            center_y = self.grid_rows // 2
            self.snake = [
                (center_x, center_y),
                (center_x - 1, center_y),
                (center_x - 2, center_y),
                (center_x - 3, center_y),
            ]
            self.direction = (1, 0)
            self.next_direction = (1, 0)

        self.food_eaten = max(0, len(self.snake) - 4)
        self._recalculate_interval()
        self.food = self._spawn_food()
        self.effect_until = 0.0
        self.last_move_time = time.monotonic()

    def _resolve_revive(self, accept: bool) -> None:
        if not self.revive_prompt:
            return
        self.revive_prompt = False
        if accept:
            self._safe_revive_snake()
            self.state = "running"
            self.last_move_time = time.monotonic()
            self._save_records()
            return
        self._set_game_over()

    def _queue_direction(self, new_direction: tuple[int, int]) -> None:
        if self.state in {"ready", "game_over"}:
            self.start()
        elif self.state == "paused" and not self.settings_open and not self.revive_prompt:
            self.state = "running"
            self.last_move_time = time.monotonic()

        if len(self.snake) > 1:
            if (
                new_direction[0] == -self.direction[0]
                and new_direction[1] == -self.direction[1]
            ):
                return
        self.next_direction = new_direction

    def _step(self) -> None:
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        delta_x, delta_y = self.direction
        next_head = (head_x + delta_x, head_y + delta_y)

        if (
            next_head[0] < 0
            or next_head[0] >= self.grid_cols
            or next_head[1] < 0
            or next_head[1] >= self.grid_rows
        ):
            self._trigger_failure()
            return

        is_growing = next_head == self.food
        body_to_check = self.snake if is_growing else self.snake[:-1]
        if next_head in body_to_check:
            self._trigger_failure()
            return

        self.snake.insert(0, next_head)
        if is_growing:
            self.score += 1
            self.food_eaten += 1
            self.food = self._spawn_food()
            self._recalculate_interval()
            self.effect_until = time.monotonic() + 0.12
            self.best_score = max(self.best_score, self.score)
            self.best_length = max(self.best_length, len(self.snake))
            self._save_records()
        else:
            self.snake.pop()

    def _update_game(self) -> None:
        if self.state != "running" or self.settings_open:
            return

        interval_seconds = self.move_interval_ms / 1000.0
        now = time.monotonic()
        max_steps = 5

        while now - self.last_move_time >= interval_seconds and max_steps > 0:
            self.last_move_time += interval_seconds
            self._step()
            if self.state != "running":
                break
            max_steps -= 1

    def _tick(self) -> None:
        self._update_game()
        self.update()

    def _toggle_pause_or_start(self) -> None:
        if self.settings_open or self.revive_prompt:
            return
        if self.state == "running":
            self.state = "paused"
            self._save_records()
        elif self.state == "paused":
            self.state = "running"
            self.last_move_time = time.monotonic()
            self._save_records()
        else:
            self.start()

    def _restart_game(self) -> None:
        if self.state in {"running", "paused"}:
            self._record_current_session("restart")
        self.revive_prompt = False
        self.reset()
        self.start()

    def _open_settings(self) -> None:
        if self.settings_open or self.revive_prompt:
            return
        self.settings_open = True
        self.settings_prev_state = self.state
        if self.state == "running":
            self.state = "paused"
        self._save_records()

    def _close_settings(self) -> None:
        if not self.settings_open:
            return
        self.settings_open = False
        if self.settings_prev_state == "running" and self.state == "paused":
            self.state = "running"
            self.last_move_time = time.monotonic()
        elif self.settings_prev_state in {"ready", "paused", "game_over"}:
            self.state = self.settings_prev_state
        self._save_records()

    def keyPressEvent(self, event) -> None:
        key = event.key()

        if self.revive_prompt:
            if key in {Qt.Key_Y, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space}:
                self._resolve_revive(True)
                return
            if key == Qt.Key_N:
                self._resolve_revive(False)
                return
            if key == Qt.Key_R:
                self._restart_game()
                return
            if key == Qt.Key_Escape:
                self.close()
                return
            return

        if key == Qt.Key_O:
            if self.settings_open:
                self._close_settings()
            else:
                self._open_settings()
            return

        if self.settings_open:
            if key in {Qt.Key_Escape, Qt.Key_Return, Qt.Key_Enter}:
                self._close_settings()
                return
            if key == Qt.Key_L:
                self._cycle_language()
                return
            if key == Qt.Key_D:
                self._cycle_difficulty()
                return
            if key == Qt.Key_M:
                self._cycle_play_mode()
                return
            if key == Qt.Key_C:
                self._cycle_snake_color()
                return
            if key == Qt.Key_H:
                self._cycle_snake_shape()
                return
            if key == Qt.Key_F:
                self._cycle_food_style()
                return
            if key == Qt.Key_V:
                self._cycle_display_scale()
                return
            if key in {Qt.Key_Minus, Qt.Key_BracketLeft}:
                self._change_speed(-1)
                return
            if key in {Qt.Key_Equal, Qt.Key_Plus, Qt.Key_BracketRight}:
                self._change_speed(1)
                return
            return

        directions = {
            Qt.Key_Up: (0, -1),
            Qt.Key_W: (0, -1),
            Qt.Key_Down: (0, 1),
            Qt.Key_S: (0, 1),
            Qt.Key_Left: (-1, 0),
            Qt.Key_A: (-1, 0),
            Qt.Key_Right: (1, 0),
            Qt.Key_D: (1, 0),
        }
        if key in directions:
            self._queue_direction(directions[key])
            return

        if key in {Qt.Key_Return, Qt.Key_Enter}:
            if self.state in {"ready", "game_over"}:
                self.start()
            return

        if key == Qt.Key_Space:
            self._toggle_pause_or_start()
            return

        if key == Qt.Key_R:
            self._restart_game()
            return

        if key in {Qt.Key_Minus, Qt.Key_BracketLeft}:
            self._change_speed(-1)
            return

        if key in {Qt.Key_Equal, Qt.Key_Plus, Qt.Key_BracketRight}:
            self._change_speed(1)
            return

        if key == Qt.Key_Escape:
            self.close()

    def _board_rect(self) -> QRectF:
        return QRectF(self.board_x, self.board_y, self.board_width, self.board_height)

    def _handle_board_click(self, point: QPointF) -> None:
        cell_x = int((point.x() - self.board_x) // self.cell_size)
        cell_y = int((point.y() - self.board_y) // self.cell_size)
        if not (0 <= cell_x < self.grid_cols and 0 <= cell_y < self.grid_rows):
            return

        head_x, head_y = self.snake[0]
        dx = cell_x - head_x
        dy = cell_y - head_y
        if dx == 0 and dy == 0:
            return

        if abs(dx) >= abs(dy):
            direction = (1, 0) if dx > 0 else (-1, 0)
        else:
            direction = (0, 1) if dy > 0 else (0, -1)
        self._queue_direction(direction)

    def _handle_click_action(self, action: str) -> None:
        if action == "action_start_pause":
            self._toggle_pause_or_start()
            return
        if action == "action_restart":
            self._restart_game()
            return
        if action == "action_settings":
            self._open_settings()
            return
        if action == "speed_minus":
            self._change_speed(-1)
            return
        if action == "speed_plus":
            self._change_speed(1)
            return
        if action == "settings_close":
            self._close_settings()
            return
        if action == "settings_lang_prev":
            self._cycle_language(-1)
            return
        if action == "settings_lang_next":
            self._cycle_language(1)
            return
        if action == "settings_diff_prev":
            self._cycle_difficulty(-1)
            return
        if action == "settings_diff_next":
            self._cycle_difficulty(1)
            return
        if action == "settings_mode_prev":
            self._cycle_play_mode(-1)
            return
        if action == "settings_mode_next":
            self._cycle_play_mode(1)
            return
        if action == "settings_scale_prev":
            self._cycle_display_scale(-1)
            return
        if action == "settings_scale_next":
            self._cycle_display_scale(1)
            return
        if action == "settings_color_prev":
            self._cycle_snake_color(-1)
            return
        if action == "settings_color_next":
            self._cycle_snake_color(1)
            return
        if action == "settings_shape_prev":
            self._cycle_snake_shape(-1)
            return
        if action == "settings_shape_next":
            self._cycle_snake_shape(1)
            return
        if action == "settings_food_prev":
            self._cycle_food_style(-1)
            return
        if action == "settings_food_next":
            self._cycle_food_style(1)
            return
        if action == "settings_speed_minus":
            self._change_speed(-1)
            return
        if action == "settings_speed_plus":
            self._change_speed(1)
            return
        if action == "revive_yes":
            self._resolve_revive(True)
            return
        if action == "revive_no":
            self._resolve_revive(False)
            return

        direction_map = {
            "dir_up": (0, -1),
            "dir_down": (0, 1),
            "dir_left": (-1, 0),
            "dir_right": (1, 0),
        }
        if action in direction_map:
            self._queue_direction(direction_map[action])

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.LeftButton:
            return

        point = QPointF(event.pos())
        if self.revive_prompt:
            for action, rect in self.click_regions.items():
                if action in {"revive_yes", "revive_no"} and rect.contains(point):
                    self._handle_click_action(action)
                    return
            return

        if self.settings_open:
            for action, rect in self.click_regions.items():
                if action.startswith("settings_") and rect.contains(point):
                    self._handle_click_action(action)
                    return
            return

        if self._board_rect().contains(point):
            self._handle_board_click(point)
            return

        for action, rect in self.click_regions.items():
            if not action.startswith("settings_") and rect.contains(point):
                self._handle_click_action(action)
                return

    def closeEvent(self, event) -> None:
        if self.state in {"running", "paused"}:
            self._record_current_session("quit")
        self._save_records()
        super().closeEvent(event)

    def _mix_color(self, start: QColor, end: QColor, ratio: float) -> QColor:
        ratio = max(0.0, min(1.0, ratio))
        red = round(start.red() + (end.red() - start.red()) * ratio)
        green = round(start.green() + (end.green() - start.green()) * ratio)
        blue = round(start.blue() + (end.blue() - start.blue()) * ratio)
        return QColor(red, green, blue)

    def _draw_button(
        self,
        painter: QPainter,
        key: str,
        rect: QRectF,
        text: str,
        active: bool = False,
    ) -> None:
        self.click_regions[key] = rect
        fill = QColor("#1A4A66") if active else QColor("#14374D")
        border = QColor("#66ADCF") if active else QColor("#3C7191")

        painter.setPen(QPen(border, 1.5))
        painter.setBrush(fill)
        painter.drawRoundedRect(rect, 8, 8)

        if min(rect.width(), rect.height()) <= 28:
            font_size = 9
        elif rect.height() <= 34:
            font_size = 10
        else:
            font_size = 12
        painter.setFont(QFont("Avenir Next", font_size, QFont.DemiBold))
        painter.setPen(QColor("#E8FCFF"))
        painter.drawText(rect, Qt.AlignCenter, text)

    def _draw_background(self, painter: QPainter) -> None:
        gradient = QLinearGradient(0, 0, 0, self.window_height)
        gradient.setColorAt(0, QColor("#0A1730"))
        gradient.setColorAt(1, QColor("#061018"))
        painter.fillRect(self.rect(), gradient)

        pen = QPen(QColor(109, 159, 191, 22))
        pen.setWidth(1)
        painter.setPen(pen)
        for index in range(-6, 20):
            x0 = index * 80
            painter.drawLine(x0, 0, x0 + 260, self.window_height)

    def _draw_board(self, painter: QPainter) -> None:
        outer = QRectF(
            self.board_x - 8,
            self.board_y - 8,
            self.board_width + 16,
            self.board_height + 16,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#2B5776"))
        painter.drawRoundedRect(outer, 16, 16)

        inner = self._board_rect()
        painter.setBrush(QColor("#0F2232"))
        painter.drawRoundedRect(inner, 14, 14)

        painter.setPen(QPen(QColor(59, 94, 120, 110), 1))
        for col in range(1, self.grid_cols):
            x = self.board_x + col * self.cell_size
            painter.drawLine(x, self.board_y + 2, x, self.board_y + self.board_height - 2)
        for row in range(1, self.grid_rows):
            y = self.board_y + row * self.cell_size
            painter.drawLine(self.board_x + 2, y, self.board_x + self.board_width - 2, y)

    def _draw_panel(self, painter: QPainter) -> None:
        panel_rect = QRectF(
            self.panel_x,
            self.panel_y,
            self.panel_width,
            self.panel_height,
        )
        painter.setPen(QPen(QColor("#3A6787"), 2))
        painter.setBrush(QColor("#0D1D2B"))
        painter.drawRoundedRect(panel_rect, 14, 14)

    def _food_center(self) -> QPointF:
        food_x, food_y = self.food
        px = self.board_x + food_x * self.cell_size
        py = self.board_y + food_y * self.cell_size
        return QPointF(px + self.cell_size / 2, py + self.cell_size / 2)

    def _draw_food_orb(self, painter: QPainter, center: QPointF, now: float) -> None:
        pulse = (math.sin(now * 7.0) + 1.0) * 0.5
        outer_radius = self.cell_size * 0.45 + pulse * 4
        gradient = QRadialGradient(center, outer_radius)
        gradient.setColorAt(0, QColor(255, 189, 189, 220))
        gradient.setColorAt(1, QColor(255, 109, 109, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(center, outer_radius, outer_radius)

        inner_radius = self.cell_size * 0.30
        painter.setBrush(QColor("#FF6666"))
        painter.drawEllipse(center, inner_radius, inner_radius)

    def _draw_food_crystal(self, painter: QPainter, center: QPointF, now: float) -> None:
        pulse = (math.sin(now * 6.0) + 1.0) * 0.5
        glow_radius = self.cell_size * 0.55 + pulse * 3
        glow = QRadialGradient(center, glow_radius)
        glow.setColorAt(0, QColor(255, 210, 210, 200))
        glow.setColorAt(1, QColor(255, 100, 100, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(center, glow_radius, glow_radius)

        half = self.cell_size * 0.34
        polygon = QPolygonF(
            [
                QPointF(center.x(), center.y() - half),
                QPointF(center.x() + half, center.y()),
                QPointF(center.x(), center.y() + half),
                QPointF(center.x() - half, center.y()),
            ]
        )
        painter.setBrush(QColor("#FF6D6D"))
        painter.drawPolygon(polygon)

    def _draw_food_star(self, painter: QPainter, center: QPointF, now: float) -> None:
        pulse = (math.sin(now * 8.0) + 1.0) * 0.5
        outer = self.cell_size * (0.38 + pulse * 0.05)
        inner = outer * 0.46
        points = []
        for idx in range(10):
            angle = -math.pi / 2 + idx * math.pi / 5
            radius = outer if idx % 2 == 0 else inner
            points.append(
                QPointF(
                    center.x() + math.cos(angle) * radius,
                    center.y() + math.sin(angle) * radius,
                )
            )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 229, 124, 235))
        painter.drawPolygon(QPolygonF(points))
        painter.setBrush(QColor(255, 135, 92, 220))
        painter.drawEllipse(center, self.cell_size * 0.12, self.cell_size * 0.12)

    def _draw_food_ring(self, painter: QPainter, center: QPointF, now: float) -> None:
        pulse = (math.sin(now * 9.0) + 1.0) * 0.5
        outer = self.cell_size * (0.36 + pulse * 0.04)
        inner = outer * 0.52
        painter.setPen(QPen(QColor("#FFB5A1"), 2.6))
        painter.setBrush(QColor(255, 128, 110, 35))
        painter.drawEllipse(center, outer, outer)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#FF6A6A"))
        painter.drawEllipse(center, inner, inner)
        painter.setBrush(QColor("#0F2232"))
        painter.drawEllipse(center, inner * 0.45, inner * 0.45)

    def _draw_food(self, painter: QPainter, now: float) -> None:
        center = self._food_center()
        if self.food_style == "crystal":
            self._draw_food_crystal(painter, center, now)
            return
        if self.food_style == "star":
            self._draw_food_star(painter, center, now)
            return
        if self.food_style == "ring":
            self._draw_food_ring(painter, center, now)
            return
        self._draw_food_orb(painter, center, now)

    def _draw_segment_shape(self, painter: QPainter, rect: QRectF, color: QColor) -> None:
        painter.setBrush(color)
        if self.snake_shape_style == "square":
            painter.drawRect(rect)
            return
        if self.snake_shape_style == "circle":
            painter.drawEllipse(rect)
            return
        if self.snake_shape_style == "diamond":
            center = rect.center()
            polygon = QPolygonF(
                [
                    QPointF(center.x(), rect.top()),
                    QPointF(rect.right(), center.y()),
                    QPointF(center.x(), rect.bottom()),
                    QPointF(rect.left(), center.y()),
                ]
            )
            painter.drawPolygon(polygon)
            return
        painter.drawRoundedRect(rect, 6, 6)

    def _draw_snake(self, painter: QPainter) -> None:
        head_color, tail_color = self.snake_palettes.get(
            self.snake_color_style,
            self.snake_palettes["neon"],
        )

        painter.setPen(Qt.NoPen)
        for index, (x, y) in enumerate(self.snake):
            ratio = index / max(1, len(self.snake) - 1)
            color = self._mix_color(head_color, tail_color, ratio)
            px = self.board_x + x * self.cell_size
            py = self.board_y + y * self.cell_size
            padding = 2 if index == 0 else 3
            rect = QRectF(
                px + padding,
                py + padding,
                self.cell_size - padding * 2,
                self.cell_size - padding * 2,
            )
            self._draw_segment_shape(painter, rect, color)

        head_x, head_y = self.snake[0]
        base_x = self.board_x + head_x * self.cell_size
        base_y = self.board_y + head_y * self.cell_size
        painter.setBrush(QColor("#052933"))

        front = self.cell_size * 0.67
        back = self.cell_size * 0.33
        side_low = self.cell_size * 0.30
        side_high = self.cell_size * 0.63
        eye_size = max(3.0, self.cell_size * 0.16)

        if self.direction == (1, 0):
            eyes = [(front, side_low), (front, side_high)]
        elif self.direction == (-1, 0):
            eyes = [(back, side_low), (back, side_high)]
        elif self.direction == (0, -1):
            eyes = [(side_low, back), (side_high, back)]
        else:
            eyes = [(side_low, front), (side_high, front)]

        for offset_x, offset_y in eyes:
            painter.drawEllipse(QRectF(base_x + offset_x, base_y + offset_y, eye_size, eye_size))

    def _draw_hud(self, painter: QPainter) -> None:
        painter.setPen(QColor("#E6FAFF"))
        painter.setFont(QFont("Avenir Next", 24, QFont.Bold))
        painter.drawText(
            QRectF(self.panel_x + 24, self.panel_y + 10, self.panel_width - 48, 44),
            Qt.AlignLeft | Qt.AlignVCenter,
            self._t("game_title"),
        )

        content_left = self.panel_x + 16
        content_right = self.panel_x + self.panel_width - 16
        label_width = 104
        value_left = content_left + label_width + 6
        value_width = max(44.0, content_right - value_left)

        difficulty_name = self._t("difficulty_" + self.difficulty)
        last_value = f"{self.last_score}/{self.last_length}" if self.games_played > 0 else "0/0"
        stats = [
            (self._t("score"), str(self.score)),
            (self._t("best_score"), str(self.best_score)),
            (self._t("length"), str(len(self.snake))),
            (self._t("best_length"), str(self.best_length)),
            (self._t("difficulty"), difficulty_name),
            (self._t("games"), str(self.games_played)),
            (self._t("last"), last_value),
        ]

        title_font = QFont("Avenir Next", 10, QFont.Bold)
        value_font = QFont("Avenir Next", 14, QFont.Bold)
        y = self.panel_y + 72

        for label, value in stats:
            painter.setFont(title_font)
            painter.setPen(QColor("#9CC6D8"))
            painter.drawText(
                QRectF(content_left, y, label_width, 28),
                Qt.AlignLeft | Qt.AlignVCenter,
                label,
            )
            painter.setFont(value_font)
            painter.setPen(QColor("#E6FAFF"))
            painter.drawText(
                QRectF(value_left, y - 1, value_width, 30),
                Qt.AlignRight | Qt.AlignVCenter,
                value,
            )
            y += 36

        button_x = content_left
        button_w = content_right - content_left
        button_y = self.panel_y + 318

        if self.state == "running":
            primary_label = self._t("pause")
            primary_active = True
        elif self.state == "paused":
            primary_label = self._t("resume")
            primary_active = True
        else:
            primary_label = self._t("start")
            primary_active = False

        self._draw_button(
            painter,
            "action_start_pause",
            QRectF(button_x, button_y, button_w, 34),
            primary_label,
            active=primary_active,
        )
        self._draw_button(
            painter,
            "action_restart",
            QRectF(button_x, button_y + 42, button_w, 34),
            self._t("restart"),
        )
        self._draw_button(
            painter,
            "action_settings",
            QRectF(button_x, button_y + 84, button_w, 34),
            self._t("settings"),
        )

        minus_rect = QRectF(button_x, button_y + 126, 44, 32)
        plus_rect = QRectF(button_x + button_w - 44, button_y + 126, 44, 32)
        value_rect = QRectF(button_x + 52, button_y + 126, button_w - 104, 32)
        self._draw_button(painter, "speed_minus", minus_rect, "-")
        self._draw_button(painter, "speed_plus", plus_rect, "+")

        painter.setPen(QPen(QColor("#3C7191"), 1.5))
        painter.setBrush(QColor("#122E42"))
        painter.drawRoundedRect(value_rect, 8, 8)
        painter.setFont(QFont("Avenir Next", 11, QFont.DemiBold))
        painter.setPen(QColor("#E8FCFF"))
        painter.drawText(
            value_rect,
            Qt.AlignCenter,
            f"{self._t('speed_level')} {self.speed_level}",
        )

        painter.setFont(QFont("Avenir Next", 11, QFont.DemiBold))
        painter.setPen(QColor("#9CC6D8"))
        painter.drawText(
            QRectF(button_x, button_y + 160, button_w, 18),
            Qt.AlignCenter,
            self._t("controls"),
        )

        key_size = 22
        key_gap = 10
        center_x = button_x + button_w / 2
        lower_row_top = button_y + 212
        down_rect = QRectF(center_x - key_size / 2, lower_row_top, key_size, key_size)
        up_rect = QRectF(
            down_rect.x(),
            lower_row_top - key_size - key_gap,
            key_size,
            key_size,
        )
        left_rect = QRectF(
            down_rect.x() - key_size - key_gap,
            lower_row_top,
            key_size,
            key_size,
        )
        right_rect = QRectF(
            down_rect.x() + key_size + key_gap,
            lower_row_top,
            key_size,
            key_size,
        )

        self._draw_button(painter, "dir_up", up_rect, "^")
        self._draw_button(painter, "dir_left", left_rect, "<")
        self._draw_button(painter, "dir_right", right_rect, ">")
        self._draw_button(painter, "dir_down", down_rect, "v")

        painter.setFont(QFont("Avenir Next", 9))
        painter.setPen(QColor("#88B6CB"))
        hint_y = self.panel_y + self.panel_height - 36
        painter.drawText(
            QRectF(button_x, hint_y, button_w, 18),
            Qt.AlignCenter,
            self._t("mouse_hint"),
        )
        painter.drawText(
            QRectF(button_x, hint_y + 18, button_w, 18),
            Qt.AlignCenter,
            self._t("keys_hint"),
        )

    def _draw_effect(self, painter: QPainter, now: float) -> None:
        return

    def _draw_revive_overlay(self, painter: QPainter) -> None:
        rect_h = 164
        rect = QRectF(
            self.board_x + 80,
            self.board_y + (self.board_height - rect_h) / 2,
            self.board_width - 160,
            rect_h,
        )
        painter.setPen(QPen(QColor("#3A6787"), 2))
        painter.setBrush(QColor(4, 16, 24, 228))
        painter.drawRoundedRect(rect, 14, 14)

        painter.setFont(QFont("Avenir Next", 28, QFont.Bold))
        painter.setPen(QColor("#FFD37A"))
        painter.drawText(
            QRectF(rect.x(), rect.y() + 18, rect.width(), 42),
            Qt.AlignCenter,
            self._t("revive_title"),
        )

        painter.setFont(QFont("Avenir Next", 13))
        painter.setPen(QColor("#9CC6D8"))
        painter.drawText(
            QRectF(rect.x(), rect.y() + 62, rect.width(), 24),
            Qt.AlignCenter,
            self._t("revive_subtitle"),
        )

        button_w = 138
        button_h = 34
        gap = 24
        total_w = button_w * 2 + gap
        start_x = rect.center().x() - total_w / 2
        button_y = rect.y() + 104

        yes_rect = QRectF(start_x, button_y, button_w, button_h)
        no_rect = QRectF(start_x + button_w + gap, button_y, button_w, button_h)
        self._draw_button(painter, "revive_yes", yes_rect, self._t("revive_yes"), active=True)
        self._draw_button(painter, "revive_no", no_rect, self._t("revive_no"))

    def _draw_overlay(self, painter: QPainter) -> None:
        if self.settings_open:
            return

        if self.revive_prompt:
            self._draw_revive_overlay(painter)
            return

        if self.state == "running":
            return

        if self.state == "ready":
            title = self._t("ready_title")
            subtitle = self._t("ready_subtitle")
            text_color = QColor("#E6FAFF")
        elif self.state == "paused":
            title = self._t("paused_title")
            subtitle = self._t("paused_subtitle")
            text_color = QColor("#FFD37A")
        else:
            title = self._t("over_title")
            subtitle = self._t("over_subtitle")
            text_color = QColor("#FF7E7E")

        rect = QRectF(
            self.board_x + 90,
            self.board_y + (self.board_height - 136) / 2,
            self.board_width - 180,
            136,
        )
        painter.setPen(QPen(QColor("#3A6787"), 2))
        painter.setBrush(QColor(4, 16, 24, 224))
        painter.drawRoundedRect(rect, 14, 14)

        painter.setFont(QFont("Avenir Next", 30, QFont.Bold))
        painter.setPen(text_color)
        painter.drawText(
            QRectF(rect.x(), rect.y() + 18, rect.width(), 56),
            Qt.AlignCenter,
            title,
        )

        painter.setFont(QFont("Avenir Next", 14))
        painter.setPen(QColor("#9CC6D8"))
        painter.drawText(
            QRectF(rect.x(), rect.y() + 78, rect.width(), 30),
            Qt.AlignCenter,
            subtitle,
        )

    def _draw_setting_row(
        self,
        painter: QPainter,
        y: float,
        label: str,
        value: str,
        prev_key: str,
        next_key: str,
    ) -> None:
        modal_w = 640
        mx = (self.window_width - modal_w) / 2
        row_rect = QRectF(mx + 28, y, modal_w - 56, 46)
        painter.setPen(QPen(QColor("#3F6D8B"), 1.4))
        painter.setBrush(QColor("#102433"))
        painter.drawRoundedRect(row_rect, 10, 10)

        next_rect = QRectF(row_rect.right() - 34, row_rect.y() + 7, 34, 32)
        value_rect = QRectF(next_rect.x() - 158, row_rect.y() + 7, 150, 32)
        prev_rect = QRectF(value_rect.x() - 42, row_rect.y() + 7, 34, 32)
        label_width = max(80.0, prev_rect.x() - row_rect.x() - 28)

        painter.setFont(QFont("Avenir Next", 12, QFont.Bold))
        painter.setPen(QColor("#9CC6D8"))
        painter.drawText(
            QRectF(row_rect.x() + 16, row_rect.y(), label_width, row_rect.height()),
            Qt.AlignLeft | Qt.AlignVCenter,
            label,
        )

        self._draw_button(painter, prev_key, prev_rect, "<")
        self._draw_button(painter, next_key, next_rect, ">")

        painter.setPen(QPen(QColor("#3C7191"), 1.5))
        painter.setBrush(QColor("#122E42"))
        painter.drawRoundedRect(value_rect, 8, 8)
        painter.setFont(QFont("Avenir Next", 10, QFont.DemiBold))
        painter.setPen(QColor("#E8FCFF"))
        painter.drawText(value_rect, Qt.AlignCenter, value)

    def _draw_settings_overlay(self, painter: QPainter) -> None:
        painter.fillRect(self.rect(), QColor(3, 12, 18, 168))

        modal_w = 640
        modal_h = 604
        mx = (self.window_width - modal_w) / 2
        my = (self.window_height - modal_h) / 2
        modal = QRectF(mx, my, modal_w, modal_h)

        painter.setPen(QPen(QColor("#4D7A98"), 2))
        painter.setBrush(QColor("#0B1A26"))
        painter.drawRoundedRect(modal, 16, 16)

        painter.setPen(QColor("#E6FAFF"))
        painter.setFont(QFont("Avenir Next", 24, QFont.Bold))
        painter.drawText(
            QRectF(mx + 24, my + 16, modal_w - 180, 42),
            Qt.AlignLeft | Qt.AlignVCenter,
            self._t("settings_title"),
        )

        close_rect = QRectF(mx + modal_w - 110, my + 20, 84, 32)
        self._draw_button(painter, "settings_close", close_rect, self._t("close"))

        row_y = my + 82
        row_gap = 56
        self._draw_setting_row(
            painter,
            row_y,
            self._t("language"),
            self._t("lang_" + self.language),
            "settings_lang_prev",
            "settings_lang_next",
        )
        self._draw_setting_row(
            painter,
            row_y + row_gap,
            self._t("difficulty"),
            self._t("difficulty_" + self.difficulty),
            "settings_diff_prev",
            "settings_diff_next",
        )
        self._draw_setting_row(
            painter,
            row_y + row_gap * 2,
            self._t("mode"),
            self._t("mode_" + self.play_mode),
            "settings_mode_prev",
            "settings_mode_next",
        )
        self._draw_setting_row(
            painter,
            row_y + row_gap * 3,
            self._t("display_scale"),
            f"{self._t('scale_level')} {self.display_scale}%",
            "settings_scale_prev",
            "settings_scale_next",
        )
        self._draw_setting_row(
            painter,
            row_y + row_gap * 4,
            self._t("snake_color"),
            self._t("snake_color_" + self.snake_color_style),
            "settings_color_prev",
            "settings_color_next",
        )
        self._draw_setting_row(
            painter,
            row_y + row_gap * 5,
            self._t("snake_shape"),
            self._t("snake_shape_" + self.snake_shape_style),
            "settings_shape_prev",
            "settings_shape_next",
        )
        self._draw_setting_row(
            painter,
            row_y + row_gap * 6,
            self._t("food_style"),
            self._t("food_style_" + self.food_style),
            "settings_food_prev",
            "settings_food_next",
        )

        speed_top = row_y + row_gap * 7 + 10
        speed_label_rect = QRectF(mx + 28, speed_top, 180, 36)
        painter.setFont(QFont("Avenir Next", 12, QFont.Bold))
        painter.setPen(QColor("#9CC6D8"))
        painter.drawText(speed_label_rect, Qt.AlignLeft | Qt.AlignVCenter, self._t("speed"))

        minus_rect = QRectF(mx + modal_w - 200, speed_top + 2, 34, 32)
        value_rect = QRectF(mx + modal_w - 162, speed_top + 2, 124, 32)
        plus_rect = QRectF(mx + modal_w - 34, speed_top + 2, 34, 32)

        self._draw_button(painter, "settings_speed_minus", minus_rect, "-")
        self._draw_button(painter, "settings_speed_plus", plus_rect, "+")

        painter.setPen(QPen(QColor("#3C7191"), 1.5))
        painter.setBrush(QColor("#122E42"))
        painter.drawRoundedRect(value_rect, 8, 8)
        painter.setFont(QFont("Avenir Next", 10, QFont.DemiBold))
        painter.setPen(QColor("#E8FCFF"))
        painter.drawText(
            value_rect,
            Qt.AlignCenter,
            f"{self._t('speed_level')} {self.speed_level}",
        )

        painter.setFont(QFont("Avenir Next", 10))
        painter.setPen(QColor("#88B6CB"))
        painter.drawText(
            QRectF(mx + 28, my + modal_h - 36, modal_w - 56, 20),
            Qt.AlignCenter,
            self._t("settings_hint"),
        )

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        self.click_regions.clear()
        now = time.monotonic()
        self._draw_background(painter)
        self._draw_board(painter)
        self._draw_panel(painter)
        self._draw_food(painter, now)
        self._draw_snake(painter)
        self._draw_hud(painter)
        self._draw_effect(painter, now)
        self._draw_overlay(painter)
        if self.settings_open:
            self._draw_settings_overlay(painter)


def main() -> None:
    app = QApplication(sys.argv)
    game = SnakeGame()
    game.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
