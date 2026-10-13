# -*- coding: utf-8 -*-
"""贴吧（tieba）适配器。

时间特点：``publish_time`` 是**裸字符串**（``2026-07-17 06:48:50``），
实际为北京时间、不带时区后缀，因此 ``naive_tz`` 按 +08:00 补齐。
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


class TiebaAdapter(BaseAdapter):
    platform = "tieba"
    aliases = ("tieba", "tb")

    def adapt_content(self, raw: Mapping[str, Any]) -> UnifiedNote:
        return UnifiedNote(
            platform=self.platform,
            note_id=str(raw.get("note_id", "")),
            title=raw.get("title"),
            content=raw.get("desc"),
            url=raw.get("note_url"),
            publish_time=self._time(raw.get("publish_time")),
            crawled_at=self._crawled_at(raw),
            creator_id=raw.get("creator_hash"),
            creator_nickname=raw.get("user_nickname"),
            source_keyword=raw.get("source_keyword"),
            comment_count=as_int(raw.get("total_replay_num")),
            extra_metrics={"tieba_reply_page": as_int(raw.get("total_replay_page")) or 0},
            raw=raw,
        )

    def adapt_comment(self, raw: Mapping[str, Any]) -> UnifiedComment:
        return UnifiedComment(
            platform=self.platform,
            comment_id=str(raw.get("comment_id", "")),
            note_id=str(raw.get("note_id", "")) or None,
            parent_comment_id=_clean_parent(raw.get("parent_comment_id")),
            content=raw.get("content"),
            publish_time=self._time(raw.get("publish_time")),
            crawled_at=self._crawled_at(raw),
            creator_id=raw.get("creator_hash"),
            creator_nickname=raw.get("user_nickname"),
            sub_comment_count=as_int(raw.get("sub_comment_count")),
            raw=raw,
        )
