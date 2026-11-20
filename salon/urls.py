from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("book/", views.book, name="book"),
    path("pay/<int:pk>/", views.pay, name="pay"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]
