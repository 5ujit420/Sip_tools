from django.urls import path
from . import views

urlpatterns = [
    path("", views.portScanner, name="portScanner"),
    path("attacks/<str:attack_id>/", views.attack_form, name="attack_form"),
    path("attacks/", views.attacks, name="attacks"),
    path("nmap/", views.nmap, name="nmap"),
    path("logs/", views.read_log_file, name="read_log_file")
]