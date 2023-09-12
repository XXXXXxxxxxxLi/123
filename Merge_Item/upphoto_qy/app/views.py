import os
import pandas as pd
from .forms import UploadImagesForm
from .models import WhirQyMedicine, WhirMedicine, WhirQyArchives, WhirEquipment
from django.utils import timezone

import uuid
from django.db import transaction
from collections import defaultdict

IMAGE_PATH1 = "./photo_qy"

class DatabaseFetcher:
    def get_equipment_ids(self, qy_id):
        return defaultdict(
            list,
            {
                equipment["qy_id"]: str(equipment["equipment_id"])
                for equipment in WhirEquipment.objects.filter(qy_id=qy_id).values(
                    "qy_id", "equipment_id"
                )
            },
        )

    def get_all_medicines(self, df):
        return {
            medicine.name: medicine
            for medicine in WhirMedicine.objects.filter(name__in=df["药物通用名"].unique())
        }

    def get_qy_data(self, brand):
        whir_qy_archive = WhirQyArchives.objects.filter(name=brand).first()
        all_qy_medicines = {
            (qy_medicine.medicine_id, qy_medicine.brand): qy_medicine
            for qy_medicine in WhirQyMedicine.objects.filter(brand=brand)
        }

        return {
            "whir_qy_archive": whir_qy_archive,
            "all_qy_medicines": all_qy_medicines,
        }

    def get_all_data(self, brand, df):
        data = self.get_qy_data(brand)
        data["equipment_ids"] = None
        data["all_medicines"] = self.get_all_medicines(df)
        if data["whir_qy_archive"]:
            qy_id = data["whir_qy_archive"].id
            data["equipment_ids"] = self.get_equipment_ids(qy_id)
        return data


def upload_images_view(request):
    context = {}
    form = UploadImagesForm(
        request.POST if request.method == "POST" else None, request.FILES or None
    )
    context["form"] = form

    if request.method != "POST":
        return render(request, "upload_qy.html", context)

    if not form.is_valid():
        return render(request, "upload_qy.html", context)

    sid = transaction.savepoint()

    try:
        with transaction.atomic():
            brand = form.cleaned_data["brand"]
            xlsx_file = form.cleaned_data["xlsx_file"]
            images = request.FILES.getlist("images")

            df = pd.read_excel(xlsx_file.file)

            # 使用 DatabaseFetcher 类来获取所有数据
            fetcher = DatabaseFetcher()
            data = fetcher.get_all_data(brand, df)

            whir_qy_archive = data["whir_qy_archive"]
            if not whir_qy_archive:
                context["error"] = "没有找到与输入的企业名称匹配的企业。请检查输入的企业名称是否正确。"
                return render(request, "upload_qy.html", context)

            qy_id = whir_qy_archive.id
            equipment_ids_dict = data["equipment_ids"]
            all_medicines = data["all_medicines"]
            all_qy_medicines = data["all_qy_medicines"]

            created_count, skipped_count = create_records_from_file(
                df, brand, qy_id, all_medicines, all_qy_medicines, equipment_ids_dict
            )

            (
                uploaded_count,
                not_uploaded_images,
                uploaded_image_names,
            ) = upload_images_to_records(
                images, brand, all_medicines, all_qy_medicines, qy_id
            )

            context["message"] = compose_message(
                created_count, skipped_count, uploaded_count
            )
            context["unmatched_image_names"] = not_uploaded_images  # 这里是存储不匹配图片名的列表
            context["uploaded_image_names"] = uploaded_image_names  # 这里是存储上传成功图片名的列表

            return render(request, "success_qy.html", context)

    except Exception as e:
        transaction.savepoint_rollback(sid)
        context["error"] = str(e)
        return render(request, "upload_qy.html", context)


def compose_message(created_count, skipped_count, uploaded_count):
    return f"成功创建了 {created_count} 个记录。跳过了 {skipped_count} 个已存在的记录。成功上传了 {uploaded_count} 张图片。"


def create_records_from_file(
    df, brand, qy_id, all_medicines, all_qy_medicines, equipment_ids_dict
):
    created_count = 0
    skipped_count = 0
    new_records = []
    for row in df.itertuples(index=False):  # 使用itertuples替代iterrows
        medicine_name = getattr(row, "药物通用名")
        whir_medicine = all_medicines.get(medicine_name)
        medicine_id = whir_medicine.id if whir_medicine else None
        if (medicine_id, brand) in all_qy_medicines:
            skipped_count += 1
        else:
            equipment_ids = equipment_ids_dict[qy_id]
            equipment_id_str = ",".join(equipment_ids)
            new_records.append(
                WhirQyMedicine(
                    id=str(uuid.uuid4().int)[:19],
                    medicine_id=medicine_id,
                    brand=brand,
                    symptom=whir_medicine.symptom if whir_medicine else None,
                    qy_id=qy_id,
                    people="苏城",
                    equipment_id=equipment_id_str,
                    create_time=timezone.now(),
                    update_time=timezone.now(),
                )
            )
            created_count += 1
    WhirQyMedicine.objects.bulk_create(new_records)  # 批量插入
    return created_count, skipped_count


def upload_images_to_records(images, brand, all_medicines, all_qy_medicines, qy_id):
    uploaded_count = 0
    not_uploaded_images = []
    uploaded_image_names = []  # 新建一个列表来存储上传成功的图片名

    if not os.path.exists(IMAGE_PATH1):
        os.makedirs(IMAGE_PATH1)
    for image in images:
        medicine_name = image.name.split(".")[0]
        whir_medicine = all_medicines.get(medicine_name)
        if whir_medicine is None:
            not_uploaded_images.append(image.name)
            continue
        medicine_id = whir_medicine.id
        record = all_qy_medicines.get((medicine_id, brand))
        if record is None:
            not_uploaded_images.append(image.name)
            continue

        base, ext = os.path.splitext(image.name)
        filename = f"{base}_{qy_id}{ext}"
        uploaded_image_names.append(filename)  # 添加成功上传的图片名到列表中

        filepath = os.path.join(IMAGE_PATH1, filename)
        with open(filepath, "wb") as f:
            for chunk in image.chunks():
                f.write(chunk)
        uploaded_count += 1
        record.medicine_img = filepath
        record.update_time = timezone.now()
        record.save()

    return uploaded_count, not_uploaded_images, uploaded_image_names


def index_view(request):
    return render(request, "index.html")


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "用户名已存在，请选择一个不同的用户名。")
        else:
            User.objects.create(username=username, password=password)
            return redirect("login")

    return render(request, "register.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if User.objects.filter(username=username, password=password).exists():
            return redirect("index")
        else:
            messages.error(request, "无效的凭证，请重试。")

    return render(request, "login.html")
