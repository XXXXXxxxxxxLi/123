from datetime import datetime
import hashlib
import os
import uuid
import logging
from pywebio.input import *
from pywebio.output import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from models import WhirMedicine
from config import DB_URI, IMAGE_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库引擎和session
engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)
session = Session()


def update_db(record, now, img, name, sha256):
    # 如果数据库中已存在相同的sha256，就返回
    existing_sha256 = (
        session.query(WhirMedicine).filter(WhirMedicine.sha256 == sha256).first()
    )
    if existing_sha256 is not None:
        logger.info(f"图片 {img['filename']} 的sha256值已存在，跳过处理")
        return None
    img_path = os.path.join(IMAGE_PATH, img["filename"])
    try:
        if record is None:  # 如果没有匹配的name字段，插入新记录
            with open(img_path, "wb") as f:
                f.write(img["content"])
            new_medicine = WhirMedicine(
                id=str(uuid.uuid4()),
                create_time=now,
                name=name,
                img=img_path,
                sha256=sha256,
            )
            session.add(new_medicine)
            logger.info(f"为图片 {img['filename']} 添加了新记录")
            session.commit()
            return new_medicine
        else:  # 如果有匹配的name字段
            if record.sha256 and record.sha256 != sha256:  # sha256字段不为空且不相同
                if os.path.exists(img_path):  # 检查文件路径是否存在
                    # 查找已经存在的同名文件的数量
                    same_name_count = (
                        session.query(WhirMedicine)
                        .filter(WhirMedicine.name == name)
                        .count()
                    )
                    old_img_path = os.path.join(
                        IMAGE_PATH,
                        f"{name}_{now.strftime('%Y%m%d')}_{same_name_count}{os.path.splitext(img['filename'])[1]}",
                    )
                    os.rename(img_path, old_img_path)  # 修改保存路径下的文件名
                    record.img = old_img_path  # 更新数据库中对应的img字段
                    session.commit()  # 提交对数据库的修改
                # 保存新文件
                with open(img_path, "wb") as f:
                    f.write(img["content"])
                # 创建新记录
                new_medicine = WhirMedicine(
                    id=str(uuid.uuid4()),
                    create_time=now,
                    update_time=now,
                    name=name,
                    img=img_path,
                    sha256=sha256,
                    create_by=record.create_by,
                    sys_org_code=record.sys_org_code,
                    number=record.number,
                    status=record.status,
                    steps=record.steps,
                    reference=record.reference,
                    compose=record.compose,
                    effect=record.effect,
                    indication=record.indication,
                    taboo=record.taboo,
                    enterprise=record.enterprise,
                    by_effect=record.by_effect,
                    symptom=record.symptom,
                )
                session.add(new_medicine)
                logger.info(f"更新了图片 {img['filename']} 的记录")
                session.commit()
                return new_medicine
            else:
                # sha256字段为空，更新img字段和sha256字段以及update_time字段
                with open(img_path, "wb") as f:
                    f.write(img["content"])
                record.img = img_path
                record.sha256 = sha256
                record.update_time = now
                session.commit()
                return record
    except SQLAlchemyError as e:
        logger.error(f"数据库错误：{e}")
        return None


def process_image(img):
    try:
        # 对图片进行处理，直接在这里计算图片的sha256哈希值
        sha256_hash = hashlib.sha256()
        sha256_hash.update(img["content"])
        sha256 = sha256_hash.hexdigest()
        # 从文件名获取name字段
        name = os.path.splitext(img["filename"])[0]
        # 查询数据库中是否有相同的name字段
        record = (
            session.query(WhirMedicine)
            .filter(WhirMedicine.name == name)
            .order_by(WhirMedicine.update_time.desc())
            .first()
        )
        now = datetime.now()
        # 更新数据库
        updated_record = update_db(record, now, img, name, sha256)
        return True, sha256, updated_record
    except Exception as e:
        logger.error(f"图片处理错误：{e}")
        return False, None, None


def upload_images():
    images = file_upload("上传图片", accept="image/*", multiple=True)
    if not images:
        return

    # 创建一个字典保存所有文件的信息
    file_info = {}
    for img in images:
        sha256_hash = hashlib.sha256()
        sha256_hash.update(img["content"])
        sha256 = sha256_hash.hexdigest()
        name = os.path.splitext(img["filename"])[0]
        file_info[sha256] = {"img": img, "name": name}

    # 一次性查询数据库中所有具有这些SHA256值的记录
    existing_sha256s = (
        session.query(WhirMedicine.sha256)
        .filter(WhirMedicine.sha256.in_(file_info.keys()))
        .all()
    )
    existing_sha256s = [item[0] for item in existing_sha256s]

    # 对于每个文件，如果它的SHA256在数据库中不存在，那么处理它
    for sha256, info in file_info.items():
        if sha256 not in existing_sha256s:
            # 调用你的处理函数处理文件
            record = (
                session.query(WhirMedicine)
                .filter(WhirMedicine.name == info["name"])
                .order_by(WhirMedicine.update_time.desc())
                .first()
            )
            now = datetime.now()
            # 更新数据库
            updated_record = update_db(record, now, info["img"], info["name"], sha256)
            if updated_record is not None:
                now = datetime.now()
                put_table(
                    [
                        ["药品名称", "图片", "效果", "适应症", "症状"],
                        [
                            updated_record.name,
                            updated_record.img,
                            updated_record.effect,
                            updated_record.indication,
                            updated_record.symptom,
                        ],
                    ]
                )

                form_data = input_group(
                    "修改数据",
                    [
                        input("药品名称", value=updated_record.name, name="name"),
                        input(
                            "图片", value=updated_record.img, required=True, name="img"
                        ),
                        input(
                            "效果",
                            value=updated_record.effect,
                            required=False,
                            name="effect",
                        ),
                        input(
                            "适应症",
                            value=updated_record.indication,
                            required=False,
                            name="indication",
                        ),
                        input(
                            "症状",
                            value=updated_record.symptom,
                            required=False,
                            name="symptom",
                        ),
                    ],
                )

                for key, value in form_data.items():
                    setattr(updated_record, key, value)
                updated_record.update_time = now
                session.commit()

    put_text("上传成功！")
