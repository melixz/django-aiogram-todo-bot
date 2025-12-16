from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from tasks.models import Task

from api.v1.tasks.serializers import TaskCreateSerializer, TaskListSerializer, TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
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
            return Task.objects.none()

        queryset = Task.objects.filter(telegram_id=telegram_id).select_related("category")

        is_completed = self.request.query_params.get("is_completed")
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == "true")

        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TaskListSerializer
        if self.action == "create":
            return TaskCreateSerializer
        return TaskSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["telegram_id"] = self.get_telegram_id()
        return context

    def create(self, request, *args, **kwargs):
        telegram_id = self.get_telegram_id()
        if telegram_id is None:
            return Response(
                {"error": "X-Telegram-ID header is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(telegram_id=telegram_id)

        response_serializer = TaskSerializer(task)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.is_completed = True
        task.save(update_fields=["is_completed", "updated_at"])
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def uncomplete(self, request, pk=None):
        task = self.get_object()
        task.is_completed = False
        task.save(update_fields=["is_completed", "updated_at"])
        serializer = TaskSerializer(task)
        return Response(serializer.data)
