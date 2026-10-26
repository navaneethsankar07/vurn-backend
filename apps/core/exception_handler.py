import logging

from rest_framework.views import exception_handler

logger = logging.getLogger("apps")


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    request = context.get("request")
    view = context.get("view")

    if response is not None:
        logger.warning(
            "API error | method=%s path=%s view=%s " "status=%s error=%s",
            request.method if request else None,
            request.path if request else None,
            view.__class__.__name__ if view else None,
            response.status_code,
            str(exc),
        )

        return response

    logger.error(
        "Unhandled API exception | method=%s path=%s view=%s",
        request.method if request else None,
        request.path if request else None,
        view.__class__.__name__ if view else None,
        exc_info=exc,
    )

    return None
