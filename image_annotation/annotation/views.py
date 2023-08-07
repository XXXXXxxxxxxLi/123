from django.shortcuts import render
from django.urls import reverse
from .models import Picture, Tagged_Data, Mixed_Physique
from django.http import HttpResponseRedirect, Http404
from .forms import PictureForm, TaggedDataForm, PictureFormSet
from django.shortcuts import get_object_or_404
from django.db import transaction

@transaction.atomic
def upload_image(request):
    if request.method == "POST":
        formset = PictureFormSet(
            request.POST, request.FILES, queryset=Picture.objects.none()
        )

        if formset.is_valid():
            new_images = [
                Picture(path=uploaded_file) for uploaded_file in request.FILES.getlist("form-0-path")
            ]
            Picture.objects.bulk_create(new_images)

            # 存储新上传的图片ID
            request.session["new_image_ids"] = [image.id for image in new_images]
            return HttpResponseRedirect(reverse("annotation:annotate_images"))
    else:
        formset = PictureFormSet(queryset=Picture.objects.none())

    return render(request, "upload_image.html", {"formset": formset})


@transaction.atomic
def annotate_images(request):
    if "new_image_ids" not in request.session or not request.session["new_image_ids"]:
        raise Http404("没有新的图片可以注解")
    image_id = request.session["new_image_ids"][0]
    return annotate_image(request, image_id)



def annotate_image(request, image_id):
    image = get_object_or_404(Picture, id=image_id)

    if request.method == "POST":
        form = TaggedDataForm(request.POST)
        if form.is_valid():
            feature = form.save(commit=False)
            feature.picture = image

            selected_physiques = form.cleaned_data["single_physique"]
            sorted_selected_physiques = sorted([p.id for p in selected_physiques])

            mixed_physiques_map = {mp.single_ids: mp for mp in Mixed_Physique.objects.all()}

            if len(selected_physiques) == 1:
                feature.physique_type = "单一体质"
                feature.physique_id = [sorted_selected_physiques[0]]
                feature.single_physique_ids = [sorted_selected_physiques[0]]
            else:
                feature.physique_type = "兼夹体质"
                combined_ids = sorted_selected_physiques

                mixed_physique = mixed_physiques_map.get(",".join(map(str, combined_ids)))
                if mixed_physique:
                    feature.physique_id = [mixed_physique.id]
                    feature.single_physique_ids = list(map(int, mixed_physique.single_ids.split(",")))
                else:
                    feature.physique_id = combined_ids
                    feature.single_physique_ids = combined_ids

            # 设置舌形
            selected_tongue_shapes = form.cleaned_data["tongue_shape"]
            feature.tongue_shape_ids = [ts.id for ts in selected_tongue_shapes]

            # 保存
            feature.save()

            if "new_image_ids" in request.session and request.session["new_image_ids"]:
                request.session["new_image_ids"].pop(0)
                request.session.modified = True

            if request.session.get("new_image_ids"):
                next_image_id = request.session["new_image_ids"][0]
                return HttpResponseRedirect(
                    reverse("annotation:annotate_image", args=(next_image_id,))
                )
            else:
                return HttpResponseRedirect(reverse("annotation:upload_image"))

    else:
        form = TaggedDataForm()

    return render(request, "annotate_image.html", {"form": form, "image": image})
