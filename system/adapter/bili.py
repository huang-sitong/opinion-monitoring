# -*- coding: utf-8 -*-
"""B 站（bili）适配器。

时间特点：``create_time`` 秒时间戳。内容主键是 ``video_id``。
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


class BiliAdapter(BaseAdapter):
    platform = "bili"
    aliases = ("bili", "bilibili")

    def adapt_content(self, raw: Mapping[str, Any]) -> UnifiedNote:
        extra = {
            k: v
            for k, v in {
                "dislike_count": as_int(raw.get("disliked_count")),
                "coin_count": as_int(raw.get("video_coin_count")),
                "danmaku_count": as_int(raw.get("video_danmaku")),
            }.items()
            if v is not None
        }
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
            comment_count=as_int(raw.get("video_comment")),
            share_count=as_int(raw.get("video_share_count")),
            view_count=as_int(raw.get("video_play_count")),
            collect_count=as_int(raw.get("video_favorite_count")),
            extra_metrics=extra,
            raw=raw,
        )

    def adapt_comment(self, raw: Mapping[str, Any]) -> UnifiedComment:
        return UnifiedComment(
            platform=self.platform,
            comment_id=str(raw.get("comment_id", "")),
            note_id=str(raw.get("video_id", "")) or None,
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
