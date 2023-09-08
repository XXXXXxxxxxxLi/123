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
import datetime
import argparse

logging.basicConfig(
    filename="program_output.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
)


class DatabaseManager:
    def __init__(self, db_name, user, password, host, port):
        self.conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port,
        )
        self.periods = {"this_week", "this_month", "last_week", "last_month"}
        self.intake_vars = [
            "id",
            "create_time",
            "equipment_id",
            "user_id",
            "tongue_shape",
            "tongue_color",
            "tongue_bot",
            "body_fluid",
            "liverwort",
            "moss_color",
            "pdf",
            "choroid",
            "syndrome",
            "remarks",
        ]

    def get_inspect_data(self, date_start, date_end, all_columns=False):
        if not all_columns:
            vars_str = ", ".join(self.intake_vars)
            query = f"""
                SELECT {vars_str}
                FROM whir_inspect
                WHERE create_time BETWEEN \'{date_start}\' AND \'{date_end}\'
            """
        else:
            query = f"""
                SELECT *
                FROM whir_inspect
                WHERE create_time BETWEEN \'{date_start}\' AND \'{date_end}\'
            """
        dt = pd.read_sql(query, self.conn)
        new_names = {
            k: v for k, v in column_translations.items() if k in dt.columns.values
        }
        dt = dt.rename(columns=new_names)
        dt["report_p"] = ["已出报告" if i is not None else "未出报告" for i in dt["报告"]]
        return dt

    def get_equ_qy_data(self, equ_ids=None):
        if equ_ids is not None:
            equ_ids_str = "'" + "','".join(equ_ids) + "'"
            query = f"""
                SELECT q.id AS "企业ID", q.email AS "企业邮箱", q.name AS "企业名称", e.equipment_id AS "设备ID", e.alias AS "设备别名"
                FROM whir_equipment e
                LEFT JOIN whir_qy_archives q
                ON e.qy_id = q.id
                WHERE e.equipment_id IN ({equ_ids_str})
            """
        else:
            query = f"""
                SELECT q.id AS "企业ID", q.email AS "企业邮箱", q.name AS "企业名称", e.equipment_id AS "设备ID", e.alias AS "设备别名"
                FROM whir_equipment e
                LEFT JOIN whir_qy_archives q
                ON e.qy_id = q.id
            """
        dt = pd.read_sql(query, self.conn)
        return dt

    def get_data(self, date_start, date_end, all_columns=False):
        inspect_data = self.get_inspect_data(date_start, date_end, all_columns)
        equ_ids = inspect_data["设备ID"].unique()
        equ_qy_data = self.get_equ_qy_data(equ_ids)
        detail_data = pd.merge(equ_qy_data, inspect_data, on="设备ID", how="right")
        print(detail_data.keys())
        freq_data = (
            detail_data.groupby(["企业ID", "企业名称", "企业邮箱"])
            .apply(
                lambda x: x.pivot_table(
                    index=["设备ID", "设备别名"],
                    columns="report_p",
                    values="报告ID",
                    aggfunc="count",
                    fill_value=0,
                    margins=True,
                    margins_name="合计",
                )
            )
            .drop(["未出报告"], axis=1)
            .rename(columns={"合计": "检查数量"})
            .reset_index()
        )
        dt = {"detail": detail_data, "freq": freq_data}
        return dt

    def organize(self, detail_data, freq_data):
        company_ids = freq_data["企业ID"].unique()
        detail_data_group = detail_data.groupby(["企业ID"])
        freq_data_group = freq_data.groupby(["企业ID"])
        company_vars = ["企业ID", "企业名称", "企业邮箱"]
        output = [
            {
                "company_id": i,
                "company_name": freq_data_group.get_group(i)["企业名称"].iloc[0],
                "email": freq_data_group.get_group(i)["企业邮箱"].iloc[0],
                "freq": freq_data_group.get_group(i).drop(company_vars, axis=1),
                "detail": detail_data_group.get_group(i).drop(company_vars, axis=1),
            }
            for i in company_ids
        ]
        return output

    def this_week(self):
        now = datetime.date.today()
        date_end = datetime.date.today()
        date_start = now - datetime.timedelta(date_end.weekday())
        return date_start, date_end

    def this_month(self):
        date_end = datetime.date.today()
        date_start = date_end - datetime.timedelta(date_end.day - 1)
        return date_start, date_end

    def last_week(self):
        now = datetime.date.today()
        start_of_week = now - datetime.timedelta(days=now.weekday())
        date_end = start_of_week - datetime.timedelta(days=1)  # 上周的最后一天（周日）
        date_start = date_end - datetime.timedelta(days=6)  # 上周的第一天（周一）
        return date_start, date_end

    def last_month(self):
        now = datetime.date.today()
        first_day_of_current_month = now.replace(day=1)
        last_day_of_last_month = first_day_of_current_month - datetime.timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        date_start = first_day_of_last_month
        date_end = last_day_of_last_month
        return date_start, date_end

    def get_period_data(self, period: str):
        assert period in self.periods, f"period must be one of {str(self.periods)}"
        date_start, date_end = [i.strftime("%Y-%m-%d") for i in getattr(self, period)()]
        dt = self.get_data(date_start, date_end, all_columns=False)
        return dt


def save_data_to_xlsx(data1, data2):
    try:
        logging.info("开始保存数据到xlsx文件...")
        if data1 is not None and data2 is not None:
            with pd.ExcelWriter("report1.xlsx") as writer:
                data1.to_excel(writer, sheet_name="Enterprise Data")
            with pd.ExcelWriter("report2.xlsx") as writer:
                data2.to_excel(writer, sheet_name="Frequency Data")
            logging.info("数据已成功保存到xlsx文件")
        else:
            logging.info("没有数据可以保存")
    except Exception as e:
        logging.info(f"保存数据到xlsx文件时出现错误: {e}")


class Mail:
    def __init__(self, from_address, authorization_code, smtp_server, smtp_port):
        self.from_address = from_address
        self.authorization_code = authorization_code
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(self, to_address, files_to_send):
        try:
            for file in files_to_send:
                if not os.path.exists(file):
                    raise FileNotFoundError(f"Output file '{file}' not found.")

            logging.info(f"开始发送邮件到 {to_address}...")
            subject = "您的报表"
            body = "报表数据见附件."

            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.from_address, self.authorization_code)

            msg = MIMEMultipart()
            msg["From"] = self.from_address
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
    parser = argparse.ArgumentParser(description="Send weekly or monthly reports.")
    parser.add_argument('report_type', type=str, choices=['weekly', 'monthly'],
                        help="Type of report to send ('weekly' or 'monthly').")

    args = parser.parse_args()

    db_manager = DatabaseManager(
        db_name="lichangfa_test",
        user="postgres",
        password="ai_tongue",
        host="172.18.0.3",
        port="5432",
    )

    mail_manager = Mail(
        from_address="18707362300@163.com",
        authorization_code="OARXDNMAGYKTXXWD",
        smtp_server="smtp.163.com",
        smtp_port=465,
    )

    logging.info("开始执行主程序...")

    if args.report_type == 'monthly':
        logging.info("生成月报...")

        monthly_data = db_manager.get_period_data("last_month")
        save_data_to_xlsx(monthly_data["detail"], monthly_data["freq"])

        data_frames = db_manager.organize(monthly_data["detail"], monthly_data["freq"])

    elif args.report_type == 'weekly':
        logging.info("生成周报...")

        weekly_data = db_manager.get_period_data("last_week")
        save_data_to_xlsx(weekly_data["detail"], weekly_data["freq"])

        data_frames = db_manager.organize(weekly_data["detail"], weekly_data["freq"])

    else:
        logging.info("无效的报告类型")
        return

    for data_frame in data_frames:
        to_address = data_frame.get("email", None)
        if to_address:
            # 生成唯一的文件名
            file_prefix = f"report_{data_frame['company_id']}"
            detail_file = f"{file_prefix}_detail.xlsx"
            freq_file = f"{file_prefix}_freq.xlsx"

            # 保存各自企业的数据到唯一的文件中
            data_frame["detail"].to_excel(detail_file, sheet_name="Enterprise Data")
            data_frame["freq"].to_excel(freq_file, sheet_name="Frequency Data")

            # 发送邮件
            if args.report_type == 'weekly':
                mail_manager.send_email(to_address, [freq_file])
            else:
                mail_manager.send_email(to_address, [detail_file, freq_file])

            # 删除创建的文件
            os.remove(detail_file)
            os.remove(freq_file)
        else:
            logging.info(f"未找到企业 ID {data_frame['company_id']} 的邮箱地址，跳过发送邮件。")

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
    mail_manager = Mail(
        from_address="18707362300@163.com",
        authorization_code="",
        smtp_server="smtp.163.com",
        smtp_port=465,
    )
    mail_manager.send_email("1438283270@qq.com", ["program_output.log"])
    clear_log_file("program_output.log")
