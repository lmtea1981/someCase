import os
import logging
import threading
import configparser
import time
from logging.handlers import TimedRotatingFileHandler

# 项目根目录
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 日志配置文件
conf_log_path = os.path.join(path, 'pytest.ini')

class LogSingleton:
    _lock = threading.Lock()

    def __new__(cls, config_path: str):
        with cls._lock:
            if not hasattr(cls, 'instance'):
                cls.instance = super().__new__(cls)
                cls.instance._init_from_config(config_path)
            return cls.instance

    def _init_from_config(self, config_path: str):
        cfg = configparser.ConfigParser()
        read = cfg.read(config_path, encoding='utf-8')
        if not read:
            raise FileNotFoundError(f"Logging config not found: {config_path}")

        sec = cfg['LOGGING']
        raw      = sec.get('log_file')                  # "/logs/log.log"
        # 去掉开头的斜杠或反斜杠
        rel_path = raw.lstrip('/\\')                    # "logs/log.log"
        dir_part = os.path.dirname(rel_path)            # "logs"
        base_name= os.path.basename(rel_path)           # "log.log"

        self.log_dir   = os.path.join(path, dir_part)   # "{project}/logs"
        self.base_name = base_name                      # "log.log"
        self.backup    = sec.getint('backup_count')
        self.console_on= sec.getint('console_log_on')==1
        self.file_on   = sec.getint('logfile_log_on')==1
        self.c_lvl     = sec.getint('log_level_in_console')
        self.f_lvl     = sec.getint('log_level_in_logfile')
        self.fmt       = sec.get('fmt').replace('|','%')
        self.name      = sec.get('logger_name')

        self.logger = logging.getLogger(self.name)
        self._config_handlers()

    def _config_handlers(self):
        fmt = logging.Formatter(self.fmt)
        # self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        # 控制台
        if self.console_on:
            ch = logging.StreamHandler()
            ch.setLevel(self.c_lvl)
            ch.setFormatter(fmt)
            self.logger.addHandler(ch)

        # 文件（按天滚动）
        if self.file_on:
            # 1) 确保目录存在
            os.makedirs(self.log_dir, exist_ok=True)
            # 2) 带日期后缀
            dated = f"{self.base_name}_{time.strftime('%Y-%m-%d')}"
            full  = os.path.join(self.log_dir, dated)
            # 3) touch 文件
            open(full, 'a', encoding='utf-8').close()

            fh = TimedRotatingFileHandler(
                filename=full,
                when='D',
                interval=1,
                backupCount=self.backup,
                encoding='utf-8'
            )
            fh.setLevel(self.f_lvl)
            fh.setFormatter(fmt)
            self.logger.addHandler(fh)

    def get_logger(self) -> logging.Logger:
        return self.logger

# 单例实例化
logsingleton = LogSingleton(conf_log_path)
logger = logsingleton.get_logger()
