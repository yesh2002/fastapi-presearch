# FastAPI Presearch Doppelgange Proxy (Text + Image)

> 用于把网页搜索流程封装成你自己的 API：文本搜索 + 图片搜索（上传/URL）。

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
  -d '{"image_url":"https://example.com/image.jpg","mode":"spicy"}'
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

## 6. 抓包映射建议

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


## 7. 测试（已覆盖基础用例）

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

