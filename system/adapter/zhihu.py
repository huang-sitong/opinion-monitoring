# -*- coding: utf-8 -*-
"""知乎（zhihu）适配器。

时间特点：内容用 ``created_time`` / ``updated_time``（秒时间戳）；
评论用 ``publish_time``——**注意它也是秒时间戳**（与贴吧同名字段的裸字符串
不同，这正是需要适配层抹平的坑）。parse_time 对两种类型都能处理。
"""
from __future__ import annotations

from typing import Any, Mapping

from .base import (
    BaseAdapter,
    UnifiedComment,
    UnifiedNote,
    _clean_parent,
    as_int,
)


class ZhihuAdapter(BaseAdapter):
    platform = "zhihu"
    aliases = ("zhihu", "zh")

    def adapt_content(self, raw: Mapping[str, Any]) -> UnifiedNote:
        # 正文优先取 content_text，其次 desc
        body = raw.get("content_text") or raw.get("desc")
        return UnifiedNote(
            platform=self.platform,
            note_id=str(raw.get("content_id", "")),
            title=raw.get("title"),
            content=body,
            url=raw.get("content_url"),
            publish_time=self._time(raw.get("created_time")),
            updated_time=self._time(raw.get("updated_time")),
            crawled_at=self._crawled_at(raw),
            creator_id=raw.get("creator_hash"),
            creator_nickname=raw.get("user_nickname"),
            source_keyword=raw.get("source_keyword"),
            like_count=as_int(raw.get("voteup_count")),
            comment_count=as_int(raw.get("comment_count")),
            extra_metrics={"question_id": as_int(raw.get("question_id")) or 0},
            raw=raw,
        )

    def adapt_comment(self, raw: Mapping[str, Any]) -> UnifiedComment:
        extra = {
            k: v
            for k, v in {"dislike_count": as_int(raw.get("dislike_count"))}.items()
            if v is not None
        }
        return UnifiedComment(
            platform=self.platform,
            comment_id=str(raw.get("comment_id", "")),
            note_id=str(raw.get("content_id", "")) or None,
            parent_comment_id=_clean_parent(raw.get("parent_comment_id")),
            content=raw.get("content"),
            publish_time=self._time(raw.get("publish_time")),
            crawled_at=self._crawled_at(raw),
            creator_id=raw.get("creator_hash"),
            creator_nickname=raw.get("user_nickname"),
            like_count=as_int(raw.get("like_count")),
            sub_comment_count=as_int(raw.get("sub_comment_count")),
            extra_metrics=extra,
            raw=raw,
        )
