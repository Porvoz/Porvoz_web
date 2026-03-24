from django.urls import path
from . import views

urlpatterns = [
    path("contacts", views.contacts_list),
    path("contacts/<int:pk>", views.contact_detail),
]
