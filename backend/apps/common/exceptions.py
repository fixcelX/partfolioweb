from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Izchil xato formati: {"detail": ..., "errors": {...}}."""
    response = exception_handler(exc, context)
    if response is None:
        return response

    data = response.data
    if isinstance(data, dict) and "detail" in data and len(data) == 1:
        response.data = {"detail": data["detail"], "errors": {}}
    elif isinstance(data, dict):
        detail = data.get("detail", "Validatsiya xatosi.")
        errors = {k: v for k, v in data.items() if k != "detail"}
        response.data = {"detail": detail, "errors": errors}
    else:
        response.data = {"detail": "Xatolik yuz berdi.", "errors": data}
    return response
