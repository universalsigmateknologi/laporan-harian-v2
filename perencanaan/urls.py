from django.urls import path
from . import views

app_name = "perencanaan"

urlpatterns = [
    # Perencanaan
    path("", views.perencanaan_list, name="list"),
    path("create/", views.perencanaan_create, name="create"),
    path("<int:pk>/update/", views.perencanaan_update, name="update"),
    path("<int:pk>/delete/", views.perencanaan_delete, name="delete"),

    # Kategori Perencanaan
    path("kategori/", views.kategori_list, name="kategori_list"),
    path("kategori/create/", views.kategori_create, name="kategori_create"),
    path("kategori/<int:pk>/update/", views.kategori_update, name="kategori_update"),
    path("kategori/<int:pk>/delete/", views.kategori_delete, name="kategori_delete"),

    # Program
    path("program/", views.program_list, name="program_list"),
    path("program/create/", views.program_create, name="program_create"),
    path("program/<int:pk>/update/", views.program_update, name="program_update"),
    path("program/<int:pk>/delete/", views.program_delete, name="program_delete"),
]


