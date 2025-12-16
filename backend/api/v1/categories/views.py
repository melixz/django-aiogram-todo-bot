from categories.models import Category
from rest_framework import status, viewsets
from rest_framework.response import Response

from api.v1.categories.serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_telegram_id(self) -> int | None:
        telegram_id = self.request.headers.get("X-Telegram-ID")
        if telegram_id:
            try:
                return int(telegram_id)
            except ValueError:
                return None
        return None

    def get_queryset(self):
        telegram_id = self.get_telegram_id()
        if telegram_id is None:
            return Category.objects.none()
        return Category.objects.filter(telegram_id=telegram_id)

    def create(self, request, *args, **kwargs):
        telegram_id = self.get_telegram_id()
        if telegram_id is None:
            return Response(
                {"error": "X-Telegram-ID header is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(telegram_id=telegram_id)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
