import hashlib
import os
import uuid
import datetime
from django.shortcuts import render, redirect
from django.db import transaction
from .forms import ImageUploadForm
from .models import WhirMedicine
from django.core.files.storage import default_storage

IMAGE_PATH2 = "photo_pt/"


@transaction.atomic
def handle_new_upload(upload_filename, image_file, sha256, now):
    image_path = default_storage.save(
        os.path.join(IMAGE_PATH2, image_file.name), image_file
    )
    new_medicine = WhirMedicine(
        id=str(uuid.uuid4().int)[:19],
        create_time=now,
        name=upload_filename,
        img=image_path,
        sha256=sha256,
    )
    new_medicine.save()


@transaction.atomic
def handle_empty_sha256(latest_record, image_file, sha256, now):
    image_path = default_storage.save(
        os.path.join(IMAGE_PATH2, image_file.name), image_file
    )
    latest_record.img = image_path
    latest_record.sha256 = sha256
    latest_record.update_time = now
    latest_record.save()


@transaction.atomic
def handle_different_sha256(
    latest_record, upload_filename, upload_extension, image_file, sha256, now
):
    # 1. 重命名旧文件
    i = 1
    new_filename_for_old_image = f"{upload_filename}_{i}{upload_extension}"
    while default_storage.exists(os.path.join(IMAGE_PATH2, new_filename_for_old_image)):
        i += 1
        new_filename_for_old_image = f"{upload_filename}_{i}{upload_extension}"

    old_image_path = os.path.join(IMAGE_PATH2, os.path.basename(latest_record.img))
    default_storage.save(
        os.path.join(IMAGE_PATH2, new_filename_for_old_image),
        default_storage.open(old_image_path),
    )
    default_storage.delete(old_image_path)

    # 更新旧记录的img字段
    latest_record.img = os.path.join(IMAGE_PATH2, new_filename_for_old_image)
    latest_record.save()

    # 2. 保存新文件
    new_image_path = default_storage.save(
        os.path.join(IMAGE_PATH2, image_file.name), image_file
    )

    # 3. 在数据库中创建一个新的记录
    new_medicine = WhirMedicine(
        id=str(uuid.uuid4()),
        create_by=latest_record.create_by,
        create_time=latest_record.create_time,
        update_by=latest_record.update_by,
        update_time=now,
        sys_org_code=latest_record.sys_org_code,
        number=latest_record.number,
        name=latest_record.name,
        img=new_image_path,
        status=latest_record.status,
        steps=latest_record.steps,
        reference=latest_record.reference,
        compose=latest_record.compose,
        effect=latest_record.effect,
        indication=latest_record.indication,
        taboo=latest_record.taboo,
        enterprise=latest_record.enterprise,
        by_effect=latest_record.by_effect,
        symptom=latest_record.symptom,
        sha256=sha256,
    )
    new_medicine.save()


def upload_pt_images(request):
    if request.method != "POST":
        form = ImageUploadForm()
        return render(request, "upload_images.html", {"form": form})

    form = ImageUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, "upload_images.html", {"form": form})  # 可能需要添加错误信息

    # 获取多个文件
    image_files = request.FILES.getlist("images")

    # 对每个文件进行循环
    for image_file in image_files:
        if not image_file:  # 跳过NoneType文件
            continue

        name = os.path.splitext(image_file.name)[0]

        # 计算文件的SHA-256哈希值
        sha256 = hashlib.sha256(image_file.read()).hexdigest()
        image_file.seek(0)  # 将文件指针定位到文件开头

        # 分离文件名和扩展名
        upload_filename, upload_extension = os.path.splitext(image_file.name)

        # 查找所有与上传的文件名匹配的记录，并基于最新的修改时间排序它们
        records = WhirMedicine.objects.filter(name=upload_filename).order_by(
            "-update_time"
        )

        # 记录当前时间
        now = datetime.datetime.now()

        if not records.exists():
            handle_new_upload(upload_filename, image_file, sha256, now)
        else:
            latest_record = records.first()  # 获取最新的记录

            if not latest_record.sha256:
                handle_empty_sha256(latest_record, image_file, sha256, now)
            elif (
                upload_filename == latest_record.name
                and latest_record.sha256
                and latest_record.sha256 != sha256
            ):
                handle_different_sha256(
                    latest_record,
                    upload_filename,
                    upload_extension,
                    image_file,
                    sha256,
                    now,
                )
            else:
                continue

    return redirect("upload_pt_result", message=f"药品图片上传完毕!")


def upload_pt_result(request, message):
    return render(request, "result.html", {"message": message})
