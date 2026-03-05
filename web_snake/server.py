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
GRID_WIDTH = 24
GRID_HEIGHT = 20
TICK_INTERVAL_SEC = 0.14
ROOM_TIMEOUT_SEC = 6 * 60 * 60
ENDED_ROOM_TIMEOUT_SEC = 60 * 60
STATIC_DIR = Path(__file__).with_name("static")

DIRECTION_MAP: dict[str, tuple[int, int]] = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}


def _is_opposite(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] == -b[0] and a[1] == -b[1]


def _name_or_default(raw: Any, fallback: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return fallback
    return text[:14]


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
        return (width // 2, height // 2)
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
    last_tick: float = field(default_factory=time.monotonic)

    def add_player(self, name: str) -> tuple[str, int]:
        if len(self.players) >= 2:
            raise ValueError("Room is full")
        token = secrets.token_urlsafe(18)
        player_index = len(self.players)
        self.players.append(
            {
                "token": token,
                "name": name,
                "last_seen": time.time(),
            }
        )
        self.updated_at = time.time()
        if len(self.players) == 2:
            self._prepare_match_data()
        return token, player_index

    def _prepare_match_data(self) -> None:
        self.snakes = [self._default_snake(0), self._default_snake(1)]
        self.directions = [self._default_direction(0), self._default_direction(1)]
        self.next_directions = list(self.directions)
        self.scores = [0, 0]
        self.alive = [True, True]
        if self.mode == "arena":
            occupied = set(self.snakes[0]) | set(self.snakes[1])
            self.foods = _food_from_empty(GRID_WIDTH, GRID_HEIGHT, occupied)
        else:
            self.foods = [
                _food_from_empty(GRID_WIDTH, GRID_HEIGHT, set(self.snakes[0])),
                _food_from_empty(GRID_WIDTH, GRID_HEIGHT, set(self.snakes[1])),
            ]
        self.started = False
        self.ended = False
        self.winner = None
        self.message = "Ready to start"
        self.last_tick = time.monotonic()
        self.updated_at = time.time()

    def _default_snake(self, index: int) -> list[tuple[int, int]]:
        if self.mode == "arena":
            y = GRID_HEIGHT // 2
            if index == 0:
                return [(5, y), (4, y), (3, y), (2, y)]
            return [(18, y), (19, y), (20, y), (21, y)]
        y = GRID_HEIGHT // 2 + (-4 if index == 0 else 4)
        return [(5, y), (4, y), (3, y), (2, y)]

    def _default_direction(self, index: int) -> tuple[int, int]:
        if self.mode == "arena":
            return (1, 0) if index == 0 else (-1, 0)
        return (1, 0)

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
        if elapsed < TICK_INTERVAL_SEC:
            return
        steps = max(1, min(4, int(elapsed / TICK_INTERVAL_SEC)))
        for _ in range(steps):
            self.last_tick += TICK_INTERVAL_SEC
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
                or next_head[0] >= GRID_WIDTH
                or next_head[1] < 0
                or next_head[1] >= GRID_HEIGHT
            )
            if out_of_board or next_head in check_body:
                self.alive[idx] = False
                deaths.append(idx)
                continue

            self.snakes[idx].insert(0, next_head)
            if grow:
                self.scores[idx] += 1
                foods[idx] = _food_from_empty(GRID_WIDTH, GRID_HEIGHT, set(self.snakes[idx]))
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

        next_heads: list[tuple[int, int]] = []
        grows: list[bool] = [False, False]
        food = self.foods if isinstance(self.foods, tuple) else (0, 0)
        for idx in (0, 1):
            hx, hy = self.snakes[idx][0]
            dx, dy = self.directions[idx]
            head = (hx + dx, hy + dy)
            next_heads.append(head)
            grows[idx] = head == food

        dead = [False, False]
        for idx in (0, 1):
            nx, ny = next_heads[idx]
            if nx < 0 or nx >= GRID_WIDTH or ny < 0 or ny >= GRID_HEIGHT:
                dead[idx] = True
                continue

            self_check = self.snakes[idx] if grows[idx] else self.snakes[idx][:-1]
            if next_heads[idx] in self_check:
                dead[idx] = True
                continue

            other = 1 - idx
            other_check = self.snakes[other] if grows[other] else self.snakes[other][:-1]
            if next_heads[idx] in other_check:
                dead[idx] = True

        if next_heads[0] == next_heads[1]:
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
            self._finish_by_status()
            self.updated_at = time.time()
            return

        eater: int | None = None
        if grows[0] and not grows[1]:
            eater = 0
        elif grows[1] and not grows[0]:
            eater = 1
        if eater is not None:
            occupied = set(self.snakes[0]) | set(self.snakes[1])
            self.foods = _food_from_empty(GRID_WIDTH, GRID_HEIGHT, occupied)

        self.updated_at = time.time()

    def _finish_by_status(self) -> None:
        self.started = False
        self.ended = True

        if self.alive[0] and not self.alive[1]:
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
            }
            for idx, p in enumerate(self.players)
        ]
        payload: dict[str, Any] = {
            "roomCode": self.code,
            "mode": self.mode,
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

    def create_room(self, mode: str, name: str) -> dict[str, Any]:
        if mode not in {"separate", "arena"}:
            raise ValueError("Invalid mode")
        with self.lock:
            code = self._new_code()
            room = Room(code=code, mode=mode)
            token, index = room.add_player(name)
            room.message = "Waiting for player 2"
            self.rooms[code] = room
        return {
            "roomCode": code,
            "token": token,
            "playerIndex": index,
            "mode": mode,
            "host": True,
        }

    def join_room(self, code: str, name: str) -> dict[str, Any]:
        normalized = code.strip().upper()
        with self.lock:
            room = self.rooms.get(normalized)
            if room is None:
                raise ValueError("Room not found")
            token, index = room.add_player(name)
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
    server_version = "SnakeWeb/1.0"
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
                mode = str(payload.get("mode", "separate"))
                name = _name_or_default(payload.get("name"), "Player 1")
                data = HUB.create_room(mode, name)
                self._send_json(HTTPStatus.OK, {"ok": True, "data": data})
                return
            if parsed.path == "/api/join":
                room_code = str(payload.get("roomCode", ""))
                name = _name_or_default(payload.get("name"), "Player 2")
                data = HUB.join_room(room_code, name)
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
