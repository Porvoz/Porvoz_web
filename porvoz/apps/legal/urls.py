from django.urls import path

from . import views

urlpatterns = [
    path("legal/", views.legal_info_view, name="legal_info"),
    path("legal/terminos/", views.terms_view, name="terms"),
    path("legal/privacidad/", views.privacy_view, name="privacy"),
    path("contacto/", views.contact_view, name="contact"),
    path("guia/", views.guide_view, name="guide"),
]
