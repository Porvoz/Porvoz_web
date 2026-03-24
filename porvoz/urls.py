from django.urls import path, include

urlpatterns = [
    path("", include("core.urls")),
    path("api/", include("contacts.urls")),
    path("api/", include("reminders.urls")),
    path("api/", include("calls.urls")),
]
