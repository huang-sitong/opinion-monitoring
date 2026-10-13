# -*- coding: utf-8 -*-
"""
适配器基类与统一数据模型。

MediaCrawler 为每个平台产出的原始字段并不统一（时间格式、字段命名、
互动指标口径都有差异），适配器的职责就是把它们归一到 ``UnifiedNote`` /
``UnifiedComment`` 两个模型上，供下游舆情分析使用。

时间归一化约定（重点，详见 :func:`parse_time`）：

- 统一输出 **带时区的 UTC datetime**；
- 秒/毫秒时间戳自动识别（阈值 1e12）；
- 裸时间字符串（如贴吧的 ``2026-07-17 06:48:50``，实际是北京时间）
  按各适配器声明的 ``naive_tz`` 补齐时区后再转 UTC。
"""
from __future__ import annotations

import datetime as dt
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

# 秒/毫秒时间戳自动识别阈值：大于该值视为毫秒
_MS_THRESHOLD = 1e12

# 常用时区
TZ_CHINA = dt.timezone(dt.timedelta(hours=8), name="+08:00")
TZ_UTC = dt.timezone.utc

TimeLike = Union[None, int, float, str]


def parse_time(value: TimeLike, naive_tz: dt.tzinfo = TZ_CHINA) -> Optional[dt.datetime]:
    """把各平台的时间字段统一解析为带时区的 UTC datetime。

    支持的输入：
      - ``None`` → ``None``
      - ``int/float``：秒或毫秒时间戳（自动识别）
      - ``str``：ISO 字符串（``2026-10-01 22:30:00+08:00``）或裸时间
        字符串（``2026-07-17 06:48:50``，按 ``naive_tz`` 解释）

    解析失败返回 ``None``。
    """
    if value is None or value == "":
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        ts = float(value)
        if abs(ts) >= _MS_THRESHOLD:  # 毫秒 → 秒
            ts /= 1000.0
        try:
            return dt.datetime.fromtimestamp(ts, tz=TZ_UTC)
        except (OverflowError, OSError, ValueError):
            return None

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            parsed = dt.datetime.fromisoformat(text)
        except ValueError:
            return None
        if parsed.tzinfo is None:  # 裸时间 → 补齐默认时区
            parsed = parsed.replace(tzinfo=naive_tz)
        return parsed.astimezone(TZ_UTC)

    return None


def as_int(value: Any) -> Optional[int]:
    """尽力把字段转成 int（原始数据里常见字符串数字、None）。"""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if not text:
            return None
        try:
            return int(float(text))
        except ValueError:
            return None
    return None


class _Model(BaseModel):
    # 允许子类用 attribute 访问、并忽略未声明的额外字段
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class UnifiedNote(_Model):
    """归一后的“内容/帖子/视频/回答”。"""

    platform: str
    note_id: str
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None

    publish_time: Optional[dt.datetime] = None  # UTC
    updated_time: Optional[dt.datetime] = None  # 内容被编辑的时间（如有）
    crawled_at: Optional[dt.datetime] = None  # 本次爬取时间（last_modify_ts）

    creator_id: Optional[str] = None  # 平台侧匿名化的作者标识
    creator_nickname: Optional[str] = None
    source_keyword: Optional[str] = None

    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    share_count: Optional[int] = None
    view_count: Optional[int] = None
    collect_count: Optional[int] = None
    extra_metrics: dict[str, int] = Field(default_factory=dict)

    raw: Optional[Mapping[str, Any]] = None  # 原始记录，便于回溯


class UnifiedComment(_Model):
    """归一后的评论/跟帖。"""

    platform: str
    comment_id: str
    note_id: Optional[str] = None
    parent_comment_id: Optional[str] = None  # 空串/None 表示顶级评论
    content: Optional[str] = None

    publish_time: Optional[dt.datetime] = None  # UTC
    crawled_at: Optional[dt.datetime] = None

    creator_id: Optional[str] = None
    creator_nickname: Optional[str] = None

    like_count: Optional[int] = None
    sub_comment_count: Optional[int] = None
    extra_metrics: dict[str, int] = Field(default_factory=dict)

    raw: Optional[Mapping[str, Any]] = None


def _clean_parent(value: Any) -> Optional[str]:
    """把父评论里的空串归一为 None。"""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


class BaseAdapter(ABC):
    """平台适配器基类。

    子类需要声明：

    - ``platform``：规范平台名（与数据目录名一致，如 ``tieba``）；
    - ``naive_tz``：该平台裸时间字符串的时区（默认北京时间）；
    - 实现 :meth:`adapt_content` 与 :meth:`adapt_comment`。
    """

    #: 规范平台名，需与 data/ 下目录名一致
    platform: str
    #: 平台别名（爬虫 API 里的短码等），供注册表匹配
    aliases: tuple[str, ...] = ()
    #: 裸时间字符串的时区，默认北京时间
    naive_tz: dt.tzinfo = TZ_CHINA

    # ---------- 子类实现 ----------

    @abstractmethod
    def adapt_content(self, raw: Mapping[str, Any]) -> UnifiedNote:
        """把一条原始内容记录适配为 UnifiedNote。"""

    @abstractmethod
    def adapt_comment(self, raw: Mapping[str, Any]) -> UnifiedComment:
        """把一条原始评论记录适配为 UnifiedComment。"""

    # ---------- 通用工具 ----------

    def _time(self, value: TimeLike) -> Optional[dt.datetime]:
        return parse_time(value, naive_tz=self.naive_tz)

    def _crawled_at(self, raw: Mapping[str, Any]) -> Optional[dt.datetime]:
        return parse_time(raw.get("last_modify_ts"), naive_tz=self.naive_tz)

    # ---------- 文件级便捷方法 ----------

    def iter_contents(self, path: Union[str, Path]) -> Iterator[UnifiedNote]:
        for raw in read_records(path):
            yield self.adapt_content(raw)

    def iter_comments(self, path: Union[str, Path]) -> Iterator[UnifiedComment]:
        for raw in read_records(path):
            yield self.adapt_comment(raw)


def read_records(path: Union[str, Path]) -> list[Mapping[str, Any]]:
    """读取一个数据文件（json 数组 或 jsonl），返回原始记录列表。

    xhs 产出 jsonl，其余平台产出 json 数组，这里统一处理。
    """
    import json

    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    data = json.loads(text)
    if isinstance(data, list):
        return data
    raise ValueError(f"unsupported data file structure in {p}")


def collect(items: Iterable[Union[UnifiedNote, UnifiedComment]]) -> list:
    return list(items)
