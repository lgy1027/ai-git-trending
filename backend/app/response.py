"""Helpers for consistent API responses."""

from enum import Enum

from flask import jsonify


class ErrorCode(Enum):
    SUCCESS = 0
    BAD_REQUEST = 400
    VALIDATION_ERROR = 400
    NOT_FOUND = 404
    INVALID_FORMAT = 400
    TOO_MANY_REQUESTS = 429
    INTERNAL_ERROR = 500


def _normalize_code(code: ErrorCode | int) -> int:
    return code.value if isinstance(code, ErrorCode) else code


def success_response(data=None, message: str = "success", code: ErrorCode | int = ErrorCode.SUCCESS):
    return jsonify(
        {
            "code": _normalize_code(code),
            "message": message,
            "data": data,
        }
    )


def error_response(
    code: ErrorCode | int = ErrorCode.BAD_REQUEST,
    message: str = "error",
    status_code: int = 400,
    data=None,
):
    payload = {
        "code": _normalize_code(code),
        "message": message,
    }
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def paginate_response(items, total: int, page: int, page_size: int):
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def get_pagination_params(request):
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
    except (TypeError, ValueError):
        page = 1
        page_size = 20

    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    return page, page_size
