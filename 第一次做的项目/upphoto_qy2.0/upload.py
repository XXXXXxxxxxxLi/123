import os
import pandas as pd
from pywebio.input import *
from pywebio.output import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URI, IMAGE_PATH
from models import WhirQyMedicine, WhirMedicine, WhirQyArchives, WhirEquipment
import datetime
import uuid

engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)


def create_records_from_file(
    df, brand, qy_id, session, all_medicines, all_qy_medicines, all_equipments
):
    created_count = 0
    skipped_count = 0
    for _, row in df.iterrows():
        medicine_name = row["药物通用名"]
        whir_medicine = all_medicines.get(medicine_name)
        medicine_id = whir_medicine.id if whir_medicine else None
        record = all_qy_medicines.get((medicine_id, brand))
        if record:
            skipped_count += 1
        else:
            # 查询 whir_equipment 表，获取相同 qy_id 的所有 equipment_id
            equipment_ids = (
                session.query(WhirEquipment.equipment_id).filter_by(qy_id=qy_id).all()
            )
            # 将所有的 equipment_id 连接成一个字符串，用逗号分隔
            equipment_id_str = ",".join(eid[0] for eid in equipment_ids)
            record = WhirQyMedicine(
                id=str(uuid.uuid4().int)[:19],
                medicine_id=medicine_id,
                brand=brand,
                symptom=whir_medicine.symptom if whir_medicine else None,
                qy_id=qy_id,
                people="苏城",
                equipment_id=equipment_id_str,  # 使用逗号分隔的字符串
                create_time=datetime.datetime.now(),
                update_time=datetime.datetime.now(),
            )
            session.add(record)
            created_count += 1
    return created_count, skipped_count


def upload_images_to_records(
    images, session, brand, all_medicines, all_qy_medicines, all_equipments
):
    uploaded_count = 0
    not_uploaded_images = []
    for image in images:
        medicine_name = image["filename"].split(".")[0]
        whir_medicine = all_medicines.get(medicine_name)
        if whir_medicine is None:
            not_uploaded_images.append(image["filename"])
            continue
        medicine_id = whir_medicine.id
        record = all_qy_medicines.get((medicine_id, brand))  # 现在 brand 是作为参数传递的
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
    return uploaded_count, not_uploaded_images


def upload_images():
    session = Session()
    try:
        brand = input("请输入企业名称：", type=TEXT)
        whir_qy_archive = session.query(WhirQyArchives).filter_by(name=brand).first()
        if whir_qy_archive is None:
            put_text("没有找到与输入的企业名称匹配的企业。请检查输入的企业名称是否正确。")
            return
        qy_id = whir_qy_archive.id
        all_medicines = {
            medicine.name: medicine for medicine in session.query(WhirMedicine).all()
        }
        all_qy_medicines = {
            (qy_medicine.medicine_id, qy_medicine.brand): qy_medicine
            for qy_medicine in session.query(WhirQyMedicine).all()
        }
        all_equipments = {
            equipment.qy_id: equipment
            for equipment in session.query(WhirEquipment).all()
        }

        xlsx_file = file_upload("请选择一个xlsx文件：", accept=".xlsx")
        df = pd.read_excel(xlsx_file["content"])
        created_count, skipped_count = create_records_from_file(
            df, brand, qy_id, session, all_medicines, all_qy_medicines, all_equipments
        )

        put_text("成功创建了 %d 个记录。" % created_count)
        put_text("跳过了 %d 个已存在的记录。" % skipped_count)

        images = file_upload("请选择一些图片：", accept="image/*", multiple=True)
        uploaded_count, not_uploaded_images = upload_images_to_records(
            images, session, brand, all_medicines, all_qy_medicines, all_equipments
        )
        put_text("成功上传了 %d 张图片。" % uploaded_count)
        if not_uploaded_images:
            put_text("以下图片未能上传：")
            for image_name in not_uploaded_images:
                put_text(image_name)
        session.commit()
    except Exception as e:
        session.rollback()  # 发生异常，回滚事务
        put_text(f"发生错误：{str(e)}，所有操作已回滚。")
    finally:
        session.close()
