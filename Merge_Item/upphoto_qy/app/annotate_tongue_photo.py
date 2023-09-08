from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .forms import TaggedDataForm, PictureFormSet
from .models import Picture, Physique


class ImageHandler:
    def __init__(self, request):
        self.request = request

    def check_new_images_in_session(self):
        if (
            "new_image_ids" not in self.request.session
            or not self.request.session["new_image_ids"]
        ):
            raise Http404("没有新的图片可以注解")

    def get_images_from_session(self):
        new_image_ids = self.request.session.get("new_image_ids", [])

        if not new_image_ids:
            return None, {}

        images = Picture.objects.filter(id__in=new_image_ids)
        return images, {image.id: image for image in images}

    def get_first_image_from_dict(self, image_dict):
        image_id = self.request.session["new_image_ids"][0]
        image = image_dict.get(image_id)
        if not image:
            raise Http404("没有新的图片可以注解")
        return image


@transaction.atomic
def upload_image(request):
    """处理上传图片请求并将新图片的ID存储在session中"""
    if request.method == "POST":
        formset = PictureFormSet(
            request.POST, request.FILES, queryset=Picture.objects.none()
        )
        if formset.is_valid():
            new_images = create_picture_objects(request)
            Picture.objects.bulk_create(new_images)
            request.session["new_image_ids"] = [image.id for image in new_images]
            return HttpResponseRedirect(reverse("annotate_images"))
    else:
        formset = PictureFormSet(queryset=Picture.objects.none())
    return render(request, "upload_image.html", {"formset": formset})


def create_picture_objects(request):
    """从请求中创建Picture对象列表"""
    return [
        Picture(path=uploaded_file)
        for uploaded_file in request.FILES.getlist("form-0-path")
    ]


@transaction.atomic
def annotate_images(request):
    handler = ImageHandler(request)
    images, image_dict = handler.get_images_from_session()

    if not images:
        raise Http404("没有新的图片可以注解")

    image = handler.get_first_image_from_dict(image_dict)
    return annotate_image(request, image.id, image=image, image_dict=image_dict)


@transaction.atomic
def annotate_image(request, image_id, image=None, image_dict=None):
    if not image:
        image = get_image_from_id(image_id)

    if request.method == "POST":
        form = TaggedDataForm(request.POST)
        if form.is_valid():
            if not is_tongue_features_valid(form):
                form.add_error(None, "舌象特征不应重复")
            else:
                save_form_data(form, image)
                return navigate_to_next_or_upload(request, image_dict)
    else:
        form = TaggedDataForm()

    return render(request, "annotate_image.html", {"form": form, "image": image})


def get_image_from_id(image_id):
    """根据ID从数据库中获取图片对象"""
    return get_object_or_404(Picture, id=image_id)


def is_tongue_features_valid(form):
    """检查舌象特征是否重复"""
    tongue_features = get_tongue_features_from_form(form)
    return len(tongue_features) == len(set(tongue_features))


def get_tongue_features_from_form(form):
    """从表单中获取舌象特征列表"""
    feature_keys = [
        "tongue_color",
        "moss_color",
        "moss_quality",
        "body_fluid",
        "sublingual_collaterals",
    ]
    return [form.cleaned_data[k] for k in feature_keys]


def save_form_data(form, image):
    """保存表单数据到数据库"""
    feature = form.save(commit=False)
    feature.picture = image
    handle_physique_selection(feature, form)
    selected_tongue_shapes = form.cleaned_data["tongue_shape"]
    feature.tongue_shape_ids = [ts.id for ts in selected_tongue_shapes]
    feature.save()


def handle_physique_selection(feature, form):
    """处理体质选择的逻辑"""

    physiques = Physique.objects.all()
    physique_lookup = {tuple(sorted(p.single_ids)): p for p in physiques}

    selected_physiques = form.cleaned_data["physique"]
    sorted_selected_physiques_ids = tuple(sorted([p.id for p in selected_physiques]))

    feature.single_physique_ids = sorted_selected_physiques_ids

    if len(sorted_selected_physiques_ids) == 1:
        feature.physique_type = Physique.SINGLE
        feature.physique_id = [sorted_selected_physiques_ids[0]]
        return
    feature.physique_type = Physique.MIXED
    matched_physique = physique_lookup.get(sorted_selected_physiques_ids)
    if matched_physique:
        feature.physique_id = [matched_physique.id]
    else:
        feature.physique_id = sorted_selected_physiques_ids


def navigate_to_next_or_upload(request, image_dict):
    """导航到下一张图片或返回上传页面"""
    request.session["new_image_ids"].pop(0)
    request.session.modified = True

    if request.session.get("new_image_ids"):
        next_image_id = request.session["new_image_ids"][0]
        next_image = image_dict.get(next_image_id)
        if not next_image:
            raise Http404("没有新的图片可以注解")
        return HttpResponseRedirect(reverse("annotate_image", args=(next_image_id,)))
    else:
        return HttpResponseRedirect(reverse("upload_image"))
