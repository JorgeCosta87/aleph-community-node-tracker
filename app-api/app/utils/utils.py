from datetime import datetime
import smtplib

class Utils:
    @staticmethod
    def convert_unix_to_datetime(unix_timestamp):
        dt_object = datetime.fromtimestamp(unix_timestamp)
        return dt_object.strftime("%d-%m-%Y %H:%M:%S")
    
    @staticmethod
    def send_email(
            email_to: str,
            email_subject:str,
            email_body: str
        ):
        sender_email = "aleph.community.node.tracker@gmail.com"
        sender_password = "ejzh rreu wkyt fgqi"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email_to, f"Subject: {email_subject}\n\n{email_body}")
