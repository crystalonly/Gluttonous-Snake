# Snake Web（单人 + 双人在线）

## 功能
- 浏览器单人模式（普通 + 无敌复活）。
- 双人在线模式：
  - `separate`：分屏各吃各的。
  - `arena`：同屏抢同一颗豆子。
- 房间号 + 邀请链接。

## 本地运行（开发用）
在项目根目录执行：

```bash
python3 web_snake/server.py
```

浏览器打开：

```text
http://127.0.0.1:8765
```

## 直接用公网网址（推荐）
如果你不想每次本地执行命令，可以部署到云端，部署后直接打开云端链接就能玩。

### 方案 A：Render（最省事）
项目已包含根目录 `render.yaml`。

操作：
1. 把仓库推到 GitHub。
2. 登录 Render，选择 `New +` -> `Blueprint`。
3. 绑定该 GitHub 仓库后直接创建服务。
4. 部署完成后会得到 `https://xxxx.onrender.com`。

以后直接访问这个网址即可，无需本地跑 `python3`.

### 方案 B：Railway
项目已包含根目录 `railway.toml` 和 `Procfile`。

操作：
1. 上传到 GitHub。
2. Railway 中 `New Project` -> `Deploy from GitHub repo`。
3. Railway 会自动识别启动命令并部署。

## 说明
- 服务端会自动读取云平台注入的 `PORT`，本地默认 `8765`。
- 健康检查路径：`/healthz`。
- 房间数据在内存中，服务重启后清空。
