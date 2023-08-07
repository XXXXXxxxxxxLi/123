from django.urls import path
from . import views

app_name = "annotation"

urlpatterns = [
    path("upload/", views.upload_image, name="upload_image"),
    path("annotate_image/<int:image_id>/", views.annotate_image, name="annotate_image"),
    path("annotate_images/", views.annotate_images, name="annotate_images"),
]
