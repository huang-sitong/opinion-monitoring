# -*- coding: utf-8 -*-
"""
平台数据适配层。

把 MediaCrawler 为各平台产出的**异构**原始记录，归一为统一的
:class:`~system.adapter.base.UnifiedNote` / :class:`~system.adapter.base.UnifiedComment`，
抹平两类差异：

1. **时间格式**：秒/毫秒时间戳、带时区字符串、裸北京时间字符串
   （贴吧）→ 统一为带时区的 UTC datetime；
2. **字段命名**：``note_id``/``video_id``/``aweme_id``/``content_id``、
   ``create_time``/``publish_time``/``time`` 等 → 统一命名。

用法::

    from system.adapter import get_adapter, read_records

    adapter = get_adapter("tieba")           # 也支持 dy/ks/wb 等别名
    note = adapter.adapt_content(raw_dict)   # → UnifiedNote
    for note in adapter.iter_contents(path): # 直接读 json/jsonl 文件
        print(note.platform, note.publish_time)
"""
from __future__ import annotations

from .base import (
    TZ_CHINA,
    TZ_UTC,
    BaseAdapter,
    UnifiedComment,
    UnifiedNote,
    as_int,
    parse_time,
    read_records,
)
from .registry import available_platforms, get_adapter

__all__ = [
    # 模型与基类
    "BaseAdapter",
    "UnifiedNote",
    "UnifiedComment",
    "parse_time",
    "as_int",
    "read_records",
    "TZ_CHINA",
    "TZ_UTC",
    # 注册表
    "get_adapter",
    "available_platforms",
]
