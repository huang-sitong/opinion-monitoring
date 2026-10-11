# -*- coding: utf-8 -*-
"""
MediaCrawler 接口客户端（HTTP 形态）。

爬虫以独立服务形式部署在 system/_vendor/thirdparty/media_crawler，
opinion-monitoring 只通过它的 FastAPI 接口交互：

    启动服务（一次性）:
        cd system/_vendor/thirdparty/media_crawler && uv run python -m uvicorn api.main:app --port 8080

    使用:
        from system.message_source.crawler_client import CrawlerClient

        client = CrawlerClient()
        records = client.crawl(platform="xhs", keywords="舆情关键词")
"""
from __future__ import annotations

import time
from typing import Any, Optional

import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:8080"


class CrawlerError(RuntimeError):
    """爬虫服务返回错误（进程启动失败、任务重复启动等）。"""


class CrawlerClient:
    """MediaCrawler HTTP API 客户端（同步）。"""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ---------- 基础状态 ----------

    def _get(self, path: str, **kwargs) -> Any:
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            resp = client.get(path, **kwargs)
            resp.raise_for_status()
            return resp.json()

    def health(self) -> dict:
        """服务是否存活。连接失败会抛 httpx.ConnectError。"""
        return self._get("/api/health")

    def env_check(self) -> dict:
        """环境自检（uv 项目、依赖、CLI 是否可用）。"""
        return self._get("/api/env/check")

    def status(self) -> dict:
        """当前爬虫任务状态：idle | running | stopping | error。"""
        return self._get("/api/crawler/status")

    def logs(self, limit: int = 100) -> list[dict]:
        return self._get("/api/crawler/logs", params={"limit": limit})["logs"]

    # ---------- 任务控制 ----------

    def start(
        self,
        platform: str = "xhs",
        keywords: str = "",
        crawler_type: str = "search",
        save_option: str = "jsonl",
        specified_ids: str = "",
        creator_ids: str = "",
        headless: bool = True,
        enable_comments: bool = True,
        enable_sub_comments: bool = False,
        enable_media: bool = False,
        max_notes_count: Optional[int] = None,
        max_comments_count: Optional[int] = None,
    ) -> dict:
        """启动一次爬取任务（非阻塞）。platform: xhs|dy|ks|bili|wb|tieba|zhihu"""
        payload: dict[str, Any] = {
            "platform": platform,
            "login_type": "qrcode",
            "crawler_type": crawler_type,
            "keywords": keywords,
            "specified_ids": specified_ids,
            "creator_ids": creator_ids,
            "save_option": save_option,
            "headless": headless,
            "enable_comments": enable_comments,
            "enable_sub_comments": enable_sub_comments,
            "enable_media": enable_media,
        }
        if max_notes_count is not None:
            payload["max_notes_count"] = max_notes_count
        if max_comments_count is not None:
            payload["max_comments_count"] = max_comments_count

        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            resp = client.post("/api/crawler/start", json=payload)
            if resp.status_code >= 400:
                detail = resp.json().get("detail", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
                raise CrawlerError(f"start failed ({resp.status_code}): {detail}")
            return resp.json()

    def stop(self) -> dict:
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            resp = client.post("/api/crawler/stop")
            if resp.status_code >= 400:
                detail = resp.json().get("detail", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
                raise CrawlerError(f"stop failed ({resp.status_code}): {detail}")
            return resp.json()

    def wait(self, timeout: float = 1800.0, poll_interval: float = 2.0) -> dict:
        """轮询直到任务结束（idle），返回最终状态；超时抛 TimeoutError。"""
        deadline = time.monotonic() + timeout
        while True:
            st = self.status()
            if st.get("status") == "idle":
                if st.get("started_at") is None:
                    raise CrawlerError("no crawl task has been started")
                return st
            if st.get("status") == "error":
                raise CrawlerError(f"crawler error: {st.get('error_message')}")
            if time.monotonic() > deadline:
                raise TimeoutError(f"crawler still {st.get('status')} after {timeout}s")
            time.sleep(poll_interval)

    # ---------- 数据读取 ----------

    def list_files(self, platform: Optional[str] = None) -> list[dict]:
        params = {"platform": platform} if platform else {}
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            resp = client.get("/api/data/files", params=params)
            resp.raise_for_status()
            return resp.json()["files"]

    def read_records(self, file_path: str, limit: Optional[int] = None) -> list[dict]:
        """读取某个数据文件的记录（支持 json/jsonl/csv/xlsx）。"""
        params: dict[str, Any] = {"preview": "true"}
        if limit is not None:
            params["limit"] = limit
        data = self._get(f"/api/data/files/{file_path}", params=params)
        return data["data"]

    def latest_content_file(self, platform: str) -> Optional[dict]:
        """最新的笔记/内容数据文件（文件名含 contents）。"""
        files = [f for f in self.list_files(platform) if "contents" in f["name"]]
        return files[0] if files else None  # 已按修改时间倒序

    def crawl(
        self,
        platform: str = "xhs",
        keywords: str = "",
        timeout: float = 1800.0,
        **start_kwargs: Any,
    ) -> list[dict]:
        """一步到位：启动 → 等待完成 → 返回本次产出的内容记录。

        注意：返回的是该平台数据文件里的**全部**记录（含历史运行），
        需要严格"仅本次"时请先记录 start 前的文件行数再做差。
        """
        self.start(platform=platform, keywords=keywords, **start_kwargs)
        self.wait(timeout=timeout)
        latest = self.latest_content_file(platform)
        if latest is None:
            return []
        return self.read_records(latest["path"])
