from django.urls import include, path

urlpatterns = [
    path("tasks/", include("api.v1.tasks.urls")),
    path("categories/", include("api.v1.categories.urls")),
]
