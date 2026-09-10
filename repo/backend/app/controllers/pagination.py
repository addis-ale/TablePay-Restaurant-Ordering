from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any, TypeVar

from app.services.errors import AppError


T = TypeVar("T")


def parse_pagination_args(
    args: Mapping[str, Any],
    default_page_size: int = 20,
    max_page_size: int = 100,
) -> dict[str, int | bool]:
    raw_page = args.get("page")
    raw_page_size = args.get("page_size")

    if raw_page is None and raw_page_size is None:
        return {"requested": False, "page": 1, "page_size": default_page_size}

    try:
        page = int(raw_page or "1")
        page_size = int(raw_page_size or str(default_page_size))
    except (TypeError, ValueError) as exc:
        raise AppError("validation_error", "page and page_size must be integers.", 400) from exc

    if page < 1 or page_size < 1:
        raise AppError("validation_error", "page and page_size must be positive integers.", 400)

    return {"requested": True, "page": page, "page_size": min(page_size, max_page_size)}


def paginate_collection(items: Sequence[T], pagination: dict[str, int | bool]) -> tuple[list[T], dict[str, int | bool]]:
    total_items = len(items)
    requested = bool(pagination["requested"])

    if not requested:
        page = 1
        page_size = max(total_items, 1)
        page_items = list(items)
    else:
        page = int(pagination["page"])
        page_size = int(pagination["page_size"])
        start = (page - 1) * page_size
        end = start + page_size
        page_items = list(items[start:end])

    if total_items == 0:
        total_pages = 1
    else:
        total_pages = max(1, math.ceil(total_items / page_size))

    return page_items, {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
