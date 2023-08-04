from pywebio.input import *
from pywebio.output import *
from pywebio import start_server
from pywebio.session import hold
import psycopg2
import os
from datetime import datetime
import hashlib

def login():
    while True:
        data = input_group("登录", [
            input("输入用户名", name="username", required=True),
            input("输入密码", name="password", type=PASSWORD,required=True)
        ])
        if data['username'] == 'kangli' and data['password'] == 'kangli':
            break
        else:
            put_text("错误的用户名或密码，请重试。")

def upload_images():
    images = file_upload("上传图片", accept="image/*", multiple=True)
    if not images:
        return

    conn = psycopg2.connect(
        dbname="lichangfa_test",
        user="postgres",
        password="ai_tongue",
        host="172.18.0.2",
        port="5432"
    )

    cursor = conn.cursor()

    for img in images:
        sha256_hash = hashlib.sha256()
        sha256_hash.update(img['content'])
        sha256 = sha256_hash.hexdigest()

        name = os.path.splitext(img['filename'])[0]  # 从文件名获取name字段
        cursor.execute("SELECT * FROM whir_medicine WHERE name = %s;", (name,))
        record = cursor.fetchone()
        now = datetime.now()

        if record is None:  # 如果没有匹配的name字段，插入新记录
            img_path = os.path.join('/home/user_li/photo', img['filename'])
            with open(img_path, 'wb') as f:
                f.write(img['content'])
            cursor.execute("INSERT INTO whir_medicine (create_time, name, img, sha256) VALUES (%s, %s, %s, %s);",
                           (now, name, img_path, sha256))
        else:  # 如果有匹配的name字段
            if record[-1] == '' or record[-1] is None:  # sha256字段为空，更新img字段和sha256字段以及update_time字段
                img_path = os.path.join('/home/user_li/photo', img['filename'])
                with open(img_path, 'wb') as f:
                    f.write(img['content'])
                cursor.execute("UPDATE whir_medicine SET img = %s, sha256 = %s, update_time = %s WHERE name = %s;",
                               (img_path, sha256, now, name))
            elif record[-1] != sha256:  # sha256字段不为空且不相同，先修改旧记录的文件名，然后更新img字段，插入新记录
                if os.path.exists(record[6]):  # 检查旧文件是否存在
                    old_img_path = os.path.join('/home/user_li/photo',
                                                f"{name}_{now.strftime('%Y%m%d')}{os.path.splitext(img['filename'])[1]}")
                    os.rename(record[6], old_img_path)
                    cursor.execute("UPDATE whir_medicine SET img = %s , update_time = %s WHERE name = %s;",
                                   (old_img_path, now, name))
                img_path = os.path.join('/home/user_li/photo', img['filename'])
                with open(img_path, 'wb') as f:
                    f.write(img['content'])
                data = (
                now, now, record[2], record[3], record[4], name, img_path, record[7], record[8], record[9], record[10],
                record[11], record[12],
                record[13], record[14], record[15], record[16], record[17], record[18], sha256)
                cursor.execute(
                    "INSERT INTO whir_medicine (create_time, update_time, status, sys_org_code, number, name, img, steps, reference, compose, effect, "
                    "indication, taboo, enterprise, by_effect, id, symptom, create_by, update_by, sha256) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", data)

        conn.commit()

        # 打印上传图片的结果
        cursor.execute("SELECT * FROM whir_medicine WHERE sha256 = %s;", (sha256,))
        record = cursor.fetchone()
        put_table([
            ['name', 'img', 'effect', 'indication', 'symptom'],
            [record[5], record[6], record[10], record[11], record[16]],
        ])

        # 生成表单来修改数据
        form_data = input_group("修改数据",[
            input('name', value=record[5], required=True, name='name'),
            input('img', value=record[6], required=True, name='img'),
            input('effect', value=record[10], required=True, name='effect'),
            input('indication', value=record[11], required=True, name='indication'),
            input('symptom', value=record[16], required=True, name='symptom'),
        ])

        # 将修改的数据更新到数据库中
        cursor.execute("UPDATE whir_medicine SET name = %s, img = %s, effect = %s, indication = %s, symptom = %s WHERE sha256 = %s;",
                        (form_data['name'], form_data['img'], form_data['effect'], form_data['indication'], form_data['symptom'], sha256))

        conn.commit()

    cursor.close()
    conn.close()

    put_text('图片上传成功，路径保存在数据库中')

def main():
    login()
    upload_images()

start_server(main, port=5004)

