"""Common views – Shared utility endpoints."""

# pyrefly: ignore [missing-import]
from rest_framework.decorators import api_view
# pyrefly: ignore [missing-import]
from rest_framework.response import Response


@api_view(["GET"])
def common_root(request):
    """Common API root."""
    return Response({"message": "Common API – Utilities"})
