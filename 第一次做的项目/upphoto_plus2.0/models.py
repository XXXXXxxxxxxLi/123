# 导入sqlalchemy中的需要的模块
from sqlalchemy import Column, String, DateTime, Integer

# 导入sqlalchemy的声明基类
from sqlalchemy.ext.declarative import declarative_base

# 创建基类
Base = declarative_base()


# 定义一个名为WhirMedicine的类，继承自declarative_base
class WhirMedicine(Base):
    # 定义数据库表名
    __tablename__ = "whir_medicine"

    # 定义表的列及属性
    id = Column(Integer, primary_key=True)  # 主键ID
    name = Column(String)  # 名称
    img = Column(String)  # 图片
    sha256 = Column(String)  # SHA256
    create_time = Column(DateTime)  # 创建时间
    update_time = Column(DateTime)  # 更新时间
    status = Column(Integer)  # 状态
    sys_org_code = Column(String)  # 组织代码
    number = Column(String)  # 编号
    steps = Column(String)  # 步骤
    reference = Column(String)  # 引用
    compose = Column(String)  # 组成
    effect = Column(String)  # 效果
    indication = Column(String)  # 指示
    taboo = Column(String)  # 禁忌
    enterprise = Column(String)  # 企业
    by_effect = Column(String)  # 副作用
    symptom = Column(String)  # 症状
    create_by = Column(String)  # 创建者
    update_by = Column(String)  # 更新者
