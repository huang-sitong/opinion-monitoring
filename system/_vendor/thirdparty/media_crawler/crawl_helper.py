# -*- coding: utf-8 -*-
"""
把 MediaCrawler 封装成一次函数调用的示例（调试验证用）。

依赖作者提供的两个入口：
  1. cmd_arg.parse_cmd(argv)   —— 作者特意把参数解析做成可传列表，就地更新全局 config
  2. main.CrawlerFactory       —— 按平台名创建爬虫实例，await crawler.start() 执行爬取

数据不通过返回值给出，而是按 save_data_option 落盘到 data/<platform>/<format>/。
"""
from __future__ import annotations

import asyncio
from typing import Optional

import cmd_arg
import config
from base.base_crawler import AbstractCrawler
from main import CrawlerFactory


async def crawl(
    platform: str = "xhs",
    crawler_type: str = "search",
    keywords: str = "",
    specified_id: str = "",
    creator_id: str = "",
    max_notes_count: int = 20,
    max_comments_count: int = 10,
    save_data_option: str = "jsonl",
    headless: bool = True,
    get_comments: bool = True,
    get_sub_comments: bool = False,
    get_media: bool = False,
    extra_args: Optional[list[str]] = None,
) -> str:
    """执行一次爬取，返回数据保存目录（相对项目根目录）。"""
    argv = [
        "--platform", platform,
        "--type", crawler_type,
        "--keywords", keywords,
        "--specified_id", specified_id,
        "--creator_id", creator_id,
        "--crawler_max_notes_count", str(max_notes_count),
        "--max_comments_count_singlenotes", str(max_comments_count),
        "--save_data_option", save_data_option,
        "--headless", "true" if headless else "false",
        "--get_comment", "true" if get_comments else "false",
        "--get_sub_comment", "true" if get_sub_comments else "false",
        "--get_media", "true" if get_media else "false",
    ]
    if extra_args:
        argv += extra_args

    # 解析参数并覆盖全局 config（作者提供的函数入口）
    await cmd_arg.parse_cmd(argv)

    crawler: AbstractCrawler = CrawlerFactory.create_crawler(config.PLATFORM)
    try:
        await crawler.start()
    finally:
        # start() 不负责关浏览器，需要自己清理（对应 main.py 的 async_cleanup）
        try:
            await crawler.close()
        except Exception:
            pass
        if config.SAVE_DATA_OPTION == "excel":
            from store.excel_store_base import ExcelStoreBase
            ExcelStoreBase.flush_all()

    return config.SAVE_DATA_PATH or "data"


if __name__ == "__main__":
    import time

    t0 = time.time()
    data_dir = asyncio.run(
        crawl(
            platform="xhs",
            crawler_type="search",
            keywords="函数封装测试",
            max_notes_count=20,
            save_data_option="jsonl",
            headless=True,
        )
    )
    print(f"[crawl_helper] done in {time.time() - t0:.1f}s, data dir: {data_dir}")
