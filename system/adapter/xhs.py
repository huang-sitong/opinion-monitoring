# -*- coding: utf-8 -*-
"""小红书（xhs）适配器。

时间特点：发布用 ``time``（**毫秒**时间戳），编辑用 ``last_update_time``。
小红书数据文件是 jsonl（其余平台是 json 数组），读取由 base.read_records 统一处理。
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


class XhsAdapter(BaseAdapter):
    platform = "xhs"
    aliases = ("xhs", "xiaohongshu", "rednote")

    def adapt_content(self, raw: Mapping[str, Any]) -> UnifiedNote:
        tags = raw.get("tag_list") or []
        return UnifiedNote(
            platform=self.platform,
            note_id=str(raw.get("note_id", "")),
            title=raw.get("title"),
            content=raw.get("desc"),
            url=raw.get("note_url"),
            publish_time=self._time(raw.get("time")),
            updated_time=self._time(raw.get("last_update_time")),
            crawled_at=self._crawled_at(raw),
            creator_id=raw.get("creator_hash"),
            creator_nickname=raw.get("nickname"),
            source_keyword=raw.get("source_keyword"),
            like_count=as_int(raw.get("liked_count")),
            comment_count=as_int(raw.get("comment_count")),
            share_count=as_int(raw.get("share_count")),
            collect_count=as_int(raw.get("collected_count")),
            extra_metrics={"tag_count": len(tags)},
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
            like_count=as_int(raw.get("like_count")),
            sub_comment_count=as_int(raw.get("sub_comment_count")),
            raw=raw,
        )
