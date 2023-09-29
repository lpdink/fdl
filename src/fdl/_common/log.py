import logging as FatherLog
import os

COLOR_DIC = {
    "ERROR": "31",
    "INFO": "37",
    "DEBUG": "32",
    "WARN": "33",
    "WARNING": "33",
    "CRITICAL": "35",
}


class ColorFormatter(FatherLog.Formatter):
    def __init__(self, fmt, use_color=False) -> None:
        super().__init__(fmt)
        self.use_color = use_color

    def format(self, record) -> str:
        color = COLOR_DIC[record.levelname]
        return (
            f"\033[{color}m{super().format(record)}\033[0m"
            if self.use_color
            else super().format(record)
        )


class Logger(FatherLog.Logger):
    instance = None
    init = False

    def __new__(cls):
        if Logger.instance is None:
            Logger.instance = super().__new__(cls)
        return Logger.instance

    def __init__(self) -> None:
        if Logger.init:
            return
        super().__init__("logger", 0)
        self.fmt = "[%(asctime)s %(levelname)s %(pathname)s:%(lineno)d] %(message)s"
        stream_handler = FatherLog.StreamHandler()
        color_formater = ColorFormatter(self.fmt, True)
        stream_handler.setFormatter(color_formater)
        stream_handler.setLevel(FatherLog.INFO)
        self.addHandler(stream_handler)
        Logger.init = True

    def set_log_path(self, log_folder, log_file_name="log.txt"):
        """设置日志文件的保存位置，将保存在log_folder/log.txt下

        Args:
            log_folder (str): 日志文件的保存路径
        """
        self.log_folder = log_folder
        if not os.path.isdir(log_folder):
            os.makedirs(log_folder)
        # now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        log_file_path = os.path.join(log_folder, log_file_name)
        file_handler = FatherLog.FileHandler(log_file_path, encoding="utf-8")
        file_format = FatherLog.Formatter(self.fmt)
        file_handler.setFormatter(file_format)
        file_handler.setLevel(FatherLog.DEBUG)
        self.addHandler(file_handler)

    def get_work_dir(self):
        return self.log_folder
