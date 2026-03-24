from django.urls import path
from . import views

urlpatterns = [
    path("reminders", views.reminders_list),
    path("reminders/<int:pk>", views.reminder_detail),
    path("reminders/<int:pk>/call", views.trigger_call),
]
