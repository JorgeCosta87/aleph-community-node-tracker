from datetime import datetime

class Utils:
    @staticmethod
    def convert_unix_to_datetime(unix_timestamp):
        dt_object = datetime.fromtimestamp(unix_timestamp)
        return dt_object.strftime("%d-%m-%Y %H:%M:%S")