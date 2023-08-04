from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WhirMedicine(Base):
    __tablename__ = 'whir_medicine'

    id = Column(String(36), primary_key=True)  # 主键ID
    create_by = Column(String(50))
    create_time = Column(DateTime)
    update_by = Column(String(50))
    update_time = Column(DateTime)
    sys_org_code = Column(String(64))
    number = Column(String(255))
    name = Column(String(255))
    img = Column(String(255))
    status = Column(Integer)
    steps = Column(String(1024))
    reference = Column(String(255))
    compose = Column(String(512))
    effect = Column(String(255))
    indication = Column(String(512))
    taboo = Column(Text)
    enterprise = Column(String(255))
    by_effect = Column(Text)
    symptom = Column(String(255))
    sha256 = Column(String(500))

    # 建立与 WhirQyMedicine 的一对多关系
    whir_qy_medicines = relationship('WhirQyMedicine', backref='whir_medicine')

class WhirQyArchives(Base):
    __tablename__ = 'whir_qy_archives'

    id = Column(String(36), primary_key=True)  # 主键ID
    create_by = Column(String(50))
    create_time = Column(DateTime)
    update_by = Column(String(50))
    update_time = Column(DateTime)
    sys_org_code = Column(String(64))
    name = Column(String(255))
    tax_number = Column(String(255))
    licence = Column(String(255))
    person = Column(String(255))
    address = Column(String(255))
    phone = Column(String(32))
    email = Column(String(255))
    qy_explain = Column(String(255))
    status = Column(Integer)
    logo = Column(String(255))

    # 建立与 WhirQyMedicine 的一对多关系
    whir_qy_medicines = relationship('WhirQyMedicine', backref='whir_qy_archives')

class WhirQyMedicine(Base):
    __tablename__ = 'whir_qy_medicine'

    id = Column(String(36), primary_key=True)  # 主键ID
    create_by = Column(String(50))
    create_time = Column(DateTime)
    update_by = Column(String(50))
    update_time = Column(DateTime)
    sys_org_code = Column(String(64))
    qy_id = Column(String(32), ForeignKey('whir_qy_archives.id'))  # whir_qy_archives的外键
    medicine_id = Column(String(32), ForeignKey('whir_medicine.id'))  # whir_medicine的外键
    brand = Column(String(255))
    specifications = Column(String(255))
    model = Column(String(255))
    medicine_img = Column(String(255))
    img_date = Column(DateTime)
    checkstatus = Column(Integer)
    checkdate = Column(DateTime)
    checkexplain = Column(String(255))
    people = Column(String(255))
    equipment_id = Column(String(2555))
    symptom = Column(String(255))
