import os
import pandas as pd
from pywebio.input import *
from pywebio.output import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URI, IMAGE_PATH, EQUIPMENT_ID
from models import WhirQyMedicine, WhirMedicine, WhirQyArchives
import datetime
import uuid

engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)

def create_records_from_file(df, brand, qy_id, session):
    created_count = 0
    skipped_count = 0
    for _, row in df.iterrows():
        medicine_name = row["药物通用名"]
        whir_medicine = session.query(WhirMedicine).filter_by(name=medicine_name).first()
        medicine_id = whir_medicine.id if whir_medicine else None
        record = session.query(WhirQyMedicine).filter_by(medicine_id=medicine_id, brand=brand).first()
        if record:
            skipped_count += 1
        else:
            record = WhirQyMedicine(
                id=str(uuid.uuid4().int)[:19],
                medicine_id=medicine_id,
                brand=brand,
                symptom=whir_medicine.symptom if whir_medicine else None,
                qy_id=qy_id,
                people="苏城",
                equipment_id=EQUIPMENT_ID,
                create_time=datetime.datetime.now(),
                update_time=datetime.datetime.now(),
            )
            session.add(record)
            created_count += 1
    session.commit()
    return created_count, skipped_count

def upload_images_to_records(images, session):
    uploaded_count = 0
    not_uploaded_images = []
    for image in images:
        medicine_name = image["filename"].split(".")[0]
        whir_medicine = session.query(WhirMedicine).filter_by(name=medicine_name).first()
        if whir_medicine is None:
            not_uploaded_images.append(image["filename"])
            continue
        medicine_id = whir_medicine.id
        record = session.query(WhirQyMedicine).filter_by(medicine_id=medicine_id).first()
        if record is None:
            not_uploaded_images.append(image["filename"])
            continue
        base, ext = os.path.splitext(image["filename"])
        filename = f"{base}_{record.qy_id}{ext}"
        filepath = os.path.join(IMAGE_PATH, filename)
        with open(filepath, "wb") as f:
            f.write(image["content"])
        uploaded_count += 1
        record.medicine_img = filepath
        record.update_time = datetime.datetime.now()
        session.commit()
    return uploaded_count, not_uploaded_images

def upload_images():
    session = Session()
    brand = input("请输入企业名称：", type=TEXT)
    whir_qy_archive = session.query(WhirQyArchives).filter_by(name=brand).first()
    if whir_qy_archive is None:
        put_text("没有找到与输入的企业名称匹配的企业。请检查输入的企业名称是否正确。")
        return
    qy_id = whir_qy_archive.id

    xlsx_file = file_upload("请选择一个xlsx文件：", accept=".xlsx")
    df = pd.read_excel(xlsx_file["content"])
    created_count, skipped_count = create_records_from_file(df, brand, qy_id, session)

    put_text("成功创建了 %d 个记录。" % created_count)
    put_text("跳过了 %d 个已存在的记录。" % skipped_count)

    images = file_upload("请选择一些图片：", accept="image/*", multiple=True)
    uploaded_count, not_uploaded_images = upload_images_to_records(images, session)
    put_text("成功上传了 %d 张图片。" % uploaded_count)
    if not_uploaded_images:
        put_text("以下图片未能上传：")
        for image_name in not_uploaded_images:
            put_text(image_name)
    session.close()

    put_text("成功上传了 %d 张图片。" % uploaded_count)
