const $ = (id) => document.getElementById(id);

const LIMITS = {
  cols: { min: 16, max: 72 },
  rows: { min: 12, max: 48 },
  speed: { min: 1, max: 10 },
  viewScale: { min: 70, max: 140 },
  cellSize: { min: 14, max: 30 },
};

const STORAGE_SETTINGS = "snake_web_settings_v3";
const STORAGE_ONLINE_SESSION = "snake_web_online_session_v2";

const DIRECTION_MAP = {
  up: [0, -1],
  down: [0, 1],
  left: [-1, 0],
  right: [1, 0],
};

const SNAKE_PALETTES = {
  neon: { head: "#7cf9ff", tail: "#0e4f74" },
  forest: { head: "#86ffbe", tail: "#1b6d46" },
  sunset: { head: "#ffd39a", tail: "#cb5d34" },
  glacier: { head: "#b5e7ff", tail: "#2c74a5" },
};
const FOOD_COLORS = {
  classic: "#ff6666",
  mint: "#63efb2",
  violet: "#b989ff",
  sun: "#ffcb62",
};

const SNAKE_SHAPES = new Set(["rounded", "square", "circle", "diamond"]);
const FOOD_STYLES = new Set(["orb", "crystal", "star", "ring"]);
const FOOD_COLOR_STYLES = new Set(["classic", "mint", "violet", "sun"]);
const MODES = new Set(["separate", "arena"]);

const I18N = {
  zh: {
    app_title: "Neon Snake Web",
    app_subtitle: "浏览器免安装版: 单人 + 双人在线",
    tab_single: "单人模式",
    tab_online: "双人在线",
    open_settings: "设置",
    settings_title: "游戏设置",
    global_settings: "全局显示",
    single_settings: "单人设置",
    online_settings: "双人设置",
    language: "语言",
    lang_zh: "中文",
    lang_en: "英文",
    lang_ja: "日文",
    view_scale: "画面缩放",
    cell_size: "格子大小",
    difficulty: "难度",
    difficulty_easy: "入门",
    difficulty_mixed: "进阶",
    difficulty_hard: "困难",
    speed_label: "速度",
    single_mode: "模式",
    mode_normal: "普通",
    mode_invincible: "无敌复活",
    snake_color: "蛇颜色",
    snake_color_neon: "霓虹青",
    snake_color_forest: "森林绿",
    snake_color_sunset: "落日橙",
    snake_color_glacier: "冰川蓝",
    snake_shape: "蛇形状",
    snake_shape_rounded: "圆角块",
    snake_shape_square: "方块",
    snake_shape_circle: "圆形",
    snake_shape_diamond: "菱形",
    food_style: "豆子样式",
    food_style_orb: "光球",
    food_style_crystal: "水晶",
    food_style_star: "星芒",
    food_style_ring: "光环",
    food_color: "豆子颜色",
    food_color_classic: "经典红",
    food_color_mint: "薄荷绿",
    food_color_violet: "紫晶色",
    food_color_sun: "太阳金",
    grid_cols: "列数",
    grid_rows: "行数",
    grid_size: "网格",
    single_panel_title: "单人信息",
    score: "Score",
    best: "Best",
    length: "Length",
    best_length: "Best Length",
    games_played: "累计局数",
    last_round: "上局 分/长",
    start_or_resume: "开始/继续",
    pause: "暂停",
    restart: "重开",
    mouse_control: "鼠标方向键",
    online_control: "双人操作",
    single_hint: "键盘: WASD/方向键, 空格暂停, R 重开, Y/N 复活",
    ready_title: "准备开始",
    ready_sub: "按方向键 / WASD / 点击方向键开始",
    paused_title: "已暂停",
    paused_sub: "按空格或点击开始/继续",
    over_title: "游戏结束",
    over_sub: "按 R 或点击重开",
    revive_prompt_title: "无敌模式: 是否复活?",
    revive_prompt_sub: "将从更安全的位置继续。",
    revive_yes: "复活继续 (Y)",
    revive_no: "结束本局 (N)",
    player_name: "你的昵称",
    player_name_ph: "Player",
    room_code: "房间号",
    room_code_ph: "输入 6 位房间号",
    create_room: "创建房间",
    join_room: "加入房间",
    start_match: "开始对战(房主)",
    copy_invite: "复制邀请链接",
    current_room: "当前房间",
    online_mode: "模式",
    online_mode_separate: "模式1: 分屏各吃各的",
    online_mode_arena: "模式2: 同屏抢同一颗豆子",
    mini_position: "小窗位置",
    mini_pos_right_top: "右上角",
    mini_pos_left_top: "左上角",
    self_view: "我的主视角",
    opponent_mini: "对手小窗",
    apply_room_config: "应用房间配置",
    apply_style: "同步我的样式",
    status_idle: "未连接房间",
    status_created: "房间已创建，等待另一位玩家加入",
    status_joined: "已加入房间，等待房主开始",
    status_wait_start: "等待房主开始",
    status_running: "对战进行中",
    status_countdown: "倒计时中",
    status_invite_copied: "邀请链接已复制",
    status_need_room: "请先创建或加入房间",
    status_not_host: "只有房主可修改房间配置",
    status_config_applied: "房间配置已同步",
    status_style_applied: "样式已同步",
    status_reconnect: "正在恢复房间连接...",
    status_link_copy_fail: "复制失败，请手动复制",
    error_prefix: "错误",
    result_wait: "等待结果",
    result_draw: "平局",
    result_you_win: "你赢了",
    result_you_lose: "你输了",
    countdown_title: "对战即将开始",
    you_tag: "你",
    online_hint: "双人是服务端权威同步，前端做即时输入反馈以降低体感延迟。",
  },
  en: {
    app_title: "Neon Snake Web",
    app_subtitle: "Browser edition: single player + online duel",
    tab_single: "Single",
    tab_online: "Online Duo",
    open_settings: "Settings",
    settings_title: "Game Settings",
    global_settings: "Global View",
    single_settings: "Single Settings",
    online_settings: "Online Settings",
    language: "Language",
    lang_zh: "Chinese",
    lang_en: "English",
    lang_ja: "Japanese",
    view_scale: "View Scale",
    cell_size: "Cell Size",
    difficulty: "Difficulty",
    difficulty_easy: "Beginner",
    difficulty_mixed: "Advanced",
    difficulty_hard: "Hardcore",
    speed_label: "Speed",
    single_mode: "Mode",
    mode_normal: "Normal",
    mode_invincible: "Invincible Revive",
    snake_color: "Snake Color",
    snake_color_neon: "Neon Cyan",
    snake_color_forest: "Forest Green",
    snake_color_sunset: "Sunset Orange",
    snake_color_glacier: "Glacier Blue",
    snake_shape: "Snake Shape",
    snake_shape_rounded: "Rounded",
    snake_shape_square: "Square",
    snake_shape_circle: "Circle",
    snake_shape_diamond: "Diamond",
    food_style: "Bean Style",
    food_style_orb: "Orb",
    food_style_crystal: "Crystal",
    food_style_star: "Star",
    food_style_ring: "Ring",
    food_color: "Bean Color",
    food_color_classic: "Classic Red",
    food_color_mint: "Mint Green",
    food_color_violet: "Violet",
    food_color_sun: "Sun Gold",
    grid_cols: "Cols",
    grid_rows: "Rows",
    grid_size: "Grid",
    single_panel_title: "Single Info",
    score: "Score",
    best: "Best",
    length: "Length",
    best_length: "Best Length",
    games_played: "Games",
    last_round: "Last Score/Len",
    start_or_resume: "Start/Resume",
    pause: "Pause",
    restart: "Restart",
    mouse_control: "Mouse D-Pad",
    online_control: "Duel Control",
    single_hint: "Keys: WASD/Arrows, Space pause, R restart, Y/N revive",
    ready_title: "Ready",
    ready_sub: "Use arrows / WASD / D-pad to start",
    paused_title: "Paused",
    paused_sub: "Press Space or Start/Resume",
    over_title: "Game Over",
    over_sub: "Press R or click Restart",
    revive_prompt_title: "Invincible mode: revive?",
    revive_prompt_sub: "You will continue from a safer lane.",
    revive_yes: "Revive (Y)",
    revive_no: "End Run (N)",
    player_name: "Your Name",
    player_name_ph: "Player",
    room_code: "Room Code",
    room_code_ph: "Enter 6-digit code",
    create_room: "Create",
    join_room: "Join",
    start_match: "Start (Host)",
    copy_invite: "Copy Invite",
    current_room: "Current Room",
    online_mode: "Mode",
    online_mode_separate: "Mode 1: split maps",
    online_mode_arena: "Mode 2: shared arena",
    mini_position: "Mini Window",
    mini_pos_right_top: "Top Right",
    mini_pos_left_top: "Top Left",
    self_view: "My Main View",
    opponent_mini: "Opponent Mini",
    apply_room_config: "Apply Room Config",
    apply_style: "Sync My Style",
    status_idle: "Not connected",
    status_created: "Room created, waiting for player 2",
    status_joined: "Joined room, waiting for host",
    status_wait_start: "Waiting for host to start",
    status_running: "Match running",
    status_countdown: "Countdown",
    status_invite_copied: "Invite link copied",
    status_need_room: "Create or join a room first",
    status_not_host: "Only host can change room config",
    status_config_applied: "Room config synced",
    status_style_applied: "Style synced",
    status_reconnect: "Restoring room session...",
    status_link_copy_fail: "Copy failed, use this link manually",
    error_prefix: "Error",
    result_wait: "Waiting result",
    result_draw: "Draw",
    result_you_win: "You win",
    result_you_lose: "You lose",
    countdown_title: "Match starts in",
    you_tag: "You",
    online_hint: "Duel uses server-authoritative sync with immediate local input feedback.",
  },
  ja: {
    app_title: "Neon Snake Web",
    app_subtitle: "ブラウザ版: 1人 + 2人オンライン",
    tab_single: "シングル",
    tab_online: "オンライン対戦",
    open_settings: "設定",
    settings_title: "ゲーム設定",
    global_settings: "全体表示",
    single_settings: "シングル設定",
    online_settings: "対戦設定",
    language: "言語",
    lang_zh: "中国語",
    lang_en: "英語",
    lang_ja: "日本語",
    view_scale: "表示倍率",
    cell_size: "セルサイズ",
    difficulty: "難易度",
    difficulty_easy: "ビギナー",
    difficulty_mixed: "アドバンス",
    difficulty_hard: "ハード",
    speed_label: "速度",
    single_mode: "モード",
    mode_normal: "通常",
    mode_invincible: "無敵復活",
    snake_color: "ヘビ色",
    snake_color_neon: "ネオンシアン",
    snake_color_forest: "フォレストグリーン",
    snake_color_sunset: "サンセットオレンジ",
    snake_color_glacier: "グレイシャーブルー",
    snake_shape: "ヘビ形状",
    snake_shape_rounded: "ラウンド",
    snake_shape_square: "スクエア",
    snake_shape_circle: "サークル",
    snake_shape_diamond: "ダイヤ",
    food_style: "エサスタイル",
    food_style_orb: "オーブ",
    food_style_crystal: "クリスタル",
    food_style_star: "スター",
    food_style_ring: "リング",
    food_color: "エサ色",
    food_color_classic: "クラシック赤",
    food_color_mint: "ミントグリーン",
    food_color_violet: "バイオレット",
    food_color_sun: "サンゴールド",
    grid_cols: "列数",
    grid_rows: "行数",
    grid_size: "グリッド",
    single_panel_title: "シングル情報",
    score: "Score",
    best: "Best",
    length: "Length",
    best_length: "Best Length",
    games_played: "ゲーム数",
    last_round: "前回 スコア/長さ",
    start_or_resume: "開始/再開",
    pause: "一時停止",
    restart: "リスタート",
    mouse_control: "マウス方向キー",
    online_control: "対戦操作",
    single_hint: "キー: WASD/矢印, Space一時停止, R再開, Y/N復活",
    ready_title: "準備完了",
    ready_sub: "矢印 / WASD / ボタンで開始",
    paused_title: "一時停止中",
    paused_sub: "Space または 開始/再開",
    over_title: "ゲームオーバー",
    over_sub: "R または リスタート",
    revive_prompt_title: "無敵モード: 復活しますか?",
    revive_prompt_sub: "より安全な位置で再開します。",
    revive_yes: "復活 (Y)",
    revive_no: "終了 (N)",
    player_name: "プレイヤー名",
    player_name_ph: "Player",
    room_code: "ルームコード",
    room_code_ph: "6桁コードを入力",
    create_room: "作成",
    join_room: "参加",
    start_match: "開始(ホスト)",
    copy_invite: "招待リンク",
    current_room: "現在ルーム",
    online_mode: "モード",
    online_mode_separate: "モード1: 分割マップ",
    online_mode_arena: "モード2: 共通マップ",
    mini_position: "ミニ位置",
    mini_pos_right_top: "右上",
    mini_pos_left_top: "左上",
    self_view: "自分のメイン画面",
    opponent_mini: "相手ミニ画面",
    apply_room_config: "ルーム設定を反映",
    apply_style: "自分の見た目を同期",
    status_idle: "未接続",
    status_created: "ルーム作成完了、相手待ち",
    status_joined: "参加済み、ホスト開始待ち",
    status_wait_start: "ホスト開始待ち",
    status_running: "対戦中",
    status_countdown: "カウントダウン中",
    status_invite_copied: "招待リンクをコピーしました",
    status_need_room: "先にルーム作成/参加してください",
    status_not_host: "ホストのみ設定変更できます",
    status_config_applied: "ルーム設定を同期しました",
    status_style_applied: "スタイルを同期しました",
    status_reconnect: "ルームを再接続中...",
    status_link_copy_fail: "コピー失敗、手動で共有してください",
    error_prefix: "エラー",
    result_wait: "結果待ち",
    result_draw: "引き分け",
    result_you_win: "あなたの勝ち",
    result_you_lose: "あなたの負け",
    countdown_title: "開始まで",
    you_tag: "あなた",
    online_hint: "対戦はサーバー同期方式で、操作入力は即時反映します。",
  },
};

const uiState = {
  tab: "single",
  language: "zh",
  viewScale: 100,
  cellSize: 24,
};

const singleState = {
  gridCols: 28,
  gridRows: 24,
  difficulty: "mixed",
  speedLevel: 5,
  mode: "normal",
  snakeColor: "neon",
  snakeShape: "rounded",
  foodStyle: "orb",
  snake: [],
  direction: [1, 0],
  nextDirection: [1, 0],
  food: [0, 0],
  score: 0,
  bestScore: 0,
  bestLength: 4,
  gamesPlayed: 0,
  lastScore: 0,
  lastLength: 4,
  runningState: "ready",
  lastMoveAt: 0,
};

const onlinePrefs = {
  mode: "separate",
  difficulty: "mixed",
  speedLevel: 5,
  gridCols: 32,
  gridRows: 24,
  miniPosition: "left-top",
  snakeColor: "sunset",
  snakeShape: "square",
  foodStyle: "crystal",
  foodColor: "classic",
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
  statusText: "",
  statusError: false,
};

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
const singleMetaRow = $("singleMetaRow");
const singleHint = $("singleHint");
const singleSpeedLabel = $("singleSpeedLabel");
const singleSpeedInlineEl = $("singleSpeedInline");
const singleSpeedInlineValue = $("singleSpeedInlineValue");
const singleDifficultyTag = $("singleDifficultyTag");
const singleModeTag = $("singleModeTag");
const singleGridTag = $("singleGridTag");
const singleDifficultyInlineEl = $("singleDifficultyInline");
const singleModeInlineEl = $("singleModeInline");
const singleSnakeColorInlineEl = $("singleSnakeColorInline");
const singleSnakeShapeInlineEl = $("singleSnakeShapeInline");
const singleFoodStyleInlineEl = $("singleFoodStyleInline");
const singleGridColsInlineEl = $("singleGridColsInline");
const singleGridRowsInlineEl = $("singleGridRowsInline");

const singleStartBtn = $("singleStartBtn");
const singlePauseBtn = $("singlePauseBtn");
const singleRestartBtn = $("singleRestartBtn");
const reviveYesBtn = $("reviveYesBtn");
const reviveNoBtn = $("reviveNoBtn");

const playerNameInput = $("playerNameInput");
const roomCodeInput = $("roomCodeInput");
const onlineModeQuickEl = $("onlineModeQuick");
const onlineDifficultyQuickEl = $("onlineDifficultyQuick");
const createRoomBtn = $("createRoomBtn");
const joinRoomBtn = $("joinRoomBtn");
const startMatchBtn = $("startMatchBtn");
const copyInviteBtn = $("copyInviteBtn");
const currentRoomCodeEl = $("currentRoomCode");
const onlineModeTag = $("onlineModeTag");
const onlineSpeedTag = $("onlineSpeedTag");
const onlineGridTag = $("onlineGridTag");
const onlineStatusEl = $("onlineStatus");
const onlineScoreRowEl = $("onlineScoreRow");

const onlineArenaCanvas = $("onlineArenaCanvas");
const onlineArenaCtx = onlineArenaCanvas.getContext("2d");
const onlineSeparateWrap = $("onlineSeparateWrap");
const onlineMainCanvas = $("onlineMainCanvas");
const onlineMainCtx = onlineMainCanvas.getContext("2d");
const onlineMiniWrap = $("onlineMiniWrap");
const onlineMiniCanvas = $("onlineMiniCanvas");
const onlineMiniCtx = onlineMiniCanvas.getContext("2d");
const onlineQuickPanel = $("onlineQuickPanel");
const mainPlayerLabel = $("mainPlayerLabel");
const miniPlayerLabel = $("miniPlayerLabel");
const onlineResultBanner = $("onlineResultBanner");
const resultEmoji = $("resultEmoji");
const resultText = $("resultText");
const onlineCountdownBanner = $("onlineCountdownBanner");
const onlineCountdownValue = $("onlineCountdownValue");

const settingsModal = $("settingsModal");
const openSettingsBtn = $("openSettingsBtn");
const closeSettingsBtn = $("closeSettingsBtn");
const languageSelect = $("languageSelect");
const viewScaleRange = $("viewScaleRange");
const viewScaleLabel = $("viewScaleLabel");
const cellSizeRange = $("cellSizeRange");
const cellSizeLabel = $("cellSizeLabel");

const singleDifficultyEl = $("singleDifficulty");
const singleSpeedEl = $("singleSpeed");
const singleModeEl = $("singleMode");
const singleSnakeColorEl = $("singleSnakeColor");
const singleSnakeShapeEl = $("singleSnakeShape");
const singleFoodStyleEl = $("singleFoodStyle");
const singleGridColsEl = $("singleGridCols");
const singleGridRowsEl = $("singleGridRows");

const onlineModeSettingEl = $("onlineModeSetting");
const onlineDifficultySettingEl = $("onlineDifficultySetting");
const onlineSpeedEl = $("onlineSpeed");
const onlineSpeedLabel = $("onlineSpeedLabel");
const onlineSnakeColorEl = $("onlineSnakeColor");
const onlineSnakeShapeEl = $("onlineSnakeShape");
const onlineFoodStyleEl = $("onlineFoodStyle");
const onlineFoodColorEl = $("onlineFoodColor");
const onlineGridColsEl = $("onlineGridCols");
const onlineGridRowsEl = $("onlineGridRows");
const miniMapPositionEl = $("miniMapPosition");
const applyOnlineConfigBtn = $("applyOnlineConfigBtn");
const applyOnlineStyleBtn = $("applyOnlineStyleBtn");
const onlineConfigHint = $("onlineConfigHint");
const onlineModePanelEl = $("onlineModePanel");
const onlineDifficultyPanelEl = $("onlineDifficultyPanel");
const onlineSpeedPanelEl = $("onlineSpeedPanel");
const onlineSpeedPanelLabel = $("onlineSpeedPanelLabel");
const miniMapPositionPanelEl = $("miniMapPositionPanel");
const onlineSnakeColorPanelEl = $("onlineSnakeColorPanel");
const onlineSnakeShapePanelEl = $("onlineSnakeShapePanel");
const onlineFoodStylePanelEl = $("onlineFoodStylePanel");
const onlineFoodColorPanelEl = $("onlineFoodColorPanel");
const onlineGridColsPanelEl = $("onlineGridColsPanel");
const onlineGridRowsPanelEl = $("onlineGridRowsPanel");
const applyOnlineConfigPanelBtn = $("applyOnlineConfigPanelBtn");
const applyOnlineStylePanelBtn = $("applyOnlineStylePanelBtn");

function t(key) {
  const dict = I18N[uiState.language] || I18N.zh;
  return dict[key] || I18N.zh[key] || key;
}

function clamp(value, minValue, maxValue) {
  return Math.max(minValue, Math.min(maxValue, value));
}

function intOr(value, fallback) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.floor(parsed);
}

function toCellKey(x, y) {
  return `${x},${y}`;
}

function normalizeMode(value) {
  return MODES.has(value) ? value : "separate";
}

function normalizeMiniPosition(value) {
  return value === "right-top" ? "right-top" : "left-top";
}

function normalizeStyle(style) {
  const source = style && typeof style === "object" ? style : {};
  const snakeColor = typeof source.snakeColor === "string" && SNAKE_PALETTES[source.snakeColor] ? source.snakeColor : "neon";
  const snakeShape = typeof source.snakeShape === "string" && SNAKE_SHAPES.has(source.snakeShape) ? source.snakeShape : "rounded";
  const foodStyle = typeof source.foodStyle === "string" && FOOD_STYLES.has(source.foodStyle) ? source.foodStyle : "orb";
  const foodColor = typeof source.foodColor === "string" && FOOD_COLOR_STYLES.has(source.foodColor) ? source.foodColor : "classic";
  return { snakeColor, snakeShape, foodStyle, foodColor };
}

function formatText(text, vars = {}) {
  return text.replace(/\{(\w+)\}/g, (_m, name) => {
    if (Object.prototype.hasOwnProperty.call(vars, name)) {
      return String(vars[name]);
    }
    return "";
  });
}

function clampName(raw, fallback) {
  const text = String(raw || "").trim();
  if (!text) return fallback;
  return text.slice(0, 14);
}

function normalizeRoomCode(text) {
  return String(text || "")
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, "")
    .slice(0, 6);
}

function isOpposite(a, b) {
  return a[0] === -b[0] && a[1] === -b[1];
}

function applyLanguageToDom() {
  document.documentElement.lang = uiState.language === "zh" ? "zh-CN" : uiState.language;
  document.title = t("app_title");

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (!key) return;
    el.textContent = t(key);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (!key) return;
    el.setAttribute("placeholder", t(key));
  });

  singleHint.textContent = t("single_hint");
  onlineConfigHint.textContent = t("online_hint");
  mainPlayerLabel.textContent = `${t("self_view")}: P1 (${t("you_tag")})`;
  miniPlayerLabel.textContent = `${t("opponent_mini")}: P2`;
  updateSingleOverlay();
  updateSingleStats();
  updateOnlineStaticTexts();
  if (onlineState.state) {
    renderOnlineState(onlineState.state);
  } else if (!onlineState.statusError) {
    setOnlineStatusKey("status_idle");
  }
}

function loadSettings() {
  const raw = localStorage.getItem(STORAGE_SETTINGS);
  if (!raw) return;
  try {
    const data = JSON.parse(raw);
    uiState.language = ["zh", "en", "ja"].includes(data.language) ? data.language : uiState.language;
    uiState.viewScale = clamp(intOr(data.viewScale, uiState.viewScale), LIMITS.viewScale.min, LIMITS.viewScale.max);
    uiState.cellSize = clamp(intOr(data.cellSize, uiState.cellSize), LIMITS.cellSize.min, LIMITS.cellSize.max);

    singleState.gridCols = clamp(intOr(data.singleGridCols, singleState.gridCols), LIMITS.cols.min, LIMITS.cols.max);
    singleState.gridRows = clamp(intOr(data.singleGridRows, singleState.gridRows), LIMITS.rows.min, LIMITS.rows.max);
    singleState.difficulty = ["easy", "mixed", "hard"].includes(data.singleDifficulty) ? data.singleDifficulty : singleState.difficulty;
    singleState.speedLevel = clamp(intOr(data.singleSpeedLevel, singleState.speedLevel), LIMITS.speed.min, LIMITS.speed.max);
    singleState.mode = ["normal", "invincible"].includes(data.singleMode) ? data.singleMode : singleState.mode;
    singleState.snakeColor = normalizeStyle({ snakeColor: data.singleSnakeColor }).snakeColor;
    singleState.snakeShape = normalizeStyle({ snakeShape: data.singleSnakeShape }).snakeShape;
    singleState.foodStyle = normalizeStyle({ foodStyle: data.singleFoodStyle }).foodStyle;
    singleState.bestScore = Math.max(0, intOr(data.bestScore, singleState.bestScore));
    singleState.bestLength = Math.max(4, intOr(data.bestLength, singleState.bestLength));
    singleState.gamesPlayed = Math.max(0, intOr(data.gamesPlayed, singleState.gamesPlayed));
    singleState.lastScore = Math.max(0, intOr(data.lastScore, singleState.lastScore));
    singleState.lastLength = Math.max(4, intOr(data.lastLength, singleState.lastLength));

    onlinePrefs.mode = normalizeMode(data.onlineMode);
    onlinePrefs.difficulty = ["easy", "mixed", "hard"].includes(data.onlineDifficulty) ? data.onlineDifficulty : onlinePrefs.difficulty;
    onlinePrefs.speedLevel = clamp(intOr(data.onlineSpeedLevel, onlinePrefs.speedLevel), LIMITS.speed.min, LIMITS.speed.max);
    onlinePrefs.gridCols = clamp(intOr(data.onlineGridCols, onlinePrefs.gridCols), LIMITS.cols.min, LIMITS.cols.max);
    onlinePrefs.gridRows = clamp(intOr(data.onlineGridRows, onlinePrefs.gridRows), LIMITS.rows.min, LIMITS.rows.max);
    onlinePrefs.miniPosition = normalizeMiniPosition(data.onlineMiniPosition);
    onlinePrefs.snakeColor = normalizeStyle({ snakeColor: data.onlineSnakeColor }).snakeColor;
    onlinePrefs.snakeShape = normalizeStyle({ snakeShape: data.onlineSnakeShape }).snakeShape;
    onlinePrefs.foodStyle = normalizeStyle({ foodStyle: data.onlineFoodStyle }).foodStyle;
    onlinePrefs.foodColor = normalizeStyle({ foodColor: data.onlineFoodColor }).foodColor;
  } catch (_err) {
    // ignore invalid storage
  }
}

function saveSettings() {
  const payload = {
    language: uiState.language,
    viewScale: uiState.viewScale,
    cellSize: uiState.cellSize,
    singleGridCols: singleState.gridCols,
    singleGridRows: singleState.gridRows,
    singleDifficulty: singleState.difficulty,
    singleSpeedLevel: singleState.speedLevel,
    singleMode: singleState.mode,
    singleSnakeColor: singleState.snakeColor,
    singleSnakeShape: singleState.snakeShape,
    singleFoodStyle: singleState.foodStyle,
    bestScore: singleState.bestScore,
    bestLength: singleState.bestLength,
    gamesPlayed: singleState.gamesPlayed,
    lastScore: singleState.lastScore,
    lastLength: singleState.lastLength,
    onlineMode: onlinePrefs.mode,
    onlineDifficulty: onlinePrefs.difficulty,
    onlineSpeedLevel: onlinePrefs.speedLevel,
    onlineGridCols: onlinePrefs.gridCols,
    onlineGridRows: onlinePrefs.gridRows,
    onlineMiniPosition: onlinePrefs.miniPosition,
    onlineSnakeColor: onlinePrefs.snakeColor,
    onlineSnakeShape: onlinePrefs.snakeShape,
    onlineFoodStyle: onlinePrefs.foodStyle,
    onlineFoodColor: onlinePrefs.foodColor,
  };
  localStorage.setItem(STORAGE_SETTINGS, JSON.stringify(payload));
}

function saveOnlineSession() {
  if (!onlineState.roomCode || !onlineState.token) return;
  const payload = {
    roomCode: onlineState.roomCode,
    token: onlineState.token,
    playerIndex: onlineState.playerIndex,
    host: onlineState.host,
    mode: onlineState.mode,
  };
  localStorage.setItem(STORAGE_ONLINE_SESSION, JSON.stringify(payload));
}

function clearOnlineSession() {
  localStorage.removeItem(STORAGE_ONLINE_SESSION);
}

function loadOnlineSession() {
  const raw = localStorage.getItem(STORAGE_ONLINE_SESSION);
  if (!raw) return;
  try {
    const data = JSON.parse(raw);
    onlineState.roomCode = normalizeRoomCode(data.roomCode);
    onlineState.token = String(data.token || "");
    onlineState.playerIndex = Number.isInteger(data.playerIndex) ? data.playerIndex : -1;
    onlineState.host = Boolean(data.host);
    onlineState.mode = normalizeMode(data.mode);
  } catch (_err) {
    // ignore invalid session
  }
}

function updateControlsFromState() {
  languageSelect.value = uiState.language;
  viewScaleRange.value = String(uiState.viewScale);
  cellSizeRange.value = String(uiState.cellSize);
  viewScaleLabel.textContent = `${uiState.viewScale}%`;
  cellSizeLabel.textContent = `${uiState.cellSize}px`;

  singleDifficultyEl.value = singleState.difficulty;
  singleDifficultyInlineEl.value = singleState.difficulty;
  singleSpeedEl.value = String(singleState.speedLevel);
  singleSpeedInlineEl.value = String(singleState.speedLevel);
  singleSpeedLabel.textContent = String(singleState.speedLevel);
  singleModeEl.value = singleState.mode;
  singleModeInlineEl.value = singleState.mode;
  singleSnakeColorEl.value = singleState.snakeColor;
  singleSnakeColorInlineEl.value = singleState.snakeColor;
  singleSnakeShapeEl.value = singleState.snakeShape;
  singleSnakeShapeInlineEl.value = singleState.snakeShape;
  singleFoodStyleEl.value = singleState.foodStyle;
  singleFoodStyleInlineEl.value = singleState.foodStyle;
  singleGridColsEl.value = String(singleState.gridCols);
  singleGridRowsEl.value = String(singleState.gridRows);
  singleGridColsInlineEl.value = String(singleState.gridCols);
  singleGridRowsInlineEl.value = String(singleState.gridRows);

  onlineModeSettingEl.value = onlinePrefs.mode;
  onlineModeQuickEl.value = onlinePrefs.mode;
  onlineModePanelEl.value = onlinePrefs.mode;
  onlineDifficultySettingEl.value = onlinePrefs.difficulty;
  onlineDifficultyQuickEl.value = onlinePrefs.difficulty;
  onlineDifficultyPanelEl.value = onlinePrefs.difficulty;
  onlineSpeedEl.value = String(onlinePrefs.speedLevel);
  onlineSpeedLabel.textContent = String(onlinePrefs.speedLevel);
  onlineSpeedPanelEl.value = String(onlinePrefs.speedLevel);
  onlineSpeedPanelLabel.textContent = String(onlinePrefs.speedLevel);
  onlineSnakeColorEl.value = onlinePrefs.snakeColor;
  onlineSnakeColorPanelEl.value = onlinePrefs.snakeColor;
  onlineSnakeShapeEl.value = onlinePrefs.snakeShape;
  onlineSnakeShapePanelEl.value = onlinePrefs.snakeShape;
  onlineFoodStyleEl.value = onlinePrefs.foodStyle;
  onlineFoodStylePanelEl.value = onlinePrefs.foodStyle;
  onlineFoodColorEl.value = onlinePrefs.foodColor;
  onlineFoodColorPanelEl.value = onlinePrefs.foodColor;
  onlineGridColsEl.value = String(onlinePrefs.gridCols);
  onlineGridRowsEl.value = String(onlinePrefs.gridRows);
  onlineGridColsPanelEl.value = String(onlinePrefs.gridCols);
  onlineGridRowsPanelEl.value = String(onlinePrefs.gridRows);
  miniMapPositionEl.value = onlinePrefs.miniPosition;
  miniMapPositionPanelEl.value = onlinePrefs.miniPosition;
}

function applyMiniPositionClass() {
  onlineMiniWrap.classList.remove("mini-pos-right-top", "mini-pos-left-top");
  onlineQuickPanel.classList.remove("panel-pos-right", "panel-pos-left");
  if (onlinePrefs.miniPosition === "left-top") {
    onlineMiniWrap.classList.add("mini-pos-left-top");
    onlineQuickPanel.classList.add("panel-pos-right");
  } else {
    onlineMiniWrap.classList.add("mini-pos-right-top");
    onlineQuickPanel.classList.add("panel-pos-left");
  }
}

function singleMoveMs() {
  return 224 - (singleState.speedLevel - 1) * 15;
}

function resetSingleSnake() {
  const cols = singleState.gridCols;
  const rows = singleState.gridRows;
  const centerX = Math.floor(cols / 2);
  const centerY = Math.floor(rows / 2);
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

function freeNeighborCount(cell, occupied, cols, rows) {
  const [x, y] = cell;
  const around = [
    [x + 1, y],
    [x - 1, y],
    [x, y + 1],
    [x, y - 1],
  ];
  let count = 0;
  for (const [nx, ny] of around) {
    if (nx < 0 || nx >= cols || ny < 0 || ny >= rows) continue;
    if (!occupied.has(toCellKey(nx, ny))) count += 1;
  }
  return count;
}

function spawnSingleFood() {
  const cols = singleState.gridCols;
  const rows = singleState.gridRows;
  const occupied = new Set(singleState.snake.map(([x, y]) => toCellKey(x, y)));
  const empty = [];
  for (let y = 0; y < rows; y += 1) {
    for (let x = 0; x < cols; x += 1) {
      if (!occupied.has(toCellKey(x, y))) empty.push([x, y]);
    }
  }
  if (empty.length === 0) return [Math.floor(cols / 2), Math.floor(rows / 2)];

  if (singleState.difficulty === "mixed") {
    return empty[Math.floor(Math.random() * empty.length)];
  }

  const [hx, hy] = singleState.snake[0] || [Math.floor(cols / 2), Math.floor(rows / 2)];
  const scored = empty.map(([x, y]) => {
    const wallDist = Math.min(x, cols - 1 - x, y, rows - 1 - y);
    const headDist = Math.abs(hx - x) + Math.abs(hy - y);
    const freeCount = freeNeighborCount([x, y], occupied, cols, rows);
    let score = 0;
    if (singleState.difficulty === "easy") {
      score = wallDist * 2.6 + freeCount * 2.0 + headDist * 0.24;
    } else {
      score = (4 - wallDist) * 2.2 + (4 - freeCount) * 1.4 + headDist * 0.07;
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
    singleOverlayTitle.textContent = t("ready_title");
    singleOverlaySub.textContent = t("ready_sub");
    return;
  }
  if (singleState.runningState === "paused") {
    singleOverlayTitle.textContent = t("paused_title");
    singleOverlaySub.textContent = t("paused_sub");
    return;
  }
  singleOverlayTitle.textContent = t("over_title");
  singleOverlaySub.textContent = t("over_sub");
}

function updateSingleStats() {
  singleScoreEl.textContent = String(singleState.score);
  singleBestEl.textContent = String(singleState.bestScore);
  singleLengthEl.textContent = String(singleState.snake.length);
  singleBestLengthEl.textContent = String(singleState.bestLength);
  singleMetaRow.textContent = `${t("games_played")}: ${singleState.gamesPlayed} | ${t("last_round")}: ${singleState.lastScore}/${singleState.lastLength}`;
  singleSpeedEl.value = String(singleState.speedLevel);
  singleSpeedInlineEl.value = String(singleState.speedLevel);
  singleSpeedLabel.textContent = String(singleState.speedLevel);
  singleSpeedInlineValue.textContent = String(singleState.speedLevel);
  singleDifficultyTag.textContent = t(`difficulty_${singleState.difficulty}`);
  singleModeTag.textContent = singleState.mode === "invincible" ? t("mode_invincible") : t("mode_normal");
  singleGridTag.textContent = `${singleState.gridCols} x ${singleState.gridRows}`;
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

function recordSingleRound() {
  singleState.gamesPlayed += 1;
  singleState.lastScore = singleState.score;
  singleState.lastLength = singleState.snake.length;
  singleState.bestScore = Math.max(singleState.bestScore, singleState.score);
  singleState.bestLength = Math.max(singleState.bestLength, singleState.snake.length);
  saveSettings();
}

function gameOverSingle() {
  recordSingleRound();
  singleState.runningState = "over";
  reviveOverlay.classList.add("hidden");
  updateSingleStats();
}

function buildRandomReviveSnake(targetLength, cols, rows, attempts = 300) {
  if (targetLength < 4) return null;
  const minWallDistance = cols >= 12 && rows >= 12 ? 2 : 1;
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    const start = [Math.floor(Math.random() * cols), Math.floor(Math.random() * rows)];
    const snake = [start];
    const occupied = new Set([toCellKey(start[0], start[1])]);

    while (snake.length < targetLength) {
      const [cx, cy] = snake[snake.length - 1];
      const candidates = [];
      for (const [dx, dy] of Object.values(DIRECTION_MAP)) {
        const nx = cx + dx;
        const ny = cy + dy;
        if (nx < 0 || nx >= cols || ny < 0 || ny >= rows) continue;
        const key = toCellKey(nx, ny);
        if (occupied.has(key)) continue;
        const tempOccupied = new Set(occupied);
        tempOccupied.add(key);
        const free = freeNeighborCount([nx, ny], tempOccupied, cols, rows);
        const wallDist = Math.min(nx, cols - 1 - nx, ny, rows - 1 - ny);
        const score = free * 2.4 + wallDist * 0.9 + Math.random() * 0.4;
        candidates.push({ cell: [nx, ny], score });
      }
      if (!candidates.length) break;
      candidates.sort((a, b) => b.score - a.score);
      const pool = candidates.slice(0, Math.min(3, candidates.length));
      const chosen = pool[Math.floor(Math.random() * pool.length)].cell;
      snake.push(chosen);
      occupied.add(toCellKey(chosen[0], chosen[1]));
    }

    if (snake.length === targetLength) {
      const [hx, hy] = snake[0];
      const wallDist = Math.min(hx, cols - 1 - hx, hy, rows - 1 - hy);
      if (wallDist < minWallDistance) {
        continue;
      }
      let nearbyBody = 0;
      for (let idx = 2; idx < snake.length; idx += 1) {
        const [bx, by] = snake[idx];
        if (Math.abs(bx - hx) + Math.abs(by - hy) <= 2) {
          nearbyBody += 1;
        }
      }
      if (nearbyBody > 3) {
        continue;
      }
      return { snake };
    }
  }
  return null;
}

function pickReviveDirection(snake, cols, rows) {
  if (!snake.length) return [1, 0];
  const occupied = new Set(snake.map(([x, y]) => toCellKey(x, y)));
  const tail = snake[snake.length - 1];
  const [hx, hy] = snake[0];
  const options = [];
  for (const [dx, dy] of Object.values(DIRECTION_MAP)) {
    const nx = hx + dx;
    const ny = hy + dy;
    const key = toCellKey(nx, ny);
    if (nx < 0 || nx >= cols || ny < 0 || ny >= rows) continue;
    const hitsBody = occupied.has(key) && (!tail || nx !== tail[0] || ny !== tail[1]);
    if (hitsBody) continue;
    const free = freeNeighborCount([nx, ny], occupied, cols, rows);
    const wallDist = Math.min(nx, cols - 1 - nx, ny, rows - 1 - ny);
    let forwardSpace = 0;
    for (let step = 1; step <= 3; step += 1) {
      const fx = hx + dx * step;
      const fy = hy + dy * step;
      if (fx < 0 || fx >= cols || fy < 0 || fy >= rows) break;
      const fKey = toCellKey(fx, fy);
      if (occupied.has(fKey) && (!tail || fx !== tail[0] || fy !== tail[1])) break;
      forwardSpace += 1;
    }
    const score = free * 2.2 + wallDist * 1.1 + forwardSpace * 1.6 + Math.random() * 0.5;
    options.push({ direction: [dx, dy], score });
  }
  if (options.length) {
    options.sort((a, b) => b.score - a.score);
    const pool = options.slice(0, Math.min(3, options.length));
    return pool[Math.floor(Math.random() * pool.length)].direction;
  }
  return inferDirectionFromSnake(snake, [1, 0]);
}

function safeReviveSingle() {
  const cols = singleState.gridCols;
  const rows = singleState.gridRows;
  const maxLength = Math.max(4, cols * rows - 1);
  const originalLength = clamp(singleState.snake.length, 4, maxLength);
  let revived = null;
  for (let length = originalLength; length >= 4; length -= 1) {
    revived = buildRandomReviveSnake(length, cols, rows, length > 45 ? 520 : 320);
    if (revived) break;
  }
  if (!revived) {
    resetSingleSnake();
    return;
  }
  const direction = pickReviveDirection(revived.snake, cols, rows);
  singleState.snake = revived.snake;
  singleState.direction = direction;
  singleState.nextDirection = direction;
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
  const cols = singleState.gridCols;
  const rows = singleState.gridRows;
  singleState.direction = singleState.nextDirection;
  const [hx, hy] = singleState.snake[0];
  const [dx, dy] = singleState.direction;
  const next = [hx + dx, hy + dy];
  const hitWall = next[0] < 0 || next[0] >= cols || next[1] < 0 || next[1] >= rows;
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
    saveSettings();
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

function hexToRgb(hex) {
  const normalized = String(hex || "").replace("#", "");
  if (normalized.length !== 6) return [255, 255, 255];
  return [0, 2, 4].map((index) => parseInt(normalized.slice(index, index + 2), 16));
}

function mixRgb(a, b, tValue) {
  const tClamped = clamp(tValue, 0, 1);
  return [
    Math.floor(a[0] * (1 - tClamped) + b[0] * tClamped),
    Math.floor(a[1] * (1 - tClamped) + b[1] * tClamped),
    Math.floor(a[2] * (1 - tClamped) + b[2] * tClamped),
  ];
}

function drawRoundedRectPath(ctx, x, y, width, height, radius) {
  const r = Math.max(0, Math.min(radius, Math.min(width, height) / 2));
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + width, y, x + width, y + height, r);
  ctx.arcTo(x + width, y + height, x, y + height, r);
  ctx.arcTo(x, y + height, x, y, r);
  ctx.arcTo(x, y, x + width, y, r);
  ctx.closePath();
}

function drawGridBackground(ctx, cols, rows, width, height) {
  const grad = ctx.createLinearGradient(0, 0, 0, height);
  grad.addColorStop(0, "#08192d");
  grad.addColorStop(1, "#0a1322");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, width, height);

  const cellW = width / cols;
  const cellH = height / rows;
  ctx.strokeStyle = "rgba(123, 189, 235, 0.08)";
  ctx.lineWidth = 1;
  for (let x = 0; x <= cols; x += 1) {
    const px = x * cellW + 0.5;
    ctx.beginPath();
    ctx.moveTo(px, 0);
    ctx.lineTo(px, height);
    ctx.stroke();
  }
  for (let y = 0; y <= rows; y += 1) {
    const py = y * cellH + 0.5;
    ctx.beginPath();
    ctx.moveTo(0, py);
    ctx.lineTo(width, py);
    ctx.stroke();
  }
}

function drawFood(ctx, food, cols, rows, canvas, style, now, colorKey = "classic") {
  if (!food) return;
  const [x, y] = food;
  const width = canvas.width;
  const height = canvas.height;
  const cellW = width / cols;
  const cellH = height / rows;
  const cell = Math.min(cellW, cellH);
  const cx = (x + 0.5) * cellW;
  const cy = (y + 0.5) * cellH;
  const pulse = (Math.sin(now / 140) + 1) * 0.5;
  ctx.save();
  const foodColor = FOOD_COLORS[colorKey] || FOOD_COLORS.classic;
  ctx.fillStyle = foodColor;
  ctx.strokeStyle = foodColor;
  ctx.lineWidth = Math.max(1.4, cell * 0.1);
  const radius = cell * (0.29 + pulse * 0.06);

  if (style === "crystal") {
    ctx.fillStyle = foodColor;
    ctx.beginPath();
    ctx.moveTo(cx, cy - cell * 0.34);
    ctx.lineTo(cx + cell * 0.24, cy);
    ctx.lineTo(cx, cy + cell * 0.34);
    ctx.lineTo(cx - cell * 0.24, cy);
    ctx.closePath();
    ctx.fill();
  } else if (style === "star") {
    ctx.fillStyle = foodColor;
    const outer = cell * 0.3 * pulse;
    const inner = outer * 0.48;
    ctx.beginPath();
    for (let i = 0; i < 10; i += 1) {
      const angle = -Math.PI / 2 + (i * Math.PI) / 5;
      const r = i % 2 === 0 ? outer : inner;
      const px = cx + Math.cos(angle) * r;
      const py = cy + Math.sin(angle) * r;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();
    ctx.fillStyle = "rgba(255,255,255,0.28)";
    ctx.beginPath();
    ctx.arc(cx, cy, inner * 0.55, 0, Math.PI * 2);
    ctx.fill();
  } else if (style === "ring") {
    ctx.strokeStyle = foodColor;
    ctx.lineWidth = Math.max(1.5, cell * 0.13);
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 1.2, 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillStyle = foodColor;
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 0.55, 0, Math.PI * 2);
    ctx.fill();
  } else {
    const outerRadius = cell * (0.44 + pulse * 0.06);
    const glow = ctx.createRadialGradient(cx, cy, 1, cx, cy, outerRadius);
    glow.addColorStop(0, foodColor);
    glow.addColorStop(1, "rgba(255, 109, 109, 0.02)");
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(cx, cy, outerRadius, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = foodColor;
    ctx.beginPath();
    ctx.arc(cx, cy, cell * 0.3, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

function inferDirectionFromSnake(snake, fallback = [1, 0]) {
  if (!Array.isArray(snake) || snake.length < 2) return fallback;
  const [hx, hy] = snake[0];
  const [nx, ny] = snake[1];
  const dx = hx - nx;
  const dy = hy - ny;
  if ((Math.abs(dx) === 1 && dy === 0) || (Math.abs(dy) === 1 && dx === 0)) {
    return [dx, dy];
  }
  return fallback;
}

function drawSnake(ctx, snake, cols, rows, canvas, palette, shape, headDirection = [1, 0]) {
  if (!Array.isArray(snake)) return;
  const width = canvas.width;
  const height = canvas.height;
  const cellW = width / cols;
  const cellH = height / rows;
  const headRgb = hexToRgb(palette.head);
  const tailRgb = hexToRgb(palette.tail);
  snake.forEach(([x, y], idx) => {
    const tValue = idx / Math.max(1, snake.length - 1);
    const [r, g, b] = mixRgb(headRgb, tailRgb, tValue);
    const pad = idx === 0 ? Math.max(1.8, Math.min(cellW, cellH) * 0.11) : Math.max(1.3, Math.min(cellW, cellH) * 0.16);
    const left = x * cellW + pad;
    const top = y * cellH + pad;
    const segW = Math.max(2, cellW - pad * 2);
    const segH = Math.max(2, cellH - pad * 2);
    ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
    ctx.save();
    if (shape === "circle") {
      const radius = Math.min(segW, segH) / 2;
      ctx.beginPath();
      ctx.arc(left + segW / 2, top + segH / 2, radius, 0, Math.PI * 2);
      ctx.fill();
    } else if (shape === "diamond") {
      ctx.beginPath();
      ctx.moveTo(left + segW / 2, top);
      ctx.lineTo(left + segW, top + segH / 2);
      ctx.lineTo(left + segW / 2, top + segH);
      ctx.lineTo(left, top + segH / 2);
      ctx.closePath();
      ctx.fill();
    } else if (shape === "rounded") {
      drawRoundedRectPath(ctx, left, top, segW, segH, Math.min(segW, segH) * 0.3);
      ctx.fill();
    } else {
      ctx.fillRect(left, top, segW, segH);
    }
    ctx.restore();
  });

  if (!snake.length) return;
  const [headX, headY] = snake[0];
  const baseX = headX * cellW;
  const baseY = headY * cellH;
  const cell = Math.min(cellW, cellH);
  const eyeSize = Math.max(2.4, cell * 0.14);
  const front = cell * 0.66;
  const back = cell * 0.3;
  const sideLow = cell * 0.28;
  const sideHigh = cell * 0.6;
  let eyes;
  if (headDirection[0] === 1) {
    eyes = [
      [front, sideLow],
      [front, sideHigh],
    ];
  } else if (headDirection[0] === -1) {
    eyes = [
      [back, sideLow],
      [back, sideHigh],
    ];
  } else if (headDirection[1] === -1) {
    eyes = [
      [sideLow, back],
      [sideHigh, back],
    ];
  } else {
    eyes = [
      [sideLow, front],
      [sideHigh, front],
    ];
  }
  ctx.save();
  ctx.fillStyle = "#052933";
  for (const [ox, oy] of eyes) {
    ctx.beginPath();
    ctx.arc(baseX + ox, baseY + oy, eyeSize / 2, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

function drawSingleBoard(now) {
  const cols = singleState.gridCols;
  const rows = singleState.gridRows;
  drawGridBackground(singleCtx, cols, rows, singleCanvas.width, singleCanvas.height);
  const palette = SNAKE_PALETTES[singleState.snakeColor] || SNAKE_PALETTES.neon;
  drawFood(singleCtx, singleState.food, cols, rows, singleCanvas, singleState.foodStyle, now, "classic");
  drawSnake(singleCtx, singleState.snake, cols, rows, singleCanvas, palette, singleState.snakeShape, singleState.direction);
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

function calcCellSize(cols, rows, maxWidth, maxHeight) {
  const desired = uiState.cellSize * (uiState.viewScale / 100);
  const fit = Math.min(maxWidth / cols, maxHeight / rows);
  return Math.max(8, Math.min(desired, fit));
}

function setCanvasDisplaySize(canvas, cols, rows, cellSizeCss) {
  const cssW = Math.max(120, Math.floor(cols * cellSizeCss));
  const cssH = Math.max(100, Math.floor(rows * cellSizeCss));
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  canvas.style.width = `${cssW}px`;
  canvas.style.height = `${cssH}px`;
  canvas.width = Math.floor(cssW * dpr);
  canvas.height = Math.floor(cssH * dpr);
}

function resizeSingleCanvas() {
  const maxW = Math.max(260, singleStage.clientWidth - 14);
  const maxH = Math.max(220, singleStage.clientHeight - 14);
  const cell = calcCellSize(singleState.gridCols, singleState.gridRows, maxW, maxH);
  setCanvasDisplaySize(singleCanvas, singleState.gridCols, singleState.gridRows, cell);
}

function getOnlineGrid() {
  if (onlineState.state) {
    return {
      cols: intOr(onlineState.state.gridCols, onlinePrefs.gridCols),
      rows: intOr(onlineState.state.gridRows, onlinePrefs.gridRows),
    };
  }
  return { cols: onlinePrefs.gridCols, rows: onlinePrefs.gridRows };
}

function resizeOnlineCanvases() {
  const boardCard = document.querySelector(".online-board-card");
  if (!boardCard) return;
  const grid = getOnlineGrid();
  if (onlineState.mode === "arena") {
    const maxW = Math.max(240, boardCard.clientWidth - 20);
    const maxH = Math.max(220, boardCard.clientHeight - 20);
    const cell = calcCellSize(grid.cols, grid.rows, maxW, maxH);
    setCanvasDisplaySize(onlineArenaCanvas, grid.cols, grid.rows, cell);
    return;
  }
  const maxW = Math.max(240, boardCard.clientWidth - 24);
  const maxH = Math.max(220, boardCard.clientHeight - 24);
  const mainCell = calcCellSize(grid.cols, grid.rows, maxW * 0.96, maxH * 0.96);
  setCanvasDisplaySize(onlineMainCanvas, grid.cols, grid.rows, mainCell);

  const miniCell = Math.max(6, mainCell * 0.4);
  setCanvasDisplaySize(onlineMiniCanvas, grid.cols, grid.rows, miniCell);
}

function resizeAllCanvases() {
  resizeSingleCanvas();
  resizeOnlineCanvases();
}

function setOnlineStatus(text, isError = false) {
  onlineState.statusText = text;
  onlineState.statusError = isError;
  onlineStatusEl.textContent = text;
  onlineStatusEl.style.color = isError ? "var(--bad)" : "#b8d8ed";
}

function setOnlineStatusKey(key, isError = false) {
  setOnlineStatus(t(key), isError);
}

async function apiPost(path, payload) {
  const resp = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
  const data = await resp.json();
  if (!resp.ok || !data.ok) {
    throw new Error(data.error || `HTTP ${resp.status}`);
  }
  return data;
}

function showOnlineBoards(mode) {
  onlineState.mode = normalizeMode(mode);
  if (onlineState.mode === "arena") {
    onlineArenaCanvas.classList.remove("hidden");
    onlineSeparateWrap.classList.add("hidden");
  } else {
    onlineArenaCanvas.classList.add("hidden");
    onlineSeparateWrap.classList.remove("hidden");
  }
  applyMiniPositionClass();
  resizeOnlineCanvases();
}

function getPlayerStyle(state, index) {
  const style = state?.players?.[index]?.style;
  return normalizeStyle(style);
}

function drawArenaState(state, now) {
  const cols = intOr(state.gridCols, onlinePrefs.gridCols);
  const rows = intOr(state.gridRows, onlinePrefs.gridRows);
  drawGridBackground(onlineArenaCtx, cols, rows, onlineArenaCanvas.width, onlineArenaCanvas.height);

  const p0Style = getPlayerStyle(state, 0);
  const p1Style = getPlayerStyle(state, 1);
  const viewerStyle = getPlayerStyle(state, clamp(onlineState.playerIndex, 0, 1));
  drawFood(onlineArenaCtx, state.food, cols, rows, onlineArenaCanvas, viewerStyle.foodStyle, now, viewerStyle.foodColor);
  drawSnake(
    onlineArenaCtx,
    state.snakes?.[0] || [],
    cols,
    rows,
    onlineArenaCanvas,
    SNAKE_PALETTES[p0Style.snakeColor] || SNAKE_PALETTES.neon,
    p0Style.snakeShape,
    inferDirectionFromSnake(state.snakes?.[0] || [], [1, 0]),
  );
  drawSnake(
    onlineArenaCtx,
    state.snakes?.[1] || [],
    cols,
    rows,
    onlineArenaCanvas,
    SNAKE_PALETTES[p1Style.snakeColor] || SNAKE_PALETTES.sunset,
    p1Style.snakeShape,
    inferDirectionFromSnake(state.snakes?.[1] || [], [-1, 0]),
  );
}

function drawSeparateState(state, now) {
  const cols = intOr(state.gridCols, onlinePrefs.gridCols);
  const rows = intOr(state.gridRows, onlinePrefs.gridRows);
  const myIndex = onlineState.playerIndex === 1 ? 1 : 0;
  const opIndex = myIndex === 0 ? 1 : 0;
  const myStyle = getPlayerStyle(state, myIndex);
  const opStyle = getPlayerStyle(state, opIndex);
  const mySnake = state.snakes?.[myIndex] || [];
  const opSnake = state.snakes?.[opIndex] || [];
  const myFood = state.foods?.[myIndex];
  const opFood = state.foods?.[opIndex];

  drawGridBackground(onlineMainCtx, cols, rows, onlineMainCanvas.width, onlineMainCanvas.height);
  drawFood(onlineMainCtx, myFood, cols, rows, onlineMainCanvas, myStyle.foodStyle, now, myStyle.foodColor);
  drawSnake(
    onlineMainCtx,
    mySnake,
    cols,
    rows,
    onlineMainCanvas,
    SNAKE_PALETTES[myStyle.snakeColor] || SNAKE_PALETTES.neon,
    myStyle.snakeShape,
    inferDirectionFromSnake(mySnake, [1, 0]),
  );

  drawGridBackground(onlineMiniCtx, cols, rows, onlineMiniCanvas.width, onlineMiniCanvas.height);
  drawFood(onlineMiniCtx, opFood, cols, rows, onlineMiniCanvas, opStyle.foodStyle, now, opStyle.foodColor);
  drawSnake(
    onlineMiniCtx,
    opSnake,
    cols,
    rows,
    onlineMiniCanvas,
    SNAKE_PALETTES[opStyle.snakeColor] || SNAKE_PALETTES.sunset,
    opStyle.snakeShape,
    inferDirectionFromSnake(opSnake, [-1, 0]),
  );
}

function updateOnlineStaticTexts() {
  const modeText = onlineState.mode === "arena" ? t("online_mode_arena") : t("online_mode_separate");
  const difficulty = onlineState.state?.difficulty || onlinePrefs.difficulty;
  onlineModeTag.textContent = `${modeText} | ${t("difficulty")}: ${t(`difficulty_${difficulty}`)}`;
  onlineSpeedTag.textContent = String(onlineState.state?.speedLevel || onlinePrefs.speedLevel);
  const cols = onlineState.state?.gridCols || onlinePrefs.gridCols;
  const rows = onlineState.state?.gridRows || onlinePrefs.gridRows;
  onlineGridTag.textContent = `${cols} x ${rows}`;
  if (!onlineState.state) {
    mainPlayerLabel.textContent = `${t("self_view")}: P1 (${t("you_tag")})`;
    miniPlayerLabel.textContent = `${t("opponent_mini")}: P2`;
  }
  applyMiniPositionClass();
}

function updateOnlineResult(state) {
  if (!state.ended) {
    onlineResultBanner.classList.add("hidden");
    onlineResultBanner.classList.remove("win", "lose", "draw");
    return;
  }
  onlineResultBanner.classList.remove("hidden");
  onlineResultBanner.classList.remove("win", "lose", "draw");
  if (state.winner === -1) {
    resultEmoji.textContent = "🤝";
    resultText.textContent = t("result_draw");
    onlineResultBanner.classList.add("draw");
    return;
  }
  if (state.winner === onlineState.playerIndex) {
    resultEmoji.textContent = "😄🎉🎆";
    resultText.textContent = t("result_you_win");
    onlineResultBanner.classList.add("win");
  } else {
    resultEmoji.textContent = "😢";
    resultText.textContent = t("result_you_lose");
    onlineResultBanner.classList.add("lose");
  }
}

function updateOnlineCountdown(state) {
  const remainingMs = Math.max(0, intOr(state.countdownMs, 0));
  if (remainingMs <= 0) {
    onlineCountdownBanner.classList.add("hidden");
    return;
  }
  onlineCountdownBanner.classList.remove("hidden");
  const sec = Math.max(1, Math.ceil(remainingMs / 1000));
  onlineCountdownValue.textContent = String(sec);
}

function renderOnlineState(state) {
  onlineState.state = state;
  onlineState.mode = normalizeMode(state.mode || onlineState.mode);
  onlinePrefs.mode = normalizeMode(state.mode || onlinePrefs.mode);
  onlinePrefs.difficulty = ["easy", "mixed", "hard"].includes(state.difficulty) ? state.difficulty : onlinePrefs.difficulty;
  onlinePrefs.speedLevel = clamp(intOr(state.speedLevel, onlinePrefs.speedLevel), LIMITS.speed.min, LIMITS.speed.max);
  onlinePrefs.gridCols = clamp(intOr(state.gridCols, onlinePrefs.gridCols), LIMITS.cols.min, LIMITS.cols.max);
  onlinePrefs.gridRows = clamp(intOr(state.gridRows, onlinePrefs.gridRows), LIMITS.rows.min, LIMITS.rows.max);
  showOnlineBoards(onlineState.mode);
  updateControlsFromState();
  updateOnlineStaticTexts();

  const p0 = state.players?.[0]?.name || "P1";
  const p1 = state.players?.[1]?.name || "P2";
  const myIndex = onlineState.playerIndex === 1 ? 1 : 0;
  const opIndex = myIndex === 0 ? 1 : 0;
  const names = [p0, p1];
  mainPlayerLabel.textContent = `${t("self_view")}: ${names[myIndex]} (${t("you_tag")})`;
  miniPlayerLabel.textContent = `${t("opponent_mini")}: ${names[opIndex] || "P2"}`;
  onlineScoreRowEl.textContent = `${p0} ${state.scores?.[0] ?? 0} : ${state.scores?.[1] ?? 0} ${p1}`;

  const now = performance.now();
  if (onlineState.mode === "arena") {
    drawArenaState(state, now);
  } else {
    drawSeparateState(state, now);
  }
  updateOnlineCountdown(state);
  updateOnlineResult(state);

  if (intOr(state.countdownMs, 0) > 0) {
    setOnlineStatus(`${t("status_countdown")}... ${Math.ceil(Math.max(0, state.countdownMs) / 1000)}`);
  } else if (state.started) {
    setOnlineStatusKey("status_running");
  } else if (state.ended) {
    setOnlineStatus(state.message || t("result_wait"));
  } else if ((state.players || []).length < 2) {
    setOnlineStatusKey("status_created");
  } else {
    setOnlineStatus(state.message || t("status_wait_start"));
  }
}

async function pollOnlineState() {
  if (!onlineState.roomCode || !onlineState.token || onlineState.requestPending) return;
  onlineState.requestPending = true;
  try {
    const url = `/api/state?roomCode=${encodeURIComponent(onlineState.roomCode)}&token=${encodeURIComponent(onlineState.token)}`;
    const resp = await fetch(url, { cache: "no-store" });
    const data = await resp.json();
    if (!resp.ok || !data.ok) throw new Error(data.error || `HTTP ${resp.status}`);
    renderOnlineState(data.state);
  } catch (err) {
    const message = String(err.message || "");
    if (message.includes("Room not found") || message.includes("Invalid token")) {
      clearOnlineSession();
      if (onlineState.pollingTimer) {
        clearInterval(onlineState.pollingTimer);
        onlineState.pollingTimer = null;
      }
      onlineState.roomCode = "";
      onlineState.token = "";
      onlineState.playerIndex = -1;
      onlineState.host = false;
      currentRoomCodeEl.textContent = "-";
    }
    setOnlineStatus(`${t("error_prefix")}: ${err.message}`, true);
  } finally {
    onlineState.requestPending = false;
  }
}

function startOnlinePolling() {
  if (onlineState.pollingTimer) {
    clearInterval(onlineState.pollingTimer);
  }
  onlineState.pollingTimer = setInterval(pollOnlineState, 110);
  pollOnlineState();
}

function currentOnlineStylePayload() {
  return {
    snakeColor: onlinePrefs.snakeColor,
    snakeShape: onlinePrefs.snakeShape,
    foodStyle: onlinePrefs.foodStyle,
    foodColor: onlinePrefs.foodColor,
  };
}

function currentOnlineConfigPayload() {
  return {
    mode: onlinePrefs.mode,
    difficulty: onlinePrefs.difficulty,
    speedLevel: onlinePrefs.speedLevel,
    gridCols: onlinePrefs.gridCols,
    gridRows: onlinePrefs.gridRows,
  };
}

async function handleCreateRoom() {
  const name = clampName(playerNameInput.value, "Player 1");
  onlinePrefs.mode = normalizeMode(onlineModeQuickEl.value);
  onlinePrefs.difficulty = ["easy", "mixed", "hard"].includes(onlineDifficultyQuickEl.value)
    ? onlineDifficultyQuickEl.value
    : "mixed";
  updateControlsFromState();
  updateOnlineStaticTexts();
  saveSettings();
  try {
    const res = await apiPost("/api/create", {
      name,
      ...currentOnlineConfigPayload(),
      style: currentOnlineStylePayload(),
    });
    const data = res.data;
    onlineState.roomCode = data.roomCode;
    onlineState.token = data.token;
    onlineState.playerIndex = data.playerIndex;
    onlineState.host = Boolean(data.host);
    onlineState.mode = normalizeMode(data.mode);
    currentRoomCodeEl.textContent = onlineState.roomCode;
    roomCodeInput.value = onlineState.roomCode;
    if (data.state) renderOnlineState(data.state);
    saveOnlineSession();
    setOnlineStatusKey("status_created");
    startOnlinePolling();
  } catch (err) {
    setOnlineStatus(`${t("error_prefix")}: ${err.message}`, true);
  }
}

async function handleJoinRoom() {
  const roomCode = normalizeRoomCode(roomCodeInput.value);
  roomCodeInput.value = roomCode;
  if (!roomCode) {
    setOnlineStatus(`${t("error_prefix")}: ${t("status_need_room")}`, true);
    return;
  }
  const name = clampName(playerNameInput.value, "Player 2");
  try {
    const res = await apiPost("/api/join", {
      roomCode,
      name,
      style: currentOnlineStylePayload(),
    });
    const data = res.data;
    onlineState.roomCode = data.roomCode;
    onlineState.token = data.token;
    onlineState.playerIndex = data.playerIndex;
    onlineState.host = Boolean(data.host);
    onlineState.mode = normalizeMode(data.mode);
    currentRoomCodeEl.textContent = onlineState.roomCode;
    roomCodeInput.value = onlineState.roomCode;
    if (data.state) renderOnlineState(data.state);
    saveOnlineSession();
    setOnlineStatusKey("status_joined");
    startOnlinePolling();
  } catch (err) {
    setOnlineStatus(`${t("error_prefix")}: ${err.message}`, true);
  }
}

async function handleStartMatch() {
  if (!onlineState.roomCode || !onlineState.token) {
    setOnlineStatusKey("status_need_room", true);
    return;
  }
  try {
    const res = await apiPost("/api/start", {
      roomCode: onlineState.roomCode,
      token: onlineState.token,
    });
    renderOnlineState(res.state);
    setOnlineStatusKey("status_running");
  } catch (err) {
    setOnlineStatus(`${t("error_prefix")}: ${err.message}`, true);
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
    setOnlineStatus(`${t("error_prefix")}: ${err.message}`, true);
  }
}

async function copyInviteLink() {
  if (!onlineState.roomCode) {
    setOnlineStatusKey("status_need_room", true);
    return;
  }
  const url = `${location.origin}${location.pathname}?tab=online&room=${encodeURIComponent(onlineState.roomCode)}`;
  try {
    await navigator.clipboard.writeText(url);
    setOnlineStatusKey("status_invite_copied");
  } catch (_err) {
    setOnlineStatus(`${t("status_link_copy_fail")}: ${url}`, true);
  }
}

async function applyOnlineConfigToRoom() {
  if (!onlineState.roomCode || !onlineState.token) {
    setOnlineStatusKey("status_need_room", true);
    return;
  }
  if (!onlineState.host) {
    setOnlineStatusKey("status_not_host", true);
    return;
  }
  try {
    const res = await apiPost("/api/room-config", {
      roomCode: onlineState.roomCode,
      token: onlineState.token,
      ...currentOnlineConfigPayload(),
    });
    renderOnlineState(res.state);
    setOnlineStatusKey("status_config_applied");
  } catch (err) {
    setOnlineStatus(`${t("error_prefix")}: ${err.message}`, true);
  }
}

async function applyOnlineStyleToRoom() {
  if (!onlineState.roomCode || !onlineState.token) {
    setOnlineStatusKey("status_need_room", true);
    return;
  }
  try {
    const res = await apiPost("/api/style", {
      roomCode: onlineState.roomCode,
      token: onlineState.token,
      style: currentOnlineStylePayload(),
    });
    renderOnlineState(res.state);
    setOnlineStatusKey("status_style_applied");
  } catch (err) {
    setOnlineStatus(`${t("error_prefix")}: ${err.message}`, true);
  }
}

function switchTab(tab) {
  uiState.tab = tab === "online" ? "online" : "single";
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === uiState.tab);
  });
  $("tab-single").classList.toggle("active", uiState.tab === "single");
  $("tab-online").classList.toggle("active", uiState.tab === "online");
  resizeAllCanvases();
}

function setupTabButtons() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      switchTab(btn.dataset.tab || "single");
    });
  });
}

function syncSingleGridSettings(source = "modal") {
  const colsInput = source === "inline" ? singleGridColsInlineEl : singleGridColsEl;
  const rowsInput = source === "inline" ? singleGridRowsInlineEl : singleGridRowsEl;
  const nextCols = clamp(intOr(colsInput.value, singleState.gridCols), LIMITS.cols.min, LIMITS.cols.max);
  const nextRows = clamp(intOr(rowsInput.value, singleState.gridRows), LIMITS.rows.min, LIMITS.rows.max);
  singleState.gridCols = nextCols;
  singleState.gridRows = nextRows;
  singleGridColsEl.value = String(nextCols);
  singleGridRowsEl.value = String(nextRows);
  singleGridColsInlineEl.value = String(nextCols);
  singleGridRowsInlineEl.value = String(nextRows);
  restartSingle();
  resizeAllCanvases();
  saveSettings();
}

function syncOnlineGridSettings(source = "modal") {
  const colsInput = source === "panel" ? onlineGridColsPanelEl : onlineGridColsEl;
  const rowsInput = source === "panel" ? onlineGridRowsPanelEl : onlineGridRowsEl;
  const nextCols = clamp(intOr(colsInput.value, onlinePrefs.gridCols), LIMITS.cols.min, LIMITS.cols.max);
  const nextRows = clamp(intOr(rowsInput.value, onlinePrefs.gridRows), LIMITS.rows.min, LIMITS.rows.max);
  onlinePrefs.gridCols = nextCols;
  onlinePrefs.gridRows = nextRows;
  onlineGridColsEl.value = String(nextCols);
  onlineGridRowsEl.value = String(nextRows);
  onlineGridColsPanelEl.value = String(nextCols);
  onlineGridRowsPanelEl.value = String(nextRows);
  updateOnlineStaticTexts();
  resizeOnlineCanvases();
  saveSettings();
}

function setupSettingsActions() {
  openSettingsBtn.addEventListener("click", () => {
    settingsModal.classList.remove("hidden");
  });
  closeSettingsBtn.addEventListener("click", () => {
    settingsModal.classList.add("hidden");
  });
  settingsModal.addEventListener("click", (event) => {
    if (event.target === settingsModal) settingsModal.classList.add("hidden");
  });

  languageSelect.addEventListener("change", () => {
    uiState.language = ["zh", "en", "ja"].includes(languageSelect.value) ? languageSelect.value : "zh";
    applyLanguageToDom();
    saveSettings();
  });

  viewScaleRange.addEventListener("input", () => {
    uiState.viewScale = clamp(intOr(viewScaleRange.value, uiState.viewScale), LIMITS.viewScale.min, LIMITS.viewScale.max);
    viewScaleLabel.textContent = `${uiState.viewScale}%`;
    resizeAllCanvases();
    saveSettings();
  });

  cellSizeRange.addEventListener("input", () => {
    uiState.cellSize = clamp(intOr(cellSizeRange.value, uiState.cellSize), LIMITS.cellSize.min, LIMITS.cellSize.max);
    cellSizeLabel.textContent = `${uiState.cellSize}px`;
    resizeAllCanvases();
    saveSettings();
  });

  singleDifficultyEl.addEventListener("change", () => {
    singleState.difficulty = singleDifficultyEl.value;
    singleDifficultyInlineEl.value = singleState.difficulty;
    updateSingleStats();
    saveSettings();
  });
  singleDifficultyInlineEl.addEventListener("change", () => {
    singleState.difficulty = singleDifficultyInlineEl.value;
    singleDifficultyEl.value = singleState.difficulty;
    updateSingleStats();
    saveSettings();
  });
  singleSpeedEl.addEventListener("input", () => {
    singleState.speedLevel = clamp(intOr(singleSpeedEl.value, singleState.speedLevel), LIMITS.speed.min, LIMITS.speed.max);
    singleSpeedInlineEl.value = String(singleState.speedLevel);
    singleSpeedInlineValue.textContent = String(singleState.speedLevel);
    singleSpeedLabel.textContent = String(singleState.speedLevel);
    updateSingleStats();
    saveSettings();
  });
  singleModeEl.addEventListener("change", () => {
    singleState.mode = singleModeEl.value;
    singleModeInlineEl.value = singleState.mode;
    updateSingleStats();
    saveSettings();
  });
  singleModeInlineEl.addEventListener("change", () => {
    singleState.mode = singleModeInlineEl.value;
    singleModeEl.value = singleState.mode;
    updateSingleStats();
    saveSettings();
  });
  singleSnakeColorEl.addEventListener("change", () => {
    singleState.snakeColor = normalizeStyle({ snakeColor: singleSnakeColorEl.value }).snakeColor;
    singleSnakeColorInlineEl.value = singleState.snakeColor;
    saveSettings();
  });
  singleSnakeColorInlineEl.addEventListener("change", () => {
    singleState.snakeColor = normalizeStyle({ snakeColor: singleSnakeColorInlineEl.value }).snakeColor;
    singleSnakeColorEl.value = singleState.snakeColor;
    saveSettings();
  });
  singleSnakeShapeEl.addEventListener("change", () => {
    singleState.snakeShape = normalizeStyle({ snakeShape: singleSnakeShapeEl.value }).snakeShape;
    singleSnakeShapeInlineEl.value = singleState.snakeShape;
    saveSettings();
  });
  singleSnakeShapeInlineEl.addEventListener("change", () => {
    singleState.snakeShape = normalizeStyle({ snakeShape: singleSnakeShapeInlineEl.value }).snakeShape;
    singleSnakeShapeEl.value = singleState.snakeShape;
    saveSettings();
  });
  singleFoodStyleEl.addEventListener("change", () => {
    singleState.foodStyle = normalizeStyle({ foodStyle: singleFoodStyleEl.value }).foodStyle;
    singleFoodStyleInlineEl.value = singleState.foodStyle;
    saveSettings();
  });
  singleFoodStyleInlineEl.addEventListener("change", () => {
    singleState.foodStyle = normalizeStyle({ foodStyle: singleFoodStyleInlineEl.value }).foodStyle;
    singleFoodStyleEl.value = singleState.foodStyle;
    saveSettings();
  });
  singleGridColsEl.addEventListener("change", () => syncSingleGridSettings("modal"));
  singleGridRowsEl.addEventListener("change", () => syncSingleGridSettings("modal"));
  singleGridColsInlineEl.addEventListener("change", () => syncSingleGridSettings("inline"));
  singleGridRowsInlineEl.addEventListener("change", () => syncSingleGridSettings("inline"));
  singleSpeedInlineEl.addEventListener("input", () => {
    singleState.speedLevel = clamp(intOr(singleSpeedInlineEl.value, singleState.speedLevel), LIMITS.speed.min, LIMITS.speed.max);
    singleSpeedEl.value = String(singleState.speedLevel);
    singleSpeedLabel.textContent = String(singleState.speedLevel);
    singleSpeedInlineValue.textContent = String(singleState.speedLevel);
    updateSingleStats();
    saveSettings();
  });

  onlineModeSettingEl.addEventListener("change", () => {
    onlinePrefs.mode = normalizeMode(onlineModeSettingEl.value);
    onlineModeQuickEl.value = onlinePrefs.mode;
    onlineModePanelEl.value = onlinePrefs.mode;
    updateOnlineStaticTexts();
    saveSettings();
  });
  onlineModePanelEl.addEventListener("change", () => {
    onlinePrefs.mode = normalizeMode(onlineModePanelEl.value);
    onlineModeSettingEl.value = onlinePrefs.mode;
    onlineModeQuickEl.value = onlinePrefs.mode;
    updateOnlineStaticTexts();
    saveSettings();
  });
  onlineDifficultySettingEl.addEventListener("change", () => {
    onlinePrefs.difficulty = ["easy", "mixed", "hard"].includes(onlineDifficultySettingEl.value)
      ? onlineDifficultySettingEl.value
      : "mixed";
    onlineDifficultyQuickEl.value = onlinePrefs.difficulty;
    onlineDifficultyPanelEl.value = onlinePrefs.difficulty;
    saveSettings();
  });
  onlineDifficultyPanelEl.addEventListener("change", () => {
    onlinePrefs.difficulty = ["easy", "mixed", "hard"].includes(onlineDifficultyPanelEl.value)
      ? onlineDifficultyPanelEl.value
      : "mixed";
    onlineDifficultySettingEl.value = onlinePrefs.difficulty;
    onlineDifficultyQuickEl.value = onlinePrefs.difficulty;
    saveSettings();
  });
  onlineSpeedEl.addEventListener("input", () => {
    onlinePrefs.speedLevel = clamp(intOr(onlineSpeedEl.value, onlinePrefs.speedLevel), LIMITS.speed.min, LIMITS.speed.max);
    onlineSpeedLabel.textContent = String(onlinePrefs.speedLevel);
    onlineSpeedPanelEl.value = String(onlinePrefs.speedLevel);
    onlineSpeedPanelLabel.textContent = String(onlinePrefs.speedLevel);
    updateOnlineStaticTexts();
    saveSettings();
  });
  onlineSpeedPanelEl.addEventListener("input", () => {
    onlinePrefs.speedLevel = clamp(intOr(onlineSpeedPanelEl.value, onlinePrefs.speedLevel), LIMITS.speed.min, LIMITS.speed.max);
    onlineSpeedEl.value = String(onlinePrefs.speedLevel);
    onlineSpeedLabel.textContent = String(onlinePrefs.speedLevel);
    onlineSpeedPanelLabel.textContent = String(onlinePrefs.speedLevel);
    updateOnlineStaticTexts();
    saveSettings();
  });
  onlineSnakeColorEl.addEventListener("change", () => {
    onlinePrefs.snakeColor = normalizeStyle({ snakeColor: onlineSnakeColorEl.value }).snakeColor;
    onlineSnakeColorPanelEl.value = onlinePrefs.snakeColor;
    saveSettings();
  });
  onlineSnakeColorPanelEl.addEventListener("change", () => {
    onlinePrefs.snakeColor = normalizeStyle({ snakeColor: onlineSnakeColorPanelEl.value }).snakeColor;
    onlineSnakeColorEl.value = onlinePrefs.snakeColor;
    saveSettings();
  });
  onlineSnakeShapeEl.addEventListener("change", () => {
    onlinePrefs.snakeShape = normalizeStyle({ snakeShape: onlineSnakeShapeEl.value }).snakeShape;
    onlineSnakeShapePanelEl.value = onlinePrefs.snakeShape;
    saveSettings();
  });
  onlineSnakeShapePanelEl.addEventListener("change", () => {
    onlinePrefs.snakeShape = normalizeStyle({ snakeShape: onlineSnakeShapePanelEl.value }).snakeShape;
    onlineSnakeShapeEl.value = onlinePrefs.snakeShape;
    saveSettings();
  });
  onlineFoodStyleEl.addEventListener("change", () => {
    onlinePrefs.foodStyle = normalizeStyle({ foodStyle: onlineFoodStyleEl.value }).foodStyle;
    onlineFoodStylePanelEl.value = onlinePrefs.foodStyle;
    saveSettings();
  });
  onlineFoodStylePanelEl.addEventListener("change", () => {
    onlinePrefs.foodStyle = normalizeStyle({ foodStyle: onlineFoodStylePanelEl.value }).foodStyle;
    onlineFoodStyleEl.value = onlinePrefs.foodStyle;
    saveSettings();
  });
  onlineFoodColorEl.addEventListener("change", () => {
    onlinePrefs.foodColor = normalizeStyle({ foodColor: onlineFoodColorEl.value }).foodColor;
    onlineFoodColorPanelEl.value = onlinePrefs.foodColor;
    saveSettings();
  });
  onlineFoodColorPanelEl.addEventListener("change", () => {
    onlinePrefs.foodColor = normalizeStyle({ foodColor: onlineFoodColorPanelEl.value }).foodColor;
    onlineFoodColorEl.value = onlinePrefs.foodColor;
    saveSettings();
  });
  onlineGridColsEl.addEventListener("change", () => syncOnlineGridSettings("modal"));
  onlineGridRowsEl.addEventListener("change", () => syncOnlineGridSettings("modal"));
  onlineGridColsPanelEl.addEventListener("change", () => syncOnlineGridSettings("panel"));
  onlineGridRowsPanelEl.addEventListener("change", () => syncOnlineGridSettings("panel"));
  miniMapPositionEl.addEventListener("change", () => {
    onlinePrefs.miniPosition = normalizeMiniPosition(miniMapPositionEl.value);
    miniMapPositionPanelEl.value = onlinePrefs.miniPosition;
    applyMiniPositionClass();
    saveSettings();
  });
  miniMapPositionPanelEl.addEventListener("change", () => {
    onlinePrefs.miniPosition = normalizeMiniPosition(miniMapPositionPanelEl.value);
    miniMapPositionEl.value = onlinePrefs.miniPosition;
    applyMiniPositionClass();
    saveSettings();
  });

  applyOnlineConfigBtn.addEventListener("click", applyOnlineConfigToRoom);
  applyOnlineStyleBtn.addEventListener("click", applyOnlineStyleToRoom);
  applyOnlineConfigPanelBtn.addEventListener("click", applyOnlineConfigToRoom);
  applyOnlineStylePanelBtn.addEventListener("click", applyOnlineStyleToRoom);
}

function setupSingleActions() {
  singleStartBtn.addEventListener("click", startOrResumeSingle);
  singlePauseBtn.addEventListener("click", pauseSingle);
  singleRestartBtn.addEventListener("click", restartSingle);
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
      if (!key || !DIRECTION_MAP[key]) return;
      queueSingleDirection(DIRECTION_MAP[key]);
    });
  });

  singleCanvas.addEventListener("click", (event) => {
    if (!singleState.snake.length) return;
    const rect = singleCanvas.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * singleState.gridCols;
    const y = ((event.clientY - rect.top) / rect.height) * singleState.gridRows;
    const [hx, hy] = singleState.snake[0];
    const dx = x - (hx + 0.5);
    const dy = y - (hy + 0.5);
    const dir = Math.abs(dx) >= Math.abs(dy) ? (dx >= 0 ? [1, 0] : [-1, 0]) : dy >= 0 ? [0, 1] : [0, -1];
    queueSingleDirection(dir);
  });
}

function setupOnlineActions() {
  onlineModeQuickEl.addEventListener("change", () => {
    onlinePrefs.mode = normalizeMode(onlineModeQuickEl.value);
    onlineModeSettingEl.value = onlinePrefs.mode;
    onlineModePanelEl.value = onlinePrefs.mode;
    updateOnlineStaticTexts();
    saveSettings();
  });
  onlineDifficultyQuickEl.addEventListener("change", () => {
    onlinePrefs.difficulty = ["easy", "mixed", "hard"].includes(onlineDifficultyQuickEl.value)
      ? onlineDifficultyQuickEl.value
      : "mixed";
    onlineDifficultySettingEl.value = onlinePrefs.difficulty;
    onlineDifficultyPanelEl.value = onlinePrefs.difficulty;
    saveSettings();
  });
  createRoomBtn.addEventListener("click", handleCreateRoom);
  joinRoomBtn.addEventListener("click", handleJoinRoom);
  startMatchBtn.addEventListener("click", handleStartMatch);
  copyInviteBtn.addEventListener("click", copyInviteLink);
  roomCodeInput.addEventListener("input", () => {
    roomCodeInput.value = normalizeRoomCode(roomCodeInput.value);
  });

  document.querySelectorAll("[data-online-dir]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const key = btn.dataset.onlineDir;
      if (!key || !DIRECTION_MAP[key]) return;
      sendOnlineDirection(key);
    });
  });
}

function handleKeyDown(event) {
  const dirKeys = {
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
  const onlineDirKeys = {
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

  if (event.key === "Escape") {
    settingsModal.classList.add("hidden");
  }

  const activeTag = document.activeElement?.tagName;
  if (activeTag === "INPUT" || activeTag === "TEXTAREA" || activeTag === "SELECT") {
    return;
  }

  if (uiState.tab === "single") {
    if (dirKeys[event.key]) {
      event.preventDefault();
      queueSingleDirection(dirKeys[event.key]);
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

  if (uiState.tab === "online" && onlineDirKeys[event.key]) {
    event.preventDefault();
    sendOnlineDirection(onlineDirKeys[event.key]);
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

function initSingleState() {
  resetSingleSnake();
  singleState.runningState = "ready";
  updateSingleStats();
}

function initOnlineState() {
  loadOnlineSession();
  if (onlineState.roomCode && onlineState.token) {
    currentRoomCodeEl.textContent = onlineState.roomCode;
    roomCodeInput.value = onlineState.roomCode;
    setOnlineStatusKey("status_reconnect");
    startOnlinePolling();
  } else {
    setOnlineStatusKey("status_idle");
  }
  updateOnlineStaticTexts();
  showOnlineBoards(onlineState.mode);
}

function bootstrap() {
  loadSettings();
  updateControlsFromState();
  applyLanguageToDom();

  setupTabButtons();
  setupSettingsActions();
  setupSingleActions();
  setupOnlineActions();

  initSingleState();
  initOnlineState();
  applyQueryPrefill();

  document.addEventListener("keydown", handleKeyDown);
  window.addEventListener("resize", resizeAllCanvases);
  window.addEventListener("orientationchange", resizeAllCanvases);
  resizeAllCanvases();
  requestAnimationFrame(singleLoop);
}

bootstrap();
