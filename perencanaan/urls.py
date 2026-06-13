from django.urls import path
from . import views

app_name = "perencanaan"

urlpatterns = [
    path("", views.perencanaan_list, name="list"),
    path("create/", views.perencanaan_create, name="create"),
    path("<int:pk>/update/", views.perencanaan_update, name="update"),
    path("<int:pk>/delete/", views.perencanaan_delete, name="delete"),
]
