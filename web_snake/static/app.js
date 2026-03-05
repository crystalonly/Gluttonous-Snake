const $ = (id) => document.getElementById(id);

const GRID_W = 24;
const GRID_H = 20;

const singleCanvas = $("singleCanvas");
const singleCtx = singleCanvas.getContext("2d");
const singleStage = $("singleStage");
const singleOverlay = $("singleOverlay");
const singleOverlayTitle = $("singleOverlayTitle");
const singleOverlaySub = $("singleOverlaySub");
const reviveOverlay = $("reviveOverlay");

const singleScoreEl = $("singleScore");
const singleBestEl = $("singleBest");
const singleLengthEl = $("singleLength");
const singleBestLengthEl = $("singleBestLength");
const singleDifficultyEl = $("singleDifficulty");
const singleSpeedEl = $("singleSpeed");
const singleSpeedLabelEl = $("singleSpeedLabel");
const singleScaleEl = $("singleScale");
const singleScaleLabelEl = $("singleScaleLabel");
const singleModeEl = $("singleMode");

const singleStartBtn = $("singleStartBtn");
const singlePauseBtn = $("singlePauseBtn");
const singleRestartBtn = $("singleRestartBtn");
const reviveYesBtn = $("reviveYesBtn");
const reviveNoBtn = $("reviveNoBtn");

const playerNameInput = $("playerNameInput");
const onlineModeEl = $("onlineMode");
const createRoomBtn = $("createRoomBtn");
const roomCodeInput = $("roomCodeInput");
const onlineScaleEl = $("onlineScale");
const onlineScaleLabelEl = $("onlineScaleLabel");
const joinRoomBtn = $("joinRoomBtn");
const currentRoomCodeEl = $("currentRoomCode");
const copyInviteBtn = $("copyInviteBtn");
const startMatchBtn = $("startMatchBtn");
const onlineStatusEl = $("onlineStatus");
const onlineScoreRowEl = $("onlineScoreRow");

const onlineArenaCanvas = $("onlineArenaCanvas");
const onlineArenaCtx = onlineArenaCanvas.getContext("2d");
const onlineSplitWrap = $("onlineSplitWrap");
const onlineLeftCanvas = $("onlineLeftCanvas");
const onlineRightCanvas = $("onlineRightCanvas");
const onlineLeftCtx = onlineLeftCanvas.getContext("2d");
const onlineRightCtx = onlineRightCanvas.getContext("2d");
const leftPlayerLabel = $("leftPlayerLabel");
const rightPlayerLabel = $("rightPlayerLabel");

const onlineResultBanner = $("onlineResultBanner");
const resultEmoji = $("resultEmoji");
const resultText = $("resultText");

const STORAGE_SINGLE = "snake_web_single_records_v1";
const STORAGE_ONLINE = "snake_web_online_session_v1";
const STORAGE_VIEW = "snake_web_view_scale_v1";

const tabState = {
  active: "single",
};

const singleState = {
  snake: [],
  direction: [1, 0],
  nextDirection: [1, 0],
  food: [0, 0],
  score: 0,
  bestScore: 0,
  bestLength: 4,
  speedLevel: 5,
  viewScale: 100,
  difficulty: "mixed",
  mode: "normal",
  runningState: "ready", // ready | running | paused | over | revive
  lastMoveAt: 0,
};

const onlineState = {
  roomCode: "",
  token: "",
  playerIndex: -1,
  host: false,
  mode: "separate",
  state: null,
  pollingTimer: null,
  requestPending: false,
};

function toCellKey(x, y) {
  return `${x},${y}`;
}

function isOpposite(a, b) {
  return a[0] === -b[0] && a[1] === -b[1];
}

function clampName(raw, fallback) {
  const text = (raw || "").trim();
  if (!text) return fallback;
  return text.slice(0, 14);
}

function singleMoveMs() {
  return 194 - (singleState.speedLevel - 1) * 14;
}

function saveSingleRecords() {
  const data = {
    bestScore: singleState.bestScore,
    bestLength: singleState.bestLength,
    speedLevel: singleState.speedLevel,
    viewScale: singleState.viewScale,
    difficulty: singleState.difficulty,
    mode: singleState.mode,
  };
  localStorage.setItem(STORAGE_SINGLE, JSON.stringify(data));
}

function loadSingleRecords() {
  const raw = localStorage.getItem(STORAGE_SINGLE);
  if (!raw) return;
  try {
    const data = JSON.parse(raw);
    if (typeof data.bestScore === "number") singleState.bestScore = Math.max(0, Math.floor(data.bestScore));
    if (typeof data.bestLength === "number") singleState.bestLength = Math.max(4, Math.floor(data.bestLength));
    if (typeof data.speedLevel === "number") singleState.speedLevel = Math.max(1, Math.min(9, Math.floor(data.speedLevel)));
    if (typeof data.viewScale === "number") singleState.viewScale = Math.max(80, Math.min(150, Math.round(data.viewScale)));
    if (typeof data.difficulty === "string") singleState.difficulty = data.difficulty;
    if (typeof data.mode === "string") singleState.mode = data.mode;
  } catch (_err) {
    // ignore broken storage
  }
}

function saveViewScale() {
  localStorage.setItem(STORAGE_VIEW, JSON.stringify({ value: singleState.viewScale }));
}

function loadViewScale() {
  const raw = localStorage.getItem(STORAGE_VIEW);
  if (!raw) return;
  try {
    const parsed = JSON.parse(raw);
    if (typeof parsed.value === "number") {
      singleState.viewScale = Math.max(80, Math.min(150, Math.round(parsed.value / 5) * 5));
    }
  } catch (_err) {
    // ignore broken storage
  }
}

function resetSingleSnake() {
  const centerX = Math.floor(GRID_W / 2);
  const centerY = Math.floor(GRID_H / 2);
  singleState.snake = [
    [centerX, centerY],
    [centerX - 1, centerY],
    [centerX - 2, centerY],
    [centerX - 3, centerY],
  ];
  singleState.direction = [1, 0];
  singleState.nextDirection = [1, 0];
  singleState.score = 0;
  singleState.food = spawnSingleFood();
  singleState.lastMoveAt = performance.now();
}

function freeNeighborCount(cell, occupied) {
  const [x, y] = cell;
  const around = [
    [x + 1, y],
    [x - 1, y],
    [x, y + 1],
    [x, y - 1],
  ];
  let count = 0;
  for (const [nx, ny] of around) {
    if (nx < 0 || nx >= GRID_W || ny < 0 || ny >= GRID_H) continue;
    if (!occupied.has(toCellKey(nx, ny))) count += 1;
  }
  return count;
}

function spawnSingleFood() {
  const occupied = new Set(singleState.snake.map(([x, y]) => toCellKey(x, y)));
  const empty = [];
  for (let y = 0; y < GRID_H; y += 1) {
    for (let x = 0; x < GRID_W; x += 1) {
      if (!occupied.has(toCellKey(x, y))) {
        empty.push([x, y]);
      }
    }
  }
  if (empty.length === 0) return [Math.floor(GRID_W / 2), Math.floor(GRID_H / 2)];
  if (singleState.difficulty === "mixed") {
    return empty[Math.floor(Math.random() * empty.length)];
  }

  const [hx, hy] = singleState.snake[0] || [Math.floor(GRID_W / 2), Math.floor(GRID_H / 2)];
  const scored = empty.map(([x, y]) => {
    const wallDist = Math.min(x, GRID_W - 1 - x, y, GRID_H - 1 - y);
    const headDist = Math.abs(hx - x) + Math.abs(hy - y);
    const freeCount = freeNeighborCount([x, y], occupied);
    let score;
    if (singleState.difficulty === "easy") {
      score = wallDist * 2.4 + freeCount * 2.2 + headDist * 0.22;
    } else {
      score = (4 - wallDist) * 2.0 + (4 - freeCount) * 1.4 + headDist * 0.06;
    }
    return { cell: [x, y], score };
  });

  scored.sort((a, b) => b.score - a.score);
  const pool = scored.slice(0, Math.max(1, Math.floor(scored.length * 0.2)));
  return pool[Math.floor(Math.random() * pool.length)].cell;
}

function updateSingleOverlay() {
  if (singleState.runningState === "running" || singleState.runningState === "revive") {
    singleOverlay.classList.add("hidden");
    return;
  }
  singleOverlay.classList.remove("hidden");
  if (singleState.runningState === "ready") {
    singleOverlayTitle.textContent = "准备开始";
    singleOverlaySub.textContent = "按方向键 / WASD / 点击方向键开始";
  } else if (singleState.runningState === "paused") {
    singleOverlayTitle.textContent = "已暂停";
    singleOverlaySub.textContent = "按空格或点击开始/继续";
  } else if (singleState.runningState === "over") {
    singleOverlayTitle.textContent = "游戏结束";
    singleOverlaySub.textContent = "按 R 或点击重开";
  } else {
    singleOverlayTitle.textContent = "等待操作";
    singleOverlaySub.textContent = "";
  }
}

function updateSingleStats() {
  singleScoreEl.textContent = String(singleState.score);
  singleBestEl.textContent = String(singleState.bestScore);
  singleLengthEl.textContent = String(singleState.snake.length);
  singleBestLengthEl.textContent = String(singleState.bestLength);
  singleSpeedEl.value = String(singleState.speedLevel);
  singleSpeedLabelEl.textContent = String(singleState.speedLevel);
  singleScaleEl.value = String(singleState.viewScale);
  onlineScaleEl.value = String(singleState.viewScale);
  singleScaleLabelEl.textContent = `${singleState.viewScale}%`;
  onlineScaleLabelEl.textContent = `${singleState.viewScale}%`;
  singleDifficultyEl.value = singleState.difficulty;
  singleModeEl.value = singleState.mode;
  updateSingleOverlay();
}

function startOrResumeSingle() {
  if (singleState.runningState === "revive") return;
  if (singleState.runningState === "ready" || singleState.runningState === "over") {
    resetSingleSnake();
  }
  singleState.runningState = "running";
  singleState.lastMoveAt = performance.now();
  updateSingleStats();
}

function pauseSingle() {
  if (singleState.runningState !== "running") return;
  singleState.runningState = "paused";
  updateSingleStats();
}

function restartSingle() {
  resetSingleSnake();
  singleState.runningState = "ready";
  reviveOverlay.classList.add("hidden");
  updateSingleStats();
}

function setViewScale(nextValue) {
  const normalized = Math.max(80, Math.min(150, Math.round(nextValue / 5) * 5));
  if (normalized === singleState.viewScale) return;
  singleState.viewScale = normalized;
  updateSingleStats();
  resizeAllCanvases();
  saveSingleRecords();
  saveViewScale();
}

function gameOverSingle() {
  singleState.runningState = "over";
  singleState.bestScore = Math.max(singleState.bestScore, singleState.score);
  singleState.bestLength = Math.max(singleState.bestLength, singleState.snake.length);
  saveSingleRecords();
  updateSingleStats();
}

function safeReviveSingle() {
  const originLen = Math.max(4, singleState.snake.length);
  const length = Math.min(originLen, GRID_W - 4);
  const rowCandidates = [Math.floor(GRID_H / 2), Math.floor(GRID_H / 2) - 3, Math.floor(GRID_H / 2) + 3];
  const candidates = [];

  for (const y of rowCandidates) {
    if (y <= 1 || y >= GRID_H - 2) continue;
    const startX = Math.floor((GRID_W - length) / 2);
    const line = [];
    for (let i = 0; i < length; i += 1) {
      line.push([startX + i, y]);
    }
    const variants = [
      { snake: [...line].reverse(), dir: [1, 0] },
      { snake: line, dir: [-1, 0] },
    ];
    for (const v of variants) {
      const [hx, hy] = v.snake[0];
      const occupied = new Set(v.snake.map(([sx, sy]) => toCellKey(sx, sy)));
      const wallDist = Math.min(hx, GRID_W - 1 - hx, hy, GRID_H - 1 - hy);
      const free = freeNeighborCount([hx, hy], occupied);
      candidates.push({
        ...v,
        score: wallDist * 3 + free * 2,
      });
    }
  }
  candidates.sort((a, b) => b.score - a.score);
  const picked = candidates[0];
  if (!picked) {
    resetSingleSnake();
    return;
  }
  singleState.snake = picked.snake;
  singleState.direction = picked.dir;
  singleState.nextDirection = picked.dir;
  singleState.food = spawnSingleFood();
}

function handleSingleCollision() {
  if (singleState.mode === "invincible") {
    singleState.runningState = "revive";
    reviveOverlay.classList.remove("hidden");
    updateSingleOverlay();
    return;
  }
  gameOverSingle();
}

function stepSingle() {
  singleState.direction = singleState.nextDirection;
  const [hx, hy] = singleState.snake[0];
  const [dx, dy] = singleState.direction;
  const next = [hx + dx, hy + dy];
  const hitWall = next[0] < 0 || next[0] >= GRID_W || next[1] < 0 || next[1] >= GRID_H;
  const isGrow = next[0] === singleState.food[0] && next[1] === singleState.food[1];
  const body = isGrow ? singleState.snake : singleState.snake.slice(0, -1);
  const hitBody = body.some(([x, y]) => x === next[0] && y === next[1]);
  if (hitWall || hitBody) {
    handleSingleCollision();
    return;
  }
  singleState.snake.unshift(next);
  if (isGrow) {
    singleState.score += 1;
    singleState.bestScore = Math.max(singleState.bestScore, singleState.score);
    singleState.bestLength = Math.max(singleState.bestLength, singleState.snake.length);
    singleState.food = spawnSingleFood();
    saveSingleRecords();
  } else {
    singleState.snake.pop();
  }
  updateSingleStats();
}

function queueSingleDirection(dir) {
  if (singleState.runningState === "revive") return;
  if (singleState.runningState === "ready" || singleState.runningState === "over") {
    startOrResumeSingle();
  }
  if (singleState.runningState === "paused") {
    singleState.runningState = "running";
    singleState.lastMoveAt = performance.now();
  }
  if (isOpposite(singleState.direction, dir) && singleState.snake.length > 1) return;
  singleState.nextDirection = dir;
}

function fitAspect(maxW, maxH, aspect) {
  const safeW = Math.max(10, Math.floor(maxW));
  const safeH = Math.max(10, Math.floor(maxH));
  let width = safeW;
  let height = Math.floor(width / aspect);
  if (height > safeH) {
    height = safeH;
    width = Math.floor(height * aspect);
  }
  return {
    width: Math.max(40, width),
    height: Math.max(34, height),
  };
}

function setCanvasDisplaySize(canvas, cssWidth, cssHeight) {
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  const safeW = Math.max(40, Math.floor(cssWidth));
  const safeH = Math.max(34, Math.floor(cssHeight));
  canvas.style.width = `${safeW}px`;
  canvas.style.height = `${safeH}px`;
  canvas.width = Math.floor(safeW * dpr);
  canvas.height = Math.floor(safeH * dpr);
}

function resizeSingleCanvas() {
  const scaleRatio = singleState.viewScale / 100;
  const targetH = window.innerHeight * 0.75 * scaleRatio;
  const targetW = targetH * (GRID_W / GRID_H);
  const maxW = Math.max(320, singleStage.clientWidth - 16);
  const maxH = Math.max(260, singleStage.clientHeight - 16);
  const fitTarget = fitAspect(targetW, targetH, GRID_W / GRID_H);
  const fitFinal = fitAspect(Math.min(maxW, fitTarget.width), Math.min(maxH, fitTarget.height), GRID_W / GRID_H);
  setCanvasDisplaySize(singleCanvas, fitFinal.width, fitFinal.height);
}

function resizeOnlineCanvases() {
  const scaleRatio = singleState.viewScale / 100;
  const boardCard = document.querySelector(".online-board-card");
  if (!boardCard) return;

  if (onlineState.mode === "arena") {
    const targetH = window.innerHeight * 0.74 * scaleRatio;
    const targetW = targetH * (GRID_W / GRID_H);
    const maxW = Math.max(320, boardCard.clientWidth - 20);
    const maxH = Math.max(260, boardCard.clientHeight - 20);
    const fitTarget = fitAspect(targetW, targetH, GRID_W / GRID_H);
    const fitFinal = fitAspect(Math.min(maxW, fitTarget.width), Math.min(maxH, fitTarget.height), GRID_W / GRID_H);
    setCanvasDisplaySize(onlineArenaCanvas, fitFinal.width, fitFinal.height);
    return;
  }

  const leftWrap = onlineLeftCanvas.parentElement;
  const rightWrap = onlineRightCanvas.parentElement;
  if (!leftWrap || !rightWrap) return;

  const perWrapW = Math.max(220, Math.min(leftWrap.clientWidth, rightWrap.clientWidth) - 4);
  const availableH = Math.max(180, boardCard.clientHeight - 60);
  const stacked = leftWrap.getBoundingClientRect().top !== rightWrap.getBoundingClientRect().top;
  const perWrapH = stacked ? Math.max(160, Math.floor((availableH - 10) / 2)) : availableH;

  const targetH = Math.min(perWrapH, window.innerHeight * 0.46 * scaleRatio);
  const targetW = targetH * (GRID_W / GRID_H);
  const fitTarget = fitAspect(targetW, targetH, GRID_W / GRID_H);
  const fitFinal = fitAspect(Math.min(perWrapW, fitTarget.width), Math.min(perWrapH, fitTarget.height), GRID_W / GRID_H);
  setCanvasDisplaySize(onlineLeftCanvas, fitFinal.width, fitFinal.height);
  setCanvasDisplaySize(onlineRightCanvas, fitFinal.width, fitFinal.height);
}

function resizeAllCanvases() {
  resizeSingleCanvas();
  resizeOnlineCanvases();
}

function drawSingleBoard(now) {
  const w = singleCanvas.width;
  const h = singleCanvas.height;
  const cell = w / GRID_W;

  const g = singleCtx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, "#07172b");
  g.addColorStop(1, "#0a1421");
  singleCtx.fillStyle = g;
  singleCtx.fillRect(0, 0, w, h);

  singleCtx.strokeStyle = "rgba(120, 180, 230, 0.08)";
  singleCtx.lineWidth = 1;
  for (let x = 0; x <= GRID_W; x += 1) {
    singleCtx.beginPath();
    singleCtx.moveTo(x * cell + 0.5, 0);
    singleCtx.lineTo(x * cell + 0.5, h);
    singleCtx.stroke();
  }
  for (let y = 0; y <= GRID_H; y += 1) {
    singleCtx.beginPath();
    singleCtx.moveTo(0, y * cell + 0.5);
    singleCtx.lineTo(w, y * cell + 0.5);
    singleCtx.stroke();
  }

  const pulse = 0.6 + 0.4 * Math.sin(now / 180);
  const [fx, fy] = singleState.food;
  singleCtx.fillStyle = `rgba(255, 188, 120, ${0.75 + pulse * 0.2})`;
  singleCtx.beginPath();
  singleCtx.arc((fx + 0.5) * cell, (fy + 0.5) * cell, cell * 0.26 + pulse * 1.8, 0, Math.PI * 2);
  singleCtx.fill();

  singleState.snake.forEach(([x, y], idx) => {
    const t = idx / Math.max(1, singleState.snake.length - 1);
    const r = Math.floor(124 * (1 - t) + 14 * t);
    const g2 = Math.floor(249 * (1 - t) + 94 * t);
    const b = Math.floor(255 * (1 - t) + 134 * t);
    singleCtx.fillStyle = `rgb(${r}, ${g2}, ${b})`;
    const pad = idx === 0 ? 2 : 3;
    singleCtx.fillRect(x * cell + pad, y * cell + pad, cell - pad * 2, cell - pad * 2);
  });
}

function singleLoop(now) {
  if (singleState.runningState === "running") {
    const interval = singleMoveMs();
    while (now - singleState.lastMoveAt >= interval) {
      singleState.lastMoveAt += interval;
      stepSingle();
      if (singleState.runningState !== "running") break;
    }
  }
  drawSingleBoard(now);
  requestAnimationFrame(singleLoop);
}

function setOnlineStatus(text, isError = false) {
  onlineStatusEl.textContent = text;
  onlineStatusEl.style.color = isError ? "#ffadad" : "#b9d7eb";
}

async function apiPost(path, payload) {
  const resp = await fetch(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload || {}),
  });
  const data = await resp.json();
  if (!resp.ok || !data.ok) {
    throw new Error(data.error || `HTTP ${resp.status}`);
  }
  return data;
}

function saveOnlineSession() {
  if (!onlineState.roomCode || !onlineState.token) return;
  localStorage.setItem(
    STORAGE_ONLINE,
    JSON.stringify({
      roomCode: onlineState.roomCode,
      token: onlineState.token,
      playerIndex: onlineState.playerIndex,
      host: onlineState.host,
      mode: onlineState.mode,
    }),
  );
}

function loadOnlineSession() {
  const raw = localStorage.getItem(STORAGE_ONLINE);
  if (!raw) return;
  try {
    const session = JSON.parse(raw);
    onlineState.roomCode = String(session.roomCode || "");
    onlineState.token = String(session.token || "");
    onlineState.playerIndex = Number.isInteger(session.playerIndex) ? session.playerIndex : -1;
    onlineState.host = Boolean(session.host);
    onlineState.mode = String(session.mode || "separate");
    if (onlineState.roomCode) {
      currentRoomCodeEl.textContent = onlineState.roomCode;
      roomCodeInput.value = onlineState.roomCode;
    }
  } catch (_err) {
    // ignore
  }
}

function clearOnlineSession() {
  localStorage.removeItem(STORAGE_ONLINE);
}

function showOnlineBoards(mode) {
  if (mode === "arena") {
    onlineArenaCanvas.classList.remove("hidden");
    onlineSplitWrap.classList.add("hidden");
  } else {
    onlineArenaCanvas.classList.add("hidden");
    onlineSplitWrap.classList.remove("hidden");
  }
  resizeOnlineCanvases();
}

function drawBoardBase(ctx, cellSize) {
  const w = Math.floor(GRID_W * cellSize);
  const h = Math.floor(GRID_H * cellSize);
  const grad = ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, "#081729");
  grad.addColorStop(1, "#0a1422");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);
  ctx.strokeStyle = "rgba(126, 186, 235, 0.08)";
  for (let x = 0; x <= GRID_W; x += 1) {
    ctx.beginPath();
    ctx.moveTo(x * cellSize + 0.5, 0);
    ctx.lineTo(x * cellSize + 0.5, h);
    ctx.stroke();
  }
  for (let y = 0; y <= GRID_H; y += 1) {
    ctx.beginPath();
    ctx.moveTo(0, y * cellSize + 0.5);
    ctx.lineTo(w, y * cellSize + 0.5);
    ctx.stroke();
  }
}

function drawFood(ctx, food, cellSize, color = "#ffbf78") {
  if (!food) return;
  const [x, y] = food;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc((x + 0.5) * cellSize, (y + 0.5) * cellSize, cellSize * 0.26, 0, Math.PI * 2);
  ctx.fill();
}

function drawSnake(ctx, snake, cellSize, headColor, tailColor) {
  if (!Array.isArray(snake)) return;
  snake.forEach(([x, y], idx) => {
    const t = idx / Math.max(1, snake.length - 1);
    const r = Math.floor(headColor[0] * (1 - t) + tailColor[0] * t);
    const g = Math.floor(headColor[1] * (1 - t) + tailColor[1] * t);
    const b = Math.floor(headColor[2] * (1 - t) + tailColor[2] * t);
    ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
    const pad = idx === 0 ? 2 : 3;
    ctx.fillRect(x * cellSize + pad, y * cellSize + pad, cellSize - pad * 2, cellSize - pad * 2);
  });
}

function renderArenaState(state) {
  const cell = onlineArenaCanvas.width / GRID_W;
  drawBoardBase(onlineArenaCtx, cell);
  drawFood(onlineArenaCtx, state.food, cell, "#ffd08e");
  drawSnake(onlineArenaCtx, state.snakes?.[0] || [], cell, [115, 240, 255], [12, 72, 120]);
  drawSnake(onlineArenaCtx, state.snakes?.[1] || [], cell, [255, 197, 128], [145, 63, 36]);
}

function renderSeparateState(state) {
  const cell = onlineLeftCanvas.width / GRID_W;
  drawBoardBase(onlineLeftCtx, cell);
  drawFood(onlineLeftCtx, state.foods?.[0], cell, "#ffd08e");
  drawSnake(onlineLeftCtx, state.snakes?.[0] || [], cell, [115, 240, 255], [12, 72, 120]);

  const rightCell = onlineRightCanvas.width / GRID_W;
  drawBoardBase(onlineRightCtx, rightCell);
  drawFood(onlineRightCtx, state.foods?.[1], rightCell, "#ffd08e");
  drawSnake(onlineRightCtx, state.snakes?.[1] || [], rightCell, [255, 197, 128], [145, 63, 36]);
}

function updateOnlineResult(state) {
  if (!state.ended) {
    onlineResultBanner.classList.add("hidden");
    return;
  }
  onlineResultBanner.classList.remove("hidden");
  if (state.winner === -1) {
    resultEmoji.textContent = "🤝";
    resultText.textContent = "平局";
    return;
  }
  if (state.winner === onlineState.playerIndex) {
    resultEmoji.textContent = "😄🎉✨";
    resultText.textContent = "你赢了";
  } else {
    resultEmoji.textContent = "😢";
    resultText.textContent = "你输了";
  }
}

function renderOnlineState(state) {
  onlineState.state = state;
  onlineState.mode = state.mode || onlineState.mode;
  showOnlineBoards(onlineState.mode);

  const p0 = state.players?.[0]?.name || "P1";
  const p1 = state.players?.[1]?.name || "P2";
  leftPlayerLabel.textContent = `左侧: ${p0}`;
  rightPlayerLabel.textContent = `右侧: ${p1}`;
  if (onlineState.playerIndex === 0) leftPlayerLabel.textContent += " (你)";
  if (onlineState.playerIndex === 1) rightPlayerLabel.textContent += " (你)";

  onlineScoreRowEl.textContent = `${p0} ${state.scores?.[0] ?? 0} : ${state.scores?.[1] ?? 0} ${p1}`;

  if (onlineState.mode === "arena") {
    renderArenaState(state);
  } else {
    renderSeparateState(state);
  }

  updateOnlineResult(state);

  if (state.started) {
    setOnlineStatus("对战进行中");
  } else if (!state.ended) {
    setOnlineStatus(state.message || "等待房主开始");
  } else {
    setOnlineStatus(state.message || "本局结束");
  }
}

async function pollOnlineState() {
  if (!onlineState.roomCode || !onlineState.token) return;
  if (onlineState.requestPending) return;
  onlineState.requestPending = true;
  try {
    const url = `/api/state?roomCode=${encodeURIComponent(onlineState.roomCode)}&token=${encodeURIComponent(onlineState.token)}`;
    const resp = await fetch(url, { cache: "no-store" });
    const data = await resp.json();
    if (!resp.ok || !data.ok) throw new Error(data.error || `HTTP ${resp.status}`);
    renderOnlineState(data.state);
  } catch (err) {
    setOnlineStatus(`连接中断: ${err.message}`, true);
  } finally {
    onlineState.requestPending = false;
  }
}

function startOnlinePolling() {
  if (onlineState.pollingTimer) {
    clearInterval(onlineState.pollingTimer);
  }
  onlineState.pollingTimer = setInterval(pollOnlineState, 120);
  pollOnlineState();
}

function normalizeRoomCode(text) {
  return String(text || "").toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 6);
}

async function handleCreateRoom() {
  const name = clampName(playerNameInput.value, "Player 1");
  const mode = onlineModeEl.value === "arena" ? "arena" : "separate";
  try {
    const res = await apiPost("/api/create", { name, mode });
    const data = res.data;
    onlineState.roomCode = data.roomCode;
    onlineState.token = data.token;
    onlineState.playerIndex = data.playerIndex;
    onlineState.host = Boolean(data.host);
    onlineState.mode = data.mode;
    currentRoomCodeEl.textContent = onlineState.roomCode;
    roomCodeInput.value = onlineState.roomCode;
    showOnlineBoards(onlineState.mode);
    saveOnlineSession();
    setOnlineStatus("房间已创建，等待另一位玩家加入");
    startOnlinePolling();
  } catch (err) {
    setOnlineStatus(`创建失败: ${err.message}`, true);
  }
}

async function handleJoinRoom() {
  const roomCode = normalizeRoomCode(roomCodeInput.value);
  roomCodeInput.value = roomCode;
  if (!roomCode) {
    setOnlineStatus("请先输入房间号", true);
    return;
  }
  const name = clampName(playerNameInput.value, "Player 2");
  try {
    const res = await apiPost("/api/join", { roomCode, name });
    const data = res.data;
    onlineState.roomCode = data.roomCode;
    onlineState.token = data.token;
    onlineState.playerIndex = data.playerIndex;
    onlineState.host = Boolean(data.host);
    onlineState.mode = data.mode;
    currentRoomCodeEl.textContent = onlineState.roomCode;
    roomCodeInput.value = onlineState.roomCode;
    showOnlineBoards(onlineState.mode);
    saveOnlineSession();
    setOnlineStatus("已加入房间，等待房主开始");
    if (data.state) renderOnlineState(data.state);
    startOnlinePolling();
  } catch (err) {
    setOnlineStatus(`加入失败: ${err.message}`, true);
  }
}

async function handleStartMatch() {
  if (!onlineState.roomCode || !onlineState.token) {
    setOnlineStatus("请先创建或加入房间", true);
    return;
  }
  try {
    const res = await apiPost("/api/start", {
      roomCode: onlineState.roomCode,
      token: onlineState.token,
    });
    renderOnlineState(res.state);
    setOnlineStatus("已开始对战");
  } catch (err) {
    setOnlineStatus(`开始失败: ${err.message}`, true);
  }
}

async function sendOnlineDirection(directionKey) {
  if (!onlineState.roomCode || !onlineState.token) return;
  try {
    const res = await apiPost("/api/input", {
      roomCode: onlineState.roomCode,
      token: onlineState.token,
      direction: directionKey,
    });
    renderOnlineState(res.state);
  } catch (err) {
    setOnlineStatus(`发送方向失败: ${err.message}`, true);
  }
}

async function copyInviteLink() {
  if (!onlineState.roomCode) {
    setOnlineStatus("还没有房间号", true);
    return;
  }
  const url = `${location.origin}${location.pathname}?tab=online&room=${encodeURIComponent(onlineState.roomCode)}`;
  try {
    await navigator.clipboard.writeText(url);
    setOnlineStatus("邀请链接已复制");
  } catch (_err) {
    setOnlineStatus(`复制失败，请手动复制: ${url}`, true);
  }
}

function switchTab(tabName) {
  tabState.active = tabName;
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tabName);
  });
  $("tab-single").classList.toggle("active", tabName === "single");
  $("tab-online").classList.toggle("active", tabName === "online");
  resizeAllCanvases();
}

function setupTabButtons() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      switchTab(btn.dataset.tab);
    });
  });
}

function setupSingleActions() {
  singleStartBtn.addEventListener("click", startOrResumeSingle);
  singlePauseBtn.addEventListener("click", pauseSingle);
  singleRestartBtn.addEventListener("click", restartSingle);

  singleSpeedEl.addEventListener("input", () => {
    singleState.speedLevel = Math.max(1, Math.min(9, Number(singleSpeedEl.value)));
    singleSpeedLabelEl.textContent = String(singleState.speedLevel);
    saveSingleRecords();
  });

  singleScaleEl.addEventListener("input", () => {
    setViewScale(Number(singleScaleEl.value));
  });

  singleDifficultyEl.addEventListener("change", () => {
    singleState.difficulty = singleDifficultyEl.value;
    saveSingleRecords();
  });

  singleModeEl.addEventListener("change", () => {
    singleState.mode = singleModeEl.value;
    saveSingleRecords();
  });

  reviveYesBtn.addEventListener("click", () => {
    reviveOverlay.classList.add("hidden");
    safeReviveSingle();
    singleState.runningState = "running";
    singleState.lastMoveAt = performance.now();
    updateSingleStats();
  });

  reviveNoBtn.addEventListener("click", () => {
    reviveOverlay.classList.add("hidden");
    gameOverSingle();
  });

  document.querySelectorAll("[data-single-dir]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const key = btn.dataset.singleDir;
      const map = {
        up: [0, -1],
        down: [0, 1],
        left: [-1, 0],
        right: [1, 0],
      };
      queueSingleDirection(map[key]);
    });
  });
}

function setupOnlineActions() {
  createRoomBtn.addEventListener("click", handleCreateRoom);
  joinRoomBtn.addEventListener("click", handleJoinRoom);
  startMatchBtn.addEventListener("click", handleStartMatch);
  copyInviteBtn.addEventListener("click", copyInviteLink);

  roomCodeInput.addEventListener("input", () => {
    roomCodeInput.value = normalizeRoomCode(roomCodeInput.value);
  });

  onlineScaleEl.addEventListener("input", () => {
    setViewScale(Number(onlineScaleEl.value));
  });

  document.querySelectorAll("[data-online-dir]").forEach((btn) => {
    btn.addEventListener("click", () => {
      sendOnlineDirection(btn.dataset.onlineDir);
    });
  });
}

function onKeyDown(event) {
  const dirMap = {
    ArrowUp: [0, -1],
    ArrowDown: [0, 1],
    ArrowLeft: [-1, 0],
    ArrowRight: [1, 0],
    w: [0, -1],
    s: [0, 1],
    a: [-1, 0],
    d: [1, 0],
    W: [0, -1],
    S: [0, 1],
    A: [-1, 0],
    D: [1, 0],
  };
  const onlineDirMap = {
    ArrowUp: "up",
    ArrowDown: "down",
    ArrowLeft: "left",
    ArrowRight: "right",
    w: "up",
    s: "down",
    a: "left",
    d: "right",
    W: "up",
    S: "down",
    A: "left",
    D: "right",
  };

  if (tabState.active === "single") {
    if (dirMap[event.key]) {
      event.preventDefault();
      queueSingleDirection(dirMap[event.key]);
      return;
    }
    if (event.key === " " || event.code === "Space") {
      event.preventDefault();
      if (singleState.runningState === "running") pauseSingle();
      else startOrResumeSingle();
      return;
    }
    if (event.key === "r" || event.key === "R") {
      event.preventDefault();
      restartSingle();
      return;
    }
    if (singleState.runningState === "revive") {
      if (event.key === "y" || event.key === "Y" || event.key === "Enter") {
        event.preventDefault();
        reviveYesBtn.click();
      } else if (event.key === "n" || event.key === "N") {
        event.preventDefault();
        reviveNoBtn.click();
      }
    }
    return;
  }

  if (tabState.active === "online" && onlineDirMap[event.key]) {
    event.preventDefault();
    sendOnlineDirection(onlineDirMap[event.key]);
  }
}

function applyQueryPrefill() {
  const query = new URLSearchParams(location.search);
  const room = normalizeRoomCode(query.get("room"));
  const tab = query.get("tab");
  if (room) {
    roomCodeInput.value = room;
  }
  if (tab === "online" || room) {
    switchTab("online");
  }
}

function initSingleMode() {
  loadSingleRecords();
  loadViewScale();
  resetSingleSnake();
  singleState.runningState = "ready";
  updateSingleStats();
  resizeAllCanvases();
}

function initOnlineMode() {
  loadOnlineSession();
  if (onlineState.roomCode && onlineState.token) {
    currentRoomCodeEl.textContent = onlineState.roomCode;
    startOnlinePolling();
    setOnlineStatus("正在恢复房间连接...");
  }
  resizeOnlineCanvases();
}

function bootstrap() {
  setupTabButtons();
  setupSingleActions();
  setupOnlineActions();
  initSingleMode();
  initOnlineMode();
  applyQueryPrefill();
  document.addEventListener("keydown", onKeyDown);
  window.addEventListener("resize", resizeAllCanvases);
  window.addEventListener("orientationchange", resizeAllCanvases);
  requestAnimationFrame(singleLoop);
}

bootstrap();
