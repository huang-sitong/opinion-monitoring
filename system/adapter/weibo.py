# -*- coding: utf-8 -*-
"""微博（weibo）适配器。

时间特点：``create_time`` 是秒时间戳；另有 ``create_date_time``
（``2026-10-01 22:30:00+08:00``）带时区字符串，parse_time 会自动识别。
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


class WeiboAdapter(BaseAdapter):
    platform = "weibo"
    aliases = ("weibo", "wb")

    def adapt_content(self, raw: Mapping[str, Any]) -> UnifiedNote:
        return UnifiedNote(
            platform=self.platform,
            note_id=str(raw.get("note_id", "")),
            title=None,  # 微博正文即 title 缺失
            content=raw.get("content"),
            url=raw.get("note_url"),
            publish_time=self._time(raw.get("create_time")),
            crawled_at=self._crawled_at(raw),
            creator_id=raw.get("creator_hash"),
            creator_nickname=raw.get("nickname"),
            source_keyword=raw.get("source_keyword"),
            like_count=as_int(raw.get("liked_count")),
            comment_count=as_int(raw.get("comments_count")),
            share_count=as_int(raw.get("shared_count")),
            raw=raw,
        )

    def adapt_comment(self, raw: Mapping[str, Any]) -> UnifiedComment:
        return UnifiedComment(
            platform=self.platform,
            comment_id=str(raw.get("comment_id", "")),
            note_id=str(raw.get("note_id", "")) or None,
            parent_comment_id=_clean_parent(raw.get("parent_comment_id")),
            content=raw.get("content"),
            publish_time=self._time(raw.get("create_time")),
            crawled_at=self._crawled_at(raw),
            creator_id=raw.get("creator_hash"),
            creator_nickname=raw.get("nickname"),
            like_count=as_int(raw.get("comment_like_count")),
            sub_comment_count=as_int(raw.get("sub_comment_count")),
            raw=raw,
        )
