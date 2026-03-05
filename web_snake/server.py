from __future__ import annotations

import json
import os
import random
import secrets
import threading
import time
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


HOST = "0.0.0.0"
DEFAULT_PORT = 8765
DEFAULT_GRID_COLS = 28
DEFAULT_GRID_ROWS = 24
MIN_GRID_COLS = 16
MAX_GRID_COLS = 72
MIN_GRID_ROWS = 12
MAX_GRID_ROWS = 48
DEFAULT_SPEED_LEVEL = 5
MIN_SPEED_LEVEL = 1
MAX_SPEED_LEVEL = 10
ROOM_TIMEOUT_SEC = 6 * 60 * 60
ENDED_ROOM_TIMEOUT_SEC = 60 * 60
STATIC_DIR = Path(__file__).with_name("static")

DEFAULT_SNAKE_COLOR = "neon"
DEFAULT_SNAKE_SHAPE = "rounded"
DEFAULT_FOOD_STYLE = "orb"
SNAKE_COLOR_STYLES = {"neon", "forest", "sunset", "glacier"}
SNAKE_SHAPE_STYLES = {"rounded", "square", "circle", "diamond"}
FOOD_STYLES = {"orb", "crystal", "star", "ring"}

DIRECTION_MAP: dict[str, tuple[int, int]] = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}


def _speed_to_interval(speed_level: int) -> float:
    clamped = max(MIN_SPEED_LEVEL, min(MAX_SPEED_LEVEL, int(speed_level)))
    return max(0.06, 0.24 - (clamped - 1) * 0.016)


def _is_opposite(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] == -b[0] and a[1] == -b[1]


def _as_int(raw: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, value))


def _name_or_default(raw: Any, fallback: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return fallback
    return text[:14]


def _normalize_mode(raw: Any, fallback: str = "separate") -> str:
    text = str(raw or "").strip().lower()
    if text in {"separate", "arena"}:
        return text
    return fallback


def _normalize_style(raw: Any) -> dict[str, str]:
    style = raw if isinstance(raw, dict) else {}
    snake_color = str(style.get("snakeColor", "")).strip().lower()
    snake_shape = str(style.get("snakeShape", "")).strip().lower()
    food_style = str(style.get("foodStyle", "")).strip().lower()
    if snake_color not in SNAKE_COLOR_STYLES:
        snake_color = DEFAULT_SNAKE_COLOR
    if snake_shape not in SNAKE_SHAPE_STYLES:
        snake_shape = DEFAULT_SNAKE_SHAPE
    if food_style not in FOOD_STYLES:
        food_style = DEFAULT_FOOD_STYLE
    return {
        "snakeColor": snake_color,
        "snakeShape": snake_shape,
        "foodStyle": food_style,
    }


def _food_from_empty(
    width: int,
    height: int,
    occupied: set[tuple[int, int]],
) -> tuple[int, int]:
    empty: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            cell = (x, y)
            if cell not in occupied:
                empty.append(cell)
    if not empty:
        return (max(0, width // 2), max(0, height // 2))
    return random.choice(empty)


def _snake_to_json(snake: list[tuple[int, int]]) -> list[list[int]]:
    return [[x, y] for x, y in snake]


def _read_port() -> int:
    candidates = [os.environ.get("PORT"), os.environ.get("SNAKE_PORT")]
    for raw in candidates:
        if raw is None:
            continue
        try:
            value = int(raw)
        except ValueError:
            continue
        if 1 <= value <= 65535:
            return value
    return DEFAULT_PORT


@dataclass
class Room:
    code: str
    mode: str
    grid_cols: int
    grid_rows: int
    speed_level: int
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    players: list[dict[str, Any]] = field(default_factory=list)
    started: bool = False
    ended: bool = False
    winner: int | None = None
    message: str = ""
    snakes: list[list[tuple[int, int]]] = field(default_factory=list)
    directions: list[tuple[int, int]] = field(default_factory=list)
    next_directions: list[tuple[int, int]] = field(default_factory=list)
    scores: list[int] = field(default_factory=list)
    alive: list[bool] = field(default_factory=list)
    foods: tuple[int, int] | list[tuple[int, int]] | None = None
    tick_interval: float = field(default=0.14)
    last_tick: float = field(default_factory=time.monotonic)

    def __post_init__(self) -> None:
        self.mode = _normalize_mode(self.mode)
        self.grid_cols = _as_int(self.grid_cols, DEFAULT_GRID_COLS, MIN_GRID_COLS, MAX_GRID_COLS)
        self.grid_rows = _as_int(self.grid_rows, DEFAULT_GRID_ROWS, MIN_GRID_ROWS, MAX_GRID_ROWS)
        self.speed_level = _as_int(self.speed_level, DEFAULT_SPEED_LEVEL, MIN_SPEED_LEVEL, MAX_SPEED_LEVEL)
        self.tick_interval = _speed_to_interval(self.speed_level)

    def add_player(self, name: str, style: dict[str, str]) -> tuple[str, int]:
        if len(self.players) >= 2:
            raise ValueError("Room is full")
        token = secrets.token_urlsafe(18)
        player_index = len(self.players)
        self.players.append(
            {
                "token": token,
                "name": name,
                "last_seen": time.time(),
                "style": _normalize_style(style),
            }
        )
        self.updated_at = time.time()
        if len(self.players) == 2:
            self._prepare_match_data()
        return token, player_index

    def _safe_row(self, index: int) -> int:
        if self.mode == "arena":
            return max(2, min(self.grid_rows - 3, self.grid_rows // 2))
        quarter = self.grid_rows // 4
        three_quarters = (self.grid_rows * 3) // 4
        y = quarter if index == 0 else three_quarters
        return max(2, min(self.grid_rows - 3, y))

    def _lane_margin(self) -> int:
        return max(4, min(10, self.grid_cols // 5))

    def _default_snake(self, index: int) -> list[tuple[int, int]]:
        y = self._safe_row(index)
        margin = self._lane_margin()
        if self.mode == "arena":
            if index == 0:
                head_x = margin
                return [(head_x - i, y) for i in range(4)]
            head_x = self.grid_cols - 1 - margin
            return [(head_x + i, y) for i in range(4)]
        head_x = margin
        return [(head_x - i, y) for i in range(4)]

    def _default_direction(self, index: int) -> tuple[int, int]:
        if self.mode == "arena":
            return (1, 0) if index == 0 else (-1, 0)
        return (1, 0)

    def _prepare_match_data(self) -> None:
        self.snakes = [self._default_snake(0), self._default_snake(1)]
        self.directions = [self._default_direction(0), self._default_direction(1)]
        self.next_directions = list(self.directions)
        self.scores = [0, 0]
        self.alive = [True, True]
        if self.mode == "arena":
            occupied = set(self.snakes[0]) | set(self.snakes[1])
            self.foods = _food_from_empty(self.grid_cols, self.grid_rows, occupied)
        else:
            self.foods = [
                _food_from_empty(self.grid_cols, self.grid_rows, set(self.snakes[0])),
                _food_from_empty(self.grid_cols, self.grid_rows, set(self.snakes[1])),
            ]
        self.started = False
        self.ended = False
        self.winner = None
        self.message = "Ready to start"
        self.last_tick = time.monotonic()
        self.updated_at = time.time()

    def player_index(self, token: str) -> int:
        for idx, player in enumerate(self.players):
            if player.get("token") == token:
                player["last_seen"] = time.time()
                self.updated_at = time.time()
                return idx
        return -1

    def set_direction(self, player_index: int, direction_key: str) -> None:
        if player_index < 0 or player_index >= len(self.players):
            return
        if direction_key not in DIRECTION_MAP:
            return
        current = self.directions[player_index]
        target = DIRECTION_MAP[direction_key]
        if _is_opposite(current, target) and len(self.snakes[player_index]) > 1:
            return
        self.next_directions[player_index] = target
        self.updated_at = time.time()

    def update_player_style(self, player_index: int, style: dict[str, str]) -> None:
        if player_index < 0 or player_index >= len(self.players):
            raise ValueError("Invalid player")
        self.players[player_index]["style"] = _normalize_style(style)
        self.updated_at = time.time()

    def update_room_config(
        self,
        player_index: int,
        *,
        mode: str | None = None,
        grid_cols: int | None = None,
        grid_rows: int | None = None,
        speed_level: int | None = None,
    ) -> None:
        if player_index != 0:
            raise ValueError("Only host can update room config")
        if self.started:
            raise ValueError("Cannot change config while match is running")

        next_mode = self.mode if mode is None else _normalize_mode(mode, self.mode)
        next_cols = self.grid_cols if grid_cols is None else _as_int(grid_cols, self.grid_cols, MIN_GRID_COLS, MAX_GRID_COLS)
        next_rows = self.grid_rows if grid_rows is None else _as_int(grid_rows, self.grid_rows, MIN_GRID_ROWS, MAX_GRID_ROWS)
        next_speed = self.speed_level if speed_level is None else _as_int(
            speed_level,
            self.speed_level,
            MIN_SPEED_LEVEL,
            MAX_SPEED_LEVEL,
        )

        changed = (
            next_mode != self.mode
            or next_cols != self.grid_cols
            or next_rows != self.grid_rows
            or next_speed != self.speed_level
        )
        self.mode = next_mode
        self.grid_cols = next_cols
        self.grid_rows = next_rows
        self.speed_level = next_speed
        self.tick_interval = _speed_to_interval(next_speed)
        if changed and len(self.players) == 2:
            self._prepare_match_data()
        self.updated_at = time.time()

    def start(self) -> None:
        if len(self.players) < 2:
            raise ValueError("Need two players to start")
        self._prepare_match_data()
        self.started = True
        self.message = "Match running"
        self.last_tick = time.monotonic()
        self.updated_at = time.time()

    def tick(self, now: float) -> None:
        if not self.started or self.ended or len(self.players) < 2:
            return
        elapsed = now - self.last_tick
        if elapsed < self.tick_interval:
            return
        steps = max(1, min(6, int(elapsed / self.tick_interval)))
        for _ in range(steps):
            self.last_tick += self.tick_interval
            if self.mode == "arena":
                self._step_arena()
            else:
                self._step_separate()
            if self.ended:
                break

    def _step_separate(self) -> None:
        deaths: list[int] = []
        foods = self.foods if isinstance(self.foods, list) else [(0, 0), (0, 0)]
        for idx in (0, 1):
            if not self.alive[idx]:
                continue
            desired = self.next_directions[idx]
            if not (_is_opposite(self.directions[idx], desired) and len(self.snakes[idx]) > 1):
                self.directions[idx] = desired

            head_x, head_y = self.snakes[idx][0]
            dir_x, dir_y = self.directions[idx]
            next_head = (head_x + dir_x, head_y + dir_y)
            grow = next_head == foods[idx]
            check_body = self.snakes[idx] if grow else self.snakes[idx][:-1]
            out_of_board = (
                next_head[0] < 0
                or next_head[0] >= self.grid_cols
                or next_head[1] < 0
                or next_head[1] >= self.grid_rows
            )
            if out_of_board or next_head in check_body:
                self.alive[idx] = False
                deaths.append(idx)
                continue

            self.snakes[idx].insert(0, next_head)
            if grow:
                self.scores[idx] += 1
                foods[idx] = _food_from_empty(self.grid_cols, self.grid_rows, set(self.snakes[idx]))
            else:
                self.snakes[idx].pop()

        self.foods = foods
        if deaths:
            self._finish_by_status()
        self.updated_at = time.time()

    def _step_arena(self) -> None:
        for idx in (0, 1):
            desired = self.next_directions[idx]
            if not (_is_opposite(self.directions[idx], desired) and len(self.snakes[idx]) > 1):
                self.directions[idx] = desired

        heads = [self.snakes[0][0], self.snakes[1][0]]
        next_heads: list[tuple[int, int]] = []
        grows = [False, False]
        food = self.foods if isinstance(self.foods, tuple) else (0, 0)
        for idx in (0, 1):
            hx, hy = heads[idx]
            dx, dy = self.directions[idx]
            head = (hx + dx, hy + dy)
            next_heads.append(head)
            grows[idx] = head == food

        dead = [False, False]
        capture_head = [False, False]
        for idx in (0, 1):
            nx, ny = next_heads[idx]
            if nx < 0 or nx >= self.grid_cols or ny < 0 or ny >= self.grid_rows:
                dead[idx] = True
                continue

            self_check = self.snakes[idx] if grows[idx] else self.snakes[idx][:-1]
            if next_heads[idx] in self_check:
                dead[idx] = True

        for idx in (0, 1):
            other = 1 - idx
            other_body = self.snakes[other][1:] if grows[other] else self.snakes[other][1:-1]
            if next_heads[idx] in other_body:
                dead[idx] = True

        same_next_cell = next_heads[0] == next_heads[1]
        swapped_heads = next_heads[0] == heads[1] and next_heads[1] == heads[0]
        if same_next_cell or swapped_heads:
            dead[0] = True
            dead[1] = True
        else:
            for idx in (0, 1):
                other = 1 - idx
                if next_heads[idx] == heads[other]:
                    capture_head[idx] = True
            if capture_head[0] and not capture_head[1]:
                dead[1] = True
            elif capture_head[1] and not capture_head[0]:
                dead[0] = True
            elif capture_head[0] and capture_head[1]:
                dead[0] = True
                dead[1] = True

        for idx in (0, 1):
            if dead[idx]:
                self.alive[idx] = False
                continue
            self.snakes[idx].insert(0, next_heads[idx])
            if grows[idx]:
                self.scores[idx] += 1
            else:
                self.snakes[idx].pop()

        if dead[0] or dead[1]:
            forced_winner: int | None = None
            if capture_head[0] and not dead[0]:
                forced_winner = 0
            elif capture_head[1] and not dead[1]:
                forced_winner = 1
            self._finish_by_status(forced_winner=forced_winner)
            self.updated_at = time.time()
            return

        if grows[0] or grows[1]:
            occupied = set(self.snakes[0]) | set(self.snakes[1])
            self.foods = _food_from_empty(self.grid_cols, self.grid_rows, occupied)

        self.updated_at = time.time()

    def _finish_by_status(self, forced_winner: int | None = None) -> None:
        self.started = False
        self.ended = True

        if forced_winner in (0, 1):
            self.winner = forced_winner
        elif self.alive[0] and not self.alive[1]:
            self.winner = 0
        elif self.alive[1] and not self.alive[0]:
            self.winner = 1
        else:
            if self.scores[0] > self.scores[1]:
                self.winner = 0
            elif self.scores[1] > self.scores[0]:
                self.winner = 1
            else:
                self.winner = -1

        if self.winner == -1:
            self.message = "Draw game"
        else:
            winner_name = self.players[self.winner].get("name", f"Player {self.winner + 1}")
            self.message = f"{winner_name} wins"

    def to_payload(self, token: str) -> dict[str, Any]:
        viewer_index = self.player_index(token)
        players = [
            {
                "name": p.get("name", f"Player {idx + 1}"),
                "online": (time.time() - float(p.get("last_seen", 0))) < 30,
                "style": _normalize_style(p.get("style")),
            }
            for idx, p in enumerate(self.players)
        ]
        payload: dict[str, Any] = {
            "roomCode": self.code,
            "mode": self.mode,
            "gridCols": self.grid_cols,
            "gridRows": self.grid_rows,
            "speedLevel": self.speed_level,
            "tickMs": int(self.tick_interval * 1000),
            "started": self.started,
            "ended": self.ended,
            "winner": self.winner,
            "message": self.message,
            "players": players,
            "scores": list(self.scores),
            "alive": list(self.alive),
            "viewerIndex": viewer_index,
            "updatedAt": self.updated_at,
        }
        if self.mode == "arena":
            payload["food"] = list(self.foods) if isinstance(self.foods, tuple) else [0, 0]
            payload["snakes"] = [_snake_to_json(s) for s in self.snakes]
        else:
            foods = self.foods if isinstance(self.foods, list) else [(0, 0), (0, 0)]
            payload["foods"] = [list(foods[0]), list(foods[1])]
            payload["snakes"] = [_snake_to_json(s) for s in self.snakes]
        return payload


class RoomHub:
    def __init__(self) -> None:
        self.rooms: dict[str, Room] = {}
        self.lock = threading.Lock()

    def _new_code(self) -> str:
        charset = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        for _ in range(500):
            code = "".join(random.choice(charset) for _ in range(6))
            if code not in self.rooms:
                return code
        raise RuntimeError("Failed to allocate room code")

    def create_room(
        self,
        *,
        mode: str,
        name: str,
        grid_cols: int,
        grid_rows: int,
        speed_level: int,
        style: dict[str, str],
    ) -> dict[str, Any]:
        with self.lock:
            code = self._new_code()
            room = Room(
                code=code,
                mode=mode,
                grid_cols=grid_cols,
                grid_rows=grid_rows,
                speed_level=speed_level,
            )
            token, index = room.add_player(name, style)
            room.message = "Waiting for player 2"
            self.rooms[code] = room
            state = room.to_payload(token)
        return {
            "roomCode": code,
            "token": token,
            "playerIndex": index,
            "mode": room.mode,
            "host": True,
            "state": state,
        }

    def join_room(self, code: str, name: str, style: dict[str, str]) -> dict[str, Any]:
        normalized = code.strip().upper()
        with self.lock:
            room = self.rooms.get(normalized)
            if room is None:
                raise ValueError("Room not found")
            token, index = room.add_player(name, style)
            room.message = "Ready to start"
            payload = room.to_payload(token)
        return {
            "roomCode": normalized,
            "token": token,
            "playerIndex": index,
            "mode": room.mode,
            "host": False,
            "state": payload,
        }

    def start_room(self, code: str, token: str) -> dict[str, Any]:
        normalized = code.strip().upper()
        with self.lock:
            room = self.rooms.get(normalized)
            if room is None:
                raise ValueError("Room not found")
            viewer = room.player_index(token)
            if viewer != 0:
                raise ValueError("Only host can start")
            room.start()
            payload = room.to_payload(token)
        return payload

    def update_room_config(
        self,
        code: str,
        token: str,
        *,
        mode: str | None,
        grid_cols: int | None,
        grid_rows: int | None,
        speed_level: int | None,
    ) -> dict[str, Any]:
        normalized = code.strip().upper()
        with self.lock:
            room = self.rooms.get(normalized)
            if room is None:
                raise ValueError("Room not found")
            viewer = room.player_index(token)
            if viewer < 0:
                raise ValueError("Invalid token")
            room.update_room_config(
                viewer,
                mode=mode,
                grid_cols=grid_cols,
                grid_rows=grid_rows,
                speed_level=speed_level,
            )
            payload = room.to_payload(token)
        return payload

    def update_style(self, code: str, token: str, style: dict[str, str]) -> dict[str, Any]:
        normalized = code.strip().upper()
        with self.lock:
            room = self.rooms.get(normalized)
            if room is None:
                raise ValueError("Room not found")
            viewer = room.player_index(token)
            if viewer < 0:
                raise ValueError("Invalid token")
            room.update_player_style(viewer, style)
            payload = room.to_payload(token)
        return payload

    def input_direction(self, code: str, token: str, direction_key: str) -> dict[str, Any]:
        normalized = code.strip().upper()
        with self.lock:
            room = self.rooms.get(normalized)
            if room is None:
                raise ValueError("Room not found")
            viewer = room.player_index(token)
            if viewer < 0:
                raise ValueError("Invalid token")
            room.set_direction(viewer, direction_key)
            payload = room.to_payload(token)
        return payload

    def get_state(self, code: str, token: str) -> dict[str, Any]:
        normalized = code.strip().upper()
        with self.lock:
            room = self.rooms.get(normalized)
            if room is None:
                raise ValueError("Room not found")
            return room.to_payload(token)

    def tick_all(self) -> None:
        now_mono = time.monotonic()
        now_real = time.time()
        with self.lock:
            stale_codes: list[str] = []
            for code, room in self.rooms.items():
                room.tick(now_mono)
                age = now_real - room.updated_at
                limit = ENDED_ROOM_TIMEOUT_SEC if room.ended else ROOM_TIMEOUT_SEC
                if age > limit:
                    stale_codes.append(code)
            for code in stale_codes:
                self.rooms.pop(code, None)


HUB = RoomHub()


class SnakeRequestHandler(BaseHTTPRequestHandler):
    server_version = "SnakeWeb/2.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, status: int, message: str) -> None:
        self._send_json(status, {"ok": False, "error": message})

    def _read_json_body(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = max(0, int(raw_length))
        except ValueError:
            length = 0
        body = self.rfile.read(length) if length > 0 else b""
        if not body:
            return {}
        try:
            parsed = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f"Invalid JSON: {exc}") from exc
        if not isinstance(parsed, dict):
            raise ValueError("JSON body must be object")
        return parsed

    def _serve_static(self, request_path: str) -> None:
        path = request_path
        if path == "/":
            path = "/index.html"
        safe_path = path.lstrip("/")
        if ".." in safe_path:
            self._send_error_json(HTTPStatus.BAD_REQUEST, "Invalid path")
            return
        file_path = (STATIC_DIR / safe_path).resolve()
        try:
            file_path.relative_to(STATIC_DIR.resolve())
        except ValueError:
            self._send_error_json(HTTPStatus.BAD_REQUEST, "Invalid path")
            return

        if not file_path.exists() or not file_path.is_file():
            self._send_error_json(HTTPStatus.NOT_FOUND, "Not found")
            return

        mime_map = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml",
        }
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime_map.get(file_path.suffix.lower(), "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            self._send_json(HTTPStatus.OK, {"ok": True, "status": "healthy"})
            return
        if parsed.path == "/api/state":
            query = parse_qs(parsed.query)
            room_code = query.get("roomCode", [""])[0]
            token = query.get("token", [""])[0]
            if not room_code:
                self._send_error_json(HTTPStatus.BAD_REQUEST, "roomCode is required")
                return
            try:
                state = HUB.get_state(room_code, token)
            except ValueError as exc:
                self._send_error_json(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json(HTTPStatus.OK, {"ok": True, "state": state})
            return
        self._serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self._read_json_body()
        except ValueError as exc:
            self._send_error_json(HTTPStatus.BAD_REQUEST, str(exc))
            return

        try:
            if parsed.path == "/api/create":
                mode = _normalize_mode(payload.get("mode", "separate"))
                name = _name_or_default(payload.get("name"), "Player 1")
                grid_cols = _as_int(payload.get("gridCols"), DEFAULT_GRID_COLS, MIN_GRID_COLS, MAX_GRID_COLS)
                grid_rows = _as_int(payload.get("gridRows"), DEFAULT_GRID_ROWS, MIN_GRID_ROWS, MAX_GRID_ROWS)
                speed_level = _as_int(payload.get("speedLevel"), DEFAULT_SPEED_LEVEL, MIN_SPEED_LEVEL, MAX_SPEED_LEVEL)
                style = _normalize_style(payload.get("style"))
                data = HUB.create_room(
                    mode=mode,
                    name=name,
                    grid_cols=grid_cols,
                    grid_rows=grid_rows,
                    speed_level=speed_level,
                    style=style,
                )
                self._send_json(HTTPStatus.OK, {"ok": True, "data": data})
                return
            if parsed.path == "/api/join":
                room_code = str(payload.get("roomCode", ""))
                name = _name_or_default(payload.get("name"), "Player 2")
                style = _normalize_style(payload.get("style"))
                data = HUB.join_room(room_code, name, style)
                self._send_json(HTTPStatus.OK, {"ok": True, "data": data})
                return
            if parsed.path == "/api/start":
                room_code = str(payload.get("roomCode", ""))
                token = str(payload.get("token", ""))
                data = HUB.start_room(room_code, token)
                self._send_json(HTTPStatus.OK, {"ok": True, "state": data})
                return
            if parsed.path == "/api/input":
                room_code = str(payload.get("roomCode", ""))
                token = str(payload.get("token", ""))
                direction = str(payload.get("direction", ""))
                data = HUB.input_direction(room_code, token, direction)
                self._send_json(HTTPStatus.OK, {"ok": True, "state": data})
                return
            if parsed.path == "/api/style":
                room_code = str(payload.get("roomCode", ""))
                token = str(payload.get("token", ""))
                style = _normalize_style(payload.get("style"))
                data = HUB.update_style(room_code, token, style)
                self._send_json(HTTPStatus.OK, {"ok": True, "state": data})
                return
            if parsed.path == "/api/room-config":
                room_code = str(payload.get("roomCode", ""))
                token = str(payload.get("token", ""))
                mode_raw = payload.get("mode")
                mode = None if mode_raw is None else _normalize_mode(mode_raw)
                grid_cols = None if "gridCols" not in payload else _as_int(
                    payload.get("gridCols"),
                    DEFAULT_GRID_COLS,
                    MIN_GRID_COLS,
                    MAX_GRID_COLS,
                )
                grid_rows = None if "gridRows" not in payload else _as_int(
                    payload.get("gridRows"),
                    DEFAULT_GRID_ROWS,
                    MIN_GRID_ROWS,
                    MAX_GRID_ROWS,
                )
                speed_level = None if "speedLevel" not in payload else _as_int(
                    payload.get("speedLevel"),
                    DEFAULT_SPEED_LEVEL,
                    MIN_SPEED_LEVEL,
                    MAX_SPEED_LEVEL,
                )
                data = HUB.update_room_config(
                    room_code,
                    token,
                    mode=mode,
                    grid_cols=grid_cols,
                    grid_rows=grid_rows,
                    speed_level=speed_level,
                )
                self._send_json(HTTPStatus.OK, {"ok": True, "state": data})
                return
        except ValueError as exc:
            self._send_error_json(HTTPStatus.BAD_REQUEST, str(exc))
            return

        self._send_error_json(HTTPStatus.NOT_FOUND, "Unknown API path")


def _room_tick_loop(stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        HUB.tick_all()
        stop_event.wait(0.03)


def run_server() -> None:
    if not STATIC_DIR.exists():
        raise FileNotFoundError(f"Missing static directory: {STATIC_DIR}")

    port = _read_port()
    stop_event = threading.Event()
    ticker = threading.Thread(target=_room_tick_loop, args=(stop_event,), daemon=True)
    ticker.start()

    server = ThreadingHTTPServer((HOST, port), SnakeRequestHandler)
    print(f"Snake web server running on http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    run_server()
