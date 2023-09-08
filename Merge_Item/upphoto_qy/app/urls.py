from django.urls import path
from . import views
from .upload_pt_photo_views import upload_pt_images, upload_pt_result
from .annotate_tongue_photo import upload_image, annotate_images, annotate_image
from .select_pdf_views import select_chapters

urlpatterns = [
    path("", views.index_view, name="index"),
    path("upload_qy/", views.upload_images_view, name="upload_images"),
    path("upload_images/", upload_pt_images, name="upload_pt_images"),
    path("upload_result/<str:message>/", upload_pt_result, name="upload_pt_result"),
    path("upload/", upload_image, name="upload_image"),
    path("annotate_image/<int:image_id>/", annotate_image, name="annotate_image"),
    path("annotate_images/", annotate_images, name="annotate_images"),
    path("select/", select_chapters, name="select_chapters"),
]
