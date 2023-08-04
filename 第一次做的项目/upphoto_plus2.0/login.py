# 导入 PyWebIO 输入和输出模块
from pywebio.input import *
from pywebio.output import *


def login():
    # 使用一个无限循环来反复询问用户输入，直到输入正确为止
    while True:
        # 通过 PyWebIO 获取用户名和密码
        data = input_group(
            "登录",
            [
                input("输入用户名", name="username", required=True),
                input("输入密码", name="password", type=PASSWORD, required=True),
            ],
        )

        # 检查用户名和密码是否正确
        if data["username"] == "kangli" and data["password"] == "kangli":
            # 如果用户名和密码正确，则跳出循环
            break
        else:
            # 如果用户名或密码错误，则提示用户重试
            put_text("错误的用户名或密码，请重试。")
