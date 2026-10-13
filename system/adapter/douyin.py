# -*- coding: utf-8 -*-
"""抖音（douyin）适配器。

时间特点：``create_time`` 秒时间戳。内容主键是 ``aweme_id``。
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


class DouyinAdapter(BaseAdapter):
    platform = "douyin"
    aliases = ("douyin", "dy")

    def adapt_content(self, raw: Mapping[str, Any]) -> UnifiedNote:
        return UnifiedNote(
            platform=self.platform,
            note_id=str(raw.get("aweme_id", "")),
            title=raw.get("title"),
            content=raw.get("desc"),
            url=raw.get("aweme_url"),
            publish_time=self._time(raw.get("create_time")),
            crawled_at=self._crawled_at(raw),
            creator_id=raw.get("creator_hash"),
            creator_nickname=raw.get("nickname"),
            source_keyword=raw.get("source_keyword"),
            like_count=as_int(raw.get("liked_count")),
            comment_count=as_int(raw.get("comment_count")),
            share_count=as_int(raw.get("share_count")),
            collect_count=as_int(raw.get("collected_count")),
            raw=raw,
        )

    def adapt_comment(self, raw: Mapping[str, Any]) -> UnifiedComment:
        return UnifiedComment(
            platform=self.platform,
            comment_id=str(raw.get("comment_id", "")),
            note_id=str(raw.get("aweme_id", "")) or None,
            parent_comment_id=_clean_parent(raw.get("parent_comment_id")),
            content=raw.get("content"),
            publish_time=self._time(raw.get("create_time")),
            crawled_at=self._crawled_at(raw),
            creator_id=raw.get("creator_hash"),
            creator_nickname=raw.get("nickname"),
            like_count=as_int(raw.get("like_count")),
            sub_comment_count=as_int(raw.get("sub_comment_count")),
            raw=raw,
        )
