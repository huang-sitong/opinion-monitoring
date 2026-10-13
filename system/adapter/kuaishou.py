# -*- coding: utf-8 -*-
"""快手（kuaishou）适配器。

时间特点：``create_time`` 是**毫秒**时间戳（parse_time 自动识别）。
源数据里 ``viewd_count`` 是拼写错误，这里归一为 ``view_count``。
"""
from __future__ import annotations

from typing import Any, Mapping

from .base import (
    BaseAdapter,
    UnifiedComment,
    UnifiedNote,
    as_int,
)


class KuaishouAdapter(BaseAdapter):
    platform = "kuaishou"
    aliases = ("kuaishou", "ks")

    def adapt_content(self, raw: Mapping[str, Any]) -> UnifiedNote:
        return UnifiedNote(
            platform=self.platform,
            note_id=str(raw.get("video_id", "")),
            title=raw.get("title"),
            content=raw.get("desc"),
            url=raw.get("video_url"),
            publish_time=self._time(raw.get("create_time")),
            crawled_at=self._crawled_at(raw),
            creator_id=raw.get("creator_hash"),
            creator_nickname=raw.get("nickname"),
            source_keyword=raw.get("source_keyword"),
            like_count=as_int(raw.get("liked_count")),
            view_count=as_int(raw.get("viewd_count")),  # 源字段拼写错误
            raw=raw,
        )

    def adapt_comment(self, raw: Mapping[str, Any]) -> UnifiedComment:
        return UnifiedComment(
            platform=self.platform,
            comment_id=str(raw.get("comment_id", "")),
            note_id=str(raw.get("video_id", "")) or None,
            content=raw.get("content"),
            publish_time=self._time(raw.get("create_time")),
            crawled_at=self._crawled_at(raw),
            creator_id=raw.get("creator_hash"),
            creator_nickname=raw.get("nickname"),
            sub_comment_count=as_int(raw.get("sub_comment_count")),
            raw=raw,
        )
