from __future__ import annotations

import math
import random
import sys
import time
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

        self.setWindowTitle("Neon Snake")
        self.setFixedSize(self.window_width, self.window_height)
        self.setFocusPolicy(Qt.StrongFocus)

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
        self.best_file = Path(__file__).with_name(".snake_best_score")

        self._load_best_score()
        self.reset()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(16)

    def _load_best_score(self) -> None:
        if not self.best_file.exists():
            self.best_score = 0
            return
        try:
            self.best_score = int(self.best_file.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            self.best_score = 0

    def _save_best_score(self) -> None:
        try:
            self.best_file.write_text(str(self.best_score), encoding="utf-8")
        except OSError:
            pass

    def _mix_color(self, start: QColor, end: QColor, ratio: float) -> QColor:
        ratio = max(0.0, min(1.0, ratio))
        red = round(start.red() + (end.red() - start.red()) * ratio)
        green = round(start.green() + (end.green() - start.green()) * ratio)
        blue = round(start.blue() + (end.blue() - start.blue()) * ratio)
        return QColor(red, green, blue)

    def _spawn_food(self) -> tuple[int, int]:
        occupied = set(self.snake)
        while True:
            position = (
                self.random.randrange(self.grid_cols),
                self.random.randrange(self.grid_rows),
            )
            if position not in occupied:
                return position

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
        self.move_interval_ms = 130
        self.last_move_time = time.monotonic()
        self.effect_until = 0.0

    def start(self) -> None:
        if self.state in {"ready", "game_over"}:
            if self.state == "game_over":
                self.reset()
            self.state = "running"
            self.last_move_time = time.monotonic()

    def _set_game_over(self) -> None:
        self.state = "game_over"
        if self.score > self.best_score:
            self.best_score = self.score
            self._save_best_score()

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
            self.food = self._spawn_food()
            self.move_interval_ms = max(68, self.move_interval_ms - 2)
            self.effect_until = time.monotonic() + 0.12
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
            if self.state == "running":
                self.state = "paused"
            elif self.state == "paused":
                self.state = "running"
                self.last_move_time = time.monotonic()
            elif self.state in {"ready", "game_over"}:
                self.start()
            return

        if key == Qt.Key_R:
            self.reset()
            self.start()
            return

        if key == Qt.Key_Escape:
            self.close()

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

        inner = QRectF(self.board_x, self.board_y, self.board_width, self.board_height)
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
            QRectF(self.panel_x + 24, self.panel_y + 10, self.panel_width - 48, 48),
            Qt.AlignLeft | Qt.AlignVCenter,
            "NEON SNAKE",
        )

        speed_level = int(round((130 - self.move_interval_ms) / 4)) + 1
        stats = [
            ("Score", str(self.score)),
            ("Best", str(self.best_score)),
            ("Length", str(len(self.snake))),
            ("Speed", str(max(1, speed_level))),
        ]

        title_font = QFont("Avenir Next", 12, QFont.Bold)
        value_font = QFont("Avenir Next", 19, QFont.Bold)
        y = self.panel_y + 94

        for label, value in stats:
            painter.setFont(title_font)
            painter.setPen(QColor("#9CC6D8"))
            painter.drawText(
                QRectF(self.panel_x + 24, y, 110, 30),
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
            y += 58

        painter.setFont(QFont("Avenir Next", 16, QFont.Bold))
        painter.setPen(QColor("#E6FAFF"))
        painter.drawText(
            QRectF(self.panel_x + 24, self.window_height - 200, self.panel_width - 48, 28),
            Qt.AlignLeft | Qt.AlignVCenter,
            "Controls",
        )

        painter.setFont(QFont("Avenir Next", 12))
        painter.setPen(QColor("#9CC6D8"))
        lines = [
            "Arrow / WASD   Move",
            "Space          Pause",
            "R              Restart",
            "Esc            Quit",
        ]
        for index, line in enumerate(lines):
            painter.drawText(
                QRectF(
                    self.panel_x + 24,
                    self.window_height - 168 + index * 24,
                    self.panel_width - 48,
                    22,
                ),
                Qt.AlignLeft | Qt.AlignVCenter,
                line,
            )

    def _draw_effect(self, painter: QPainter, now: float) -> None:
        if now > self.effect_until:
            return
        ratio = (self.effect_until - now) / 0.12
        color = QColor(255, 255, 255, int(70 * ratio))
        painter.fillRect(
            QRectF(self.board_x, self.board_y, self.board_width, self.board_height),
            color,
        )

    def _draw_overlay(self, painter: QPainter) -> None:
        if self.state == "running":
            return

        if self.state == "ready":
            title = "Ready?"
            subtitle = "Press Enter / Space / Arrow to start"
            text_color = QColor("#E6FAFF")
        elif self.state == "paused":
            title = "Paused"
            subtitle = "Press Space to continue"
            text_color = QColor("#FFD37A")
        else:
            title = "Game Over"
            subtitle = "Press R or Enter to restart"
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
