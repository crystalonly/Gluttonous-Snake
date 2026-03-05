from __future__ import annotations

import json
import math
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen, QRadialGradient
from PyQt5.QtWidgets import QApplication, QWidget


class SnakeGame(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.window_width = 980
        self.window_height = 660
        self.cell_size = 24
        self.grid_cols = 28
        self.grid_rows = 24

        self.board_x = 26
        self.board_y = 42
        self.board_width = self.grid_cols * self.cell_size
        self.board_height = self.grid_rows * self.cell_size
        self.panel_x = self.board_x + self.board_width + 28
        self.panel_y = 42
        self.panel_width = self.window_width - self.panel_x - 26
        self.panel_height = self.window_height - self.panel_y - 28

        self.languages = ["en", "zh", "ja"]
        self.language = "en"
        self.texts = {
            "en": {
                "window_title": "Neon Snake",
                "game_title": "NEON SNAKE",
                "score": "Score",
                "best": "Best",
                "length": "Length",
                "speed": "Speed",
                "games": "Games",
                "last": "Last",
                "controls": "Controls",
                "start": "Start",
                "pause": "Pause",
                "resume": "Resume",
                "restart": "Restart",
                "language": "Language",
                "speed_level": "Level",
                "mouse_hint": "Mouse: click board or arrows to steer",
                "keys_hint": "Keys: WASD/Arrows, Space, R, L, +/-",
                "ready_title": "Ready?",
                "ready_subtitle": "Press Enter / Space / Arrow or Click Start",
                "paused_title": "Paused",
                "paused_subtitle": "Press Space or Click Resume",
                "over_title": "Game Over",
                "over_subtitle": "Press R / Enter or Click Restart",
                "lang_en": "English",
                "lang_zh": "Chinese",
                "lang_ja": "Japanese",
                "up": "UP",
                "down": "DOWN",
                "left": "LEFT",
                "right": "RIGHT",
            },
            "zh": {
                "window_title": "霓虹贪吃蛇",
                "game_title": "霓虹贪吃蛇",
                "score": "分数",
                "best": "最高",
                "length": "蛇长",
                "speed": "速度",
                "games": "局数",
                "last": "上局",
                "controls": "操作",
                "start": "开始",
                "pause": "暂停",
                "resume": "继续",
                "restart": "重开",
                "language": "语言",
                "speed_level": "档位",
                "mouse_hint": "鼠标: 点击棋盘或方向键控制",
                "keys_hint": "键盘: WASD/方向键, 空格, R, L, +/-",
                "ready_title": "准备开始?",
                "ready_subtitle": "按 Enter / 空格 / 方向键 或点击开始",
                "paused_title": "已暂停",
                "paused_subtitle": "按空格或点击继续",
                "over_title": "游戏结束",
                "over_subtitle": "按 R / Enter 或点击重开",
                "lang_en": "英文",
                "lang_zh": "中文",
                "lang_ja": "日文",
                "up": "上",
                "down": "下",
                "left": "左",
                "right": "右",
            },
            "ja": {
                "window_title": "ネオンスネーク",
                "game_title": "ネオンスネーク",
                "score": "スコア",
                "best": "ベスト",
                "length": "長さ",
                "speed": "速度",
                "games": "回数",
                "last": "前回",
                "controls": "操作",
                "start": "開始",
                "pause": "一時停止",
                "resume": "再開",
                "restart": "リスタート",
                "language": "言語",
                "speed_level": "レベル",
                "mouse_hint": "マウス: 盤面/矢印をクリックして操作",
                "keys_hint": "キー: WASD/矢印, Space, R, L, +/-",
                "ready_title": "準備OK?",
                "ready_subtitle": "Enter/Space/矢印 または 開始をクリック",
                "paused_title": "一時停止中",
                "paused_subtitle": "Space または 再開をクリック",
                "over_title": "ゲームオーバー",
                "over_subtitle": "R / Enter または リスタートをクリック",
                "lang_en": "英語",
                "lang_zh": "中国語",
                "lang_ja": "日本語",
                "up": "UP",
                "down": "DOWN",
                "left": "LEFT",
                "right": "RIGHT",
            },
        }

        self.random = random.Random()
        self.state = "ready"
        self.snake: list[tuple[int, int]] = []
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = (0, 0)
        self.score = 0
        self.best_score = 0
        self.move_interval_ms = 130
        self.last_move_time = time.monotonic()
        self.effect_until = 0.0
        self.food_eaten = 0
        self.speed_level = 5

        self.records_file = Path(__file__).with_name(".snake_records.json")
        self.legacy_best_file = Path(__file__).with_name(".snake_best_score")
        self.history: list[dict[str, object]] = []
        self.games_played = 0
        self.last_record: dict[str, object] = {
            "timestamp": "",
            "score": 0,
            "best": 0,
            "length": 4,
            "duration_sec": 0.0,
            "speed_level": self.speed_level,
            "reason": "none",
            "language": self.language,
        }
        self.session_recorded = False
        self.game_start_time = time.monotonic()

        self.click_regions: dict[str, QRectF] = {}

        self._load_records()
        self.setWindowTitle(self._t("window_title"))
        self.setFixedSize(self.window_width, self.window_height)
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

    def _normalize_record(self, raw: dict[str, object]) -> dict[str, object]:
        return {
            "timestamp": str(raw.get("timestamp", "")),
            "score": max(0, self._as_int(raw.get("score", 0))),
            "best": max(0, self._as_int(raw.get("best", self.best_score))),
            "length": max(1, self._as_int(raw.get("length", 4))),
            "duration_sec": max(0.0, self._as_float(raw.get("duration_sec", 0.0))),
            "speed_level": min(9, max(1, self._as_int(raw.get("speed_level", 5)))),
            "reason": str(raw.get("reason", "none")),
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

        legacy_best = 0
        if self.legacy_best_file.exists():
            try:
                legacy_best = int(self.legacy_best_file.read_text(encoding="utf-8").strip())
            except (OSError, ValueError):
                legacy_best = 0

        self.best_score = max(legacy_best, self._as_int(payload.get("best_score", 0)))

        settings = payload.get("settings", {})
        if isinstance(settings, dict):
            loaded_language = str(settings.get("language", self.language))
            if loaded_language in self.languages:
                self.language = loaded_language
            loaded_speed = self._as_int(settings.get("speed_level", self.speed_level))
            self.speed_level = min(9, max(1, loaded_speed))

        raw_history = payload.get("history", [])
        if isinstance(raw_history, list):
            for item in raw_history[-300:]:
                if isinstance(item, dict):
                    self.history.append(self._normalize_record(item))
            self.history = self.history[-200:]

        self.games_played = max(
            len(self.history),
            self._as_int(payload.get("games_played", len(self.history))),
        )

        raw_last = payload.get("last_record")
        if isinstance(raw_last, dict):
            self.last_record = self._normalize_record(raw_last)
        elif self.history:
            self.last_record = self.history[-1]

    def _save_records(self) -> None:
        payload = {
            "best_score": self.best_score,
            "games_played": self.games_played,
            "last_record": self.last_record,
            "settings": {
                "language": self.language,
                "speed_level": self.speed_level,
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

    def _base_interval_for_speed(self) -> int:
        return 178 - (self.speed_level - 1) * 12

    def _recalculate_interval(self) -> None:
        self.move_interval_ms = max(58, self._base_interval_for_speed() - self.food_eaten * 2)

    def _change_speed(self, delta: int) -> None:
        new_level = min(9, max(1, self.speed_level + delta))
        if new_level == self.speed_level:
            return
        self.speed_level = new_level
        self._recalculate_interval()
        self._save_records()

    def _cycle_language(self) -> None:
        current_index = self.languages.index(self.language)
        self.language = self.languages[(current_index + 1) % len(self.languages)]
        self.setWindowTitle(self._t("window_title"))
        self._save_records()

    def _spawn_food(self) -> tuple[int, int]:
        occupied = set(self.snake)
        while True:
            position = (
                self.random.randrange(self.grid_cols),
                self.random.randrange(self.grid_rows),
            )
            if position not in occupied:
                return position

    def _record_current_session(self, reason: str, force: bool = False) -> None:
        if self.session_recorded:
            return

        duration = max(0.0, time.monotonic() - self.game_start_time)
        current_length = len(self.snake)
        if not force and self.score <= 0 and current_length <= 4 and duration < 1.0:
            return

        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": self.score,
            "best": max(self.best_score, self.score),
            "length": current_length,
            "duration_sec": round(duration, 2),
            "speed_level": self.speed_level,
            "reason": reason,
            "language": self.language,
        }
        self.history.append(record)
        self.history = self.history[-200:]
        self.games_played += 1
        self.last_record = record
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
        self.state = "game_over"
        if self.score > self.best_score:
            self.best_score = self.score
        self._record_current_session("game_over", force=True)
        self._save_records()

    def _queue_direction(self, new_direction: tuple[int, int]) -> None:
        if self.state in {"ready", "game_over"}:
            self.start()
        elif self.state == "paused":
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
            self._set_game_over()
            return

        is_growing = next_head == self.food
        body_to_check = self.snake if is_growing else self.snake[:-1]
        if next_head in body_to_check:
            self._set_game_over()
            return

        self.snake.insert(0, next_head)
        if is_growing:
            self.score += 10
            self.food_eaten += 1
            self.food = self._spawn_food()
            self._recalculate_interval()
            self.effect_until = time.monotonic() + 0.12
            if self.score > self.best_score:
                self.best_score = self.score
            self._save_records()
        else:
            self.snake.pop()

    def _update_game(self) -> None:
        if self.state != "running":
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
        self.reset()
        self.start()

    def keyPressEvent(self, event) -> None:
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

        key = event.key()
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

        if key == Qt.Key_L:
            self._cycle_language()
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
        if action == "action_language":
            self._cycle_language()
            return
        if action == "speed_minus":
            self._change_speed(-1)
            return
        if action == "speed_plus":
            self._change_speed(1)
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
        if self._board_rect().contains(point):
            self._handle_board_click(point)
            return

        for action, rect in self.click_regions.items():
            if rect.contains(point):
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

        font_size = 11 if rect.height() <= 34 else 12
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

    def _draw_food(self, painter: QPainter, now: float) -> None:
        food_x, food_y = self.food
        px = self.board_x + food_x * self.cell_size
        py = self.board_y + food_y * self.cell_size
        center = QPointF(px + self.cell_size / 2, py + self.cell_size / 2)

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

    def _draw_snake(self, painter: QPainter) -> None:
        head_color = QColor("#7CF9FF")
        tail_color = QColor("#0E4F74")

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
            painter.setBrush(color)
            painter.drawRoundedRect(rect, 6, 6)

        head_x, head_y = self.snake[0]
        base_x = self.board_x + head_x * self.cell_size
        base_y = self.board_y + head_y * self.cell_size
        painter.setBrush(QColor("#052933"))

        if self.direction == (1, 0):
            eyes = [(16, 7), (16, 15)]
        elif self.direction == (-1, 0):
            eyes = [(8, 7), (8, 15)]
        elif self.direction == (0, -1):
            eyes = [(7, 8), (15, 8)]
        else:
            eyes = [(7, 16), (15, 16)]

        for offset_x, offset_y in eyes:
            painter.drawEllipse(QRectF(base_x + offset_x, base_y + offset_y, 4, 4))

    def _draw_hud(self, painter: QPainter) -> None:
        painter.setPen(QColor("#E6FAFF"))
        painter.setFont(QFont("Avenir Next", 24, QFont.Bold))
        painter.drawText(
            QRectF(self.panel_x + 24, self.panel_y + 10, self.panel_width - 48, 44),
            Qt.AlignLeft | Qt.AlignVCenter,
            self._t("game_title"),
        )

        last_score = self._as_int(self.last_record.get("score", 0))
        last_length = self._as_int(self.last_record.get("length", 0))
        stats = [
            (self._t("score"), str(self.score)),
            (self._t("best"), str(self.best_score)),
            (self._t("length"), str(len(self.snake))),
            (self._t("speed"), str(self.speed_level)),
            (self._t("games"), str(self.games_played)),
            (self._t("last"), f"{last_score}/{last_length}"),
        ]

        title_font = QFont("Avenir Next", 12, QFont.Bold)
        value_font = QFont("Avenir Next", 18, QFont.Bold)
        y = self.panel_y + 76

        for label, value in stats:
            painter.setFont(title_font)
            painter.setPen(QColor("#9CC6D8"))
            painter.drawText(
                QRectF(self.panel_x + 24, y, 120, 30),
                Qt.AlignLeft | Qt.AlignVCenter,
                label,
            )
            painter.setFont(value_font)
            painter.setPen(QColor("#E6FAFF"))
            painter.drawText(
                QRectF(self.panel_x + 120, y - 2, self.panel_width - 42, 32),
                Qt.AlignRight | Qt.AlignVCenter,
                value,
            )
            y += 42

        button_x = self.panel_x + 24
        button_w = self.panel_width - 48
        button_y = self.panel_y + 334

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

        language_name = self._t("lang_" + self.language)
        self._draw_button(
            painter,
            "action_language",
            QRectF(button_x, button_y + 84, button_w, 34),
            f"{self._t('language')}: {language_name}",
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
            QRectF(button_x, button_y + 165, button_w, 22),
            Qt.AlignCenter,
            self._t("controls"),
        )

        pad_size = 32
        pad_gap = 6
        pad_center_x = button_x + button_w / 2
        pad_top = button_y + 190
        up_rect = QRectF(pad_center_x - pad_size / 2, pad_top, pad_size, pad_size)
        left_rect = QRectF(
            pad_center_x - pad_size - pad_gap,
            pad_top + pad_size + pad_gap,
            pad_size,
            pad_size,
        )
        right_rect = QRectF(
            pad_center_x + pad_gap,
            pad_top + pad_size + pad_gap,
            pad_size,
            pad_size,
        )
        down_rect = QRectF(
            pad_center_x - pad_size / 2,
            pad_top + pad_size + pad_gap,
            pad_size,
            pad_size,
        )

        self._draw_button(painter, "dir_up", up_rect, self._t("up"))
        self._draw_button(painter, "dir_left", left_rect, self._t("left"))
        self._draw_button(painter, "dir_right", right_rect, self._t("right"))
        self._draw_button(painter, "dir_down", down_rect, self._t("down"))

        painter.setFont(QFont("Avenir Next", 9))
        painter.setPen(QColor("#88B6CB"))
        painter.drawText(
            QRectF(button_x, self.panel_y + self.panel_height - 44, button_w, 18),
            Qt.AlignCenter,
            self._t("mouse_hint"),
        )
        painter.drawText(
            QRectF(button_x, self.panel_y + self.panel_height - 24, button_w, 18),
            Qt.AlignCenter,
            self._t("keys_hint"),
        )

    def _draw_effect(self, painter: QPainter, now: float) -> None:
        if now > self.effect_until:
            return
        ratio = (self.effect_until - now) / 0.12
        color = QColor(255, 255, 255, int(70 * ratio))
        painter.fillRect(self._board_rect(), color)

    def _draw_overlay(self, painter: QPainter) -> None:
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
            self.board_y + 214,
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


def main() -> None:
    app = QApplication(sys.argv)
    game = SnakeGame()
    game.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
