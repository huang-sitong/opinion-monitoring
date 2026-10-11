# Vendored: MediaCrawler

本目录是第三方项目 **MediaCrawler** 的 vendored 拷贝，以**独立 HTTP 服务**形式集成，
由本仓库通过接口调用，不作为 Python 包安装。

## 基本声明

| 项 | 值 |
|---|---|
| 上游仓库 | <https://github.com/NanmiCoder/MediaCrawler> |
| 上游版本 | commit `156c602c8d689266e6c5e9130b36f0b70495f5f0`（2026-10-10，"update readme"） |
| 许可证 | NON-COMMERCIAL LEARNING LICENSE 1.1，见 [LICENSE](./LICENSE) |
| 许可限制 | **仅供学习研究，禁止商业用途**；使用即表示接受上游免责声明与许可条款 |
| 集成方式 | FastAPI 服务（默认 `127.0.0.1:8080`），客户端封装见 `system/message_source/crawler_client.py` |
| 依赖环境 | **已并入仓库根 `pyproject.toml` / `uv.lock`，与主项目共享根目录 `.venv`** |

## 运行方式

```bash
# 在本目录执行；本目录已无 pyproject.toml，uv 会向上找到仓库根项目并使用共享环境
cd system/_vendor/thirdparty/media_crawler
uv run python -m uvicorn api.main:app --host 127.0.0.1 --port 8080
```

WebUI 前端构建产物在 `api/webui/`，服务根路径 `/` 直接提供页面。

## 本地改动（相对上游 commit `156c602c`）

1. `api/main.py` — `/api/env/check` 超时后杀掉子进程，避免孤儿 `uv run` 进程累积并占用 uv 锁
2. `api/services/crawler_manager.py` — 爬虫子进程输出解码加 `errors="replace"`，
   防止非法 UTF-8 打崩日志读取线程导致管道堵塞、爬虫卡死在 running 状态
3. `api/routers/data.py` — 数据接口支持 `.jsonl`（上游默认存储格式）的文件列表、预览与统计
4. 新增 `crawl_helper.py` — 进程内函数调用的封装示例（需以本目录为解释器工作目录）
5. 依赖声明整体移除（见下），改由仓库根统一管理

## 相对上游删除的内容

- 仓库元数据：`.git` `.github` `.gitattributes` `.pre-commit-config.yaml`
- 环境与构建：`.venv` `.python-version` `pyproject.toml` `uv.lock` `requirements.txt` `mypy.ini`
- 开发设施：`tests/` `test/` `.pytest_cache` `__pycache__`
- 文档站：`package.json` `package-lock.json`（vitepress）、`README_en.md`、`README_es.md`、
  `docs/` 下除 `STZHONGS.TTF`、`hit_stopwords.txt` 外的全部文档与图片
  （这两个文件被 `config.FONT_PATH` / `config.STOP_WORDS_FILE` 运行时引用，必须保留）
- 运行时输出：`data/`（运行后自动重建）

**保留**：`LICENSE`、`README.md`、`.env.example`（环境变量模板）、`.gitignore`
（上游忽略规则，可避免 `data/`、浏览器登录态等运行时文件被提交）、全部源码与 `api/webui/` 前端产物。

## 升级方式

1. 从上游克隆目标版本，用其源码覆盖本目录（勿覆盖 `VENDORED.md`）
2. 重新应用上述"本地改动"（均为小补丁，或已合入上游则跳过）
3. 若上游依赖有变，同步更新仓库根 `pyproject.toml` 并 `uv sync`
