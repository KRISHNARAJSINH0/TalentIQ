"""Parser views – Phase 2."""

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def parser_root(request):
    """Parser API root."""
    return Response({"message": "Parser API – Coming Soon"})
