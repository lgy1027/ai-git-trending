"""
Response helper functions for API responses.
"""
from flask import jsonify
from enum import Enum


class ErrorCode(Enum):
    """Error codes for API responses."""
    SUCCESS = 0
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


def success_response(data=None, message='success', code=ErrorCode.SUCCESS):
    """Return a success response."""
    response = {
        'code': code.value if isinstance(code, ErrorCode) else code,
        'message': message,
        'data': data
    }
    return jsonify(response)


def error_response(code=ErrorCode.BAD_REQUEST, message='error', status_code=400):
    """Return an error response."""
    response = {
        'code': code.value if isinstance(code, ErrorCode) else code,
        'message': message
    }
    return jsonify(response), status_code


def get_pagination_params(request):
    """Extract pagination parameters from request."""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
    except (ValueError, TypeError):
        page = 1
        page_size = 20

    # Limit page_size to prevent abuse
    page_size = min(max(page_size, 1), 100)

    return page, page_size
