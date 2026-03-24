from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard),
    path("contacts/", views.contacts_page),
    path("reminders/", views.reminders_page),
    path("calls/", views.calls_page),
]
