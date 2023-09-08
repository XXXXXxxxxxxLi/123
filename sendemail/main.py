import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import psycopg2
import smtplib
import os
from data import column_translations
import logging

logging.basicConfig(
    filename="program_output.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
)


class DatabaseManager:
    def __init__(self, db_name, user, password, host, port):
        try:
            self.conn = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port,
            )
        except Exception as e:
            logging.info(f"连接到数据库时出现错误: {e}")
            self.conn = None

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
            logging.info("数据库连接已关闭")
        else:
            logging.info("没有打开的数据库连接可以关闭")

    def get_qy_ids(self):
        cursor = self.conn.cursor()
        query = "SELECT id, email FROM whir_qy_archives"
        try:
            self.conn.autocommit = False  # 开启事务
            logging.info("开始从 whir_qy_archives 获取企业 ID 和邮箱...")
            cursor.execute(query)
            data = cursor.fetchall()
            self.conn.commit()  # 提交事务
            logging.info("成功获取企业 ID 和邮箱")
            return {item[0]: item[1] for item in data}
        except Exception as e:
            self.conn.rollback()  # 出现异常时回滚事务
            logging.info(f"获取企业 ID 和邮箱时出现错误: {e}")
            return {}
        finally:
            self.conn.autocommit = True  # 恢复自动提交

    def get_data_from_db(self, qy_ids, start_date, end_date):
        cursor = self.conn.cursor()
        data_frame_dict = {}

        try:
            self.conn.autocommit = False  # 开启事务
            logging.info("开始从数据库获取数据...")

            # Query 1
            query = """
                SELECT 
                    e.qy_id,
                    i.equipment_id, 
                    COUNT(*) AS frequency, 
                    SUM(CASE WHEN i.remarks = '报告生成成功' THEN 1 ELSE 0 END) AS successful_reports
                FROM whir_inspect i
                INNER JOIN whir_equipment e ON i.equipment_id = e.equipment_id
                WHERE i.create_time BETWEEN %s AND %s 
                AND e.qy_id = ANY(%s)
                GROUP BY e.qy_id, i.equipment_id
            """
            cursor.execute(query, (start_date, end_date, qy_ids))
            data = cursor.fetchall()

            for row in data:
                qy_id = row[0]
                if qy_id not in data_frame_dict:
                    data_frame_dict[qy_id] = {
                        "企业ID": [],
                        "设备ID": [],
                        "检测次数": [],
                        "成功报告": [],
                    }

                data_frame_dict[qy_id]["企业ID"].append(row[0])
                data_frame_dict[qy_id]["设备ID"].append(row[1])
                data_frame_dict[qy_id]["检测次数"].append(row[2])
                data_frame_dict[qy_id]["成功报告"].append(row[3])

            # Query 2
            query_detailed = """
                SELECT 
                    i.*, 
                    e.qy_id
                FROM whir_inspect i
                INNER JOIN whir_equipment e ON i.equipment_id = e.equipment_id
                WHERE i.create_time BETWEEN %s AND %s 
                AND e.qy_id = ANY(%s)
            """
            cursor.execute(query_detailed, (start_date, end_date, qy_ids))
            detailed_data = cursor.fetchall()
            detailed_colnames = [desc[0] for desc in cursor.description]

            detailed_df = pd.DataFrame(detailed_data, columns=detailed_colnames)
            detailed_df.rename(columns=column_translations, inplace=True)

            for qy_id in data_frame_dict:
                df2 = pd.DataFrame(data_frame_dict[qy_id])
                df1 = detailed_df[detailed_df["企业ID"] == qy_id]
                total_records = df2["检测次数"].sum()
                total_successful_reports = df2["成功报告"].sum()

                new_row = pd.DataFrame(
                    {
                        "企业ID": ["总计"],
                        "设备ID": [""],
                        "检测次数": [total_records],
                        "成功报告": [total_successful_reports],
                    }
                )
                df2 = pd.concat([df2, new_row], ignore_index=True)
                data_frame_dict[qy_id] = (df1, df2)

            self.conn.commit()  # 提交事务
            logging.info("成功从数据库获取数据")
            return data_frame_dict
        except Exception as e:
            self.conn.rollback()  # 出现异常时回滚事务
            logging.info(f"从数据库获取数据时出现错误: {e}")
            return {}
        finally:
            self.conn.autocommit = True


def save_data_to_xlsx(data1, data2):
    try:
        logging.info("开始保存数据到xlsx文件...")
        if data1 is not None and data2 is not None:
            with pd.ExcelWriter("Monthly report.xlsx") as writer:
                data1.to_excel(writer, sheet_name="Enterprise Data")
            with pd.ExcelWriter("weekly.xlsx") as writer:
                data2.to_excel(writer, sheet_name="Frequency Data")
            logging.info("数据已成功保存到xlsx文件")
        else:
            logging.info("没有数据可以保存")
    except Exception as e:
        logging.info(f"保存数据到xlsx文件时出现错误: {e}")


def send_email(to_address, files_to_send):
    try:
        for file in files_to_send:
            if not os.path.exists(file):
                raise FileNotFoundError(f"Output file '{file}' not found.")

        logging.info(f"开始发送邮件到 {to_address}...")
        from_address = "18707362300@163.com"
        subject = "您的报表"
        body = "报表数据见附件."

        authorization_code = "OARXDNMAGYKTXXWD"

        server = smtplib.SMTP_SSL("smtp.163.com", 465)
        server.login(from_address, authorization_code)

        msg = MIMEMultipart()
        msg["From"] = from_address
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        for file in files_to_send:
            with open(file, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(file)}",
                )
                msg.attach(part)

        server.send_message(msg)
        server.quit()
        logging.info(f"邮件已成功发送到 {to_address}")
    except Exception as e:
        logging.info(f"发送邮件时出现错误: {e}")


def main():
    from datetime import datetime, timedelta

    db_manager = DatabaseManager(
        db_name="lichangfa_test",
        user="postgres",
        password="ai_tongue",
        host="172.18.0.3",
        port="5432",
    )

    logging.info("开始执行主程序...")
    qy_ids_and_emails = db_manager.get_qy_ids()

    if not qy_ids_and_emails:
        db_manager.close_connection()
        logging.info("无企业ID和邮件信息可用，程序提前退出")
        return

    today = datetime.today()
    day_of_week = today.weekday()
    day_of_month = today.day

    qy_ids = list(qy_ids_and_emails.keys())

    start_date = None
    end_date = None
    files_to_send = ["weekly.xlsx"]

    if day_of_month == 1:
        first_day_of_last_month = (today.replace(day=1) - timedelta(days=1)).replace(
            day=1
        )
        last_day_of_last_month = today.replace(day=1) - timedelta(days=1)
        start_date = first_day_of_last_month.strftime("%Y-%m-%d")
        end_date = last_day_of_last_month.strftime("%Y-%m-%d")
        files_to_send.append("Monthly report.xlsx")
    elif day_of_week == 0:
        first_day_of_last_week = today - timedelta(days=today.weekday() + 7)
        last_day_of_last_week = first_day_of_last_week + timedelta(days=6)
        start_date = first_day_of_last_week.strftime("%Y-%m-%d")
        end_date = last_day_of_last_week.strftime("%Y-%m-%d")
    else:
        logging.info("今天不是定期报告发送的日期")
        db_manager.close_connection()
        return

    data_frame_dict = db_manager.get_data_from_db(qy_ids, start_date, end_date)

    for qy_id, (data1, data2) in data_frame_dict.items():
        if data1 is not None and data2 is not None:
            save_data_to_xlsx(data1, data2)
            to_address = qy_ids_and_emails.get(qy_id, None)
            if to_address:
                send_email(to_address, files_to_send)
            else:
                logging.info(f"未找到企业 ID {qy_id} 的邮箱地址，跳过发送邮件。")

    db_manager.close_connection()
    logging.info("程序执行完成")


def clear_log_file(log_file_path):
    try:
        with open(log_file_path, "w") as file:
            file.truncate(0)
        logging.info("日志已成功清空")
    except Exception as e:
        logging.info(f"清空日志时出现错误: {e}")


if __name__ == "__main__":
    main()
    send_email("1438283270@qq.com", ["program_output.log"])
    clear_log_file("program_output.log")

