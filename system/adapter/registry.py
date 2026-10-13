# -*- coding: utf-8 -*-
"""平台适配器注册表。

把规范平台名及别名（含爬虫 API 短码，如 ``dy``/``ks``/``wb``）映射到
对应的适配器实例，供上层按平台名取用。
"""
from __future__ import annotations

from .base import BaseAdapter
from .bili import BiliAdapter
from .douyin import DouyinAdapter
from .kuaishou import KuaishouAdapter
from .tieba import TiebaAdapter
from .weibo import WeiboAdapter
from .xhs import XhsAdapter
from .zhihu import ZhihuAdapter

# 注册顺序即遍历顺序，规范名唯一
_ADAPTER_CLASSES: tuple[type[BaseAdapter], ...] = (
    TiebaAdapter,
    WeiboAdapter,
    BiliAdapter,
    DouyinAdapter,
    KuaishouAdapter,
    XhsAdapter,
    ZhihuAdapter,
)

# name(小写) -> 适配器实例
_REGISTRY: dict[str, BaseAdapter] = {}
for _cls in _ADAPTER_CLASSES:
    _inst = _cls()
    _REGISTRY[_inst.platform] = _inst
    for _alias in _inst.aliases:
        _REGISTRY.setdefault(_alias, _inst)


def get_adapter(platform: str) -> BaseAdapter:
    """按平台名/别名取适配器；未注册则抛 KeyError。"""
    key = platform.strip().lower()
    try:
        return _REGISTRY[key]
    except KeyError:
        raise KeyError(
            f"unknown platform {platform!r}; known: {sorted({a.platform for a in _ADAPTER_CLASSES})}"
        ) from None


def available_platforms() -> list[str]:
    """所有规范平台名。"""
    return [cls.platform for cls in _ADAPTER_CLASSES]


__all__ = [
    "BiliAdapter",
    "DouyinAdapter",
    "KuaishouAdapter",
    "TiebaAdapter",
    "WeiboAdapter",
    "XhsAdapter",
    "ZhihuAdapter",
    "get_adapter",
    "available_platforms",
]
