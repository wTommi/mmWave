from __future__ import annotations
import logging

class CustomFormatter(logging.Formatter):
    normal = '\x1b[20;1m'
    white = '\x1b[49;1m'
    green = '\x1b[32;1m'
    yellow = '\x1b[33;1m'
    Magenta = '\x1b[35;1m'
    red = '\x1b[31;1m'
    reset = '\x1b[0m'
    def __init__(self, fmt="%(asctime)s | %(name)-10s| %(levelname)-8s|: %(message)s"):
        super().__init__(fmt)
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: f"{self.green} {self.fmt} {self.reset}",
            logging.INFO: f"{self.white} {self.fmt} {self.reset}",
            logging.WARNING: f"{self.yellow} {self.fmt} {self.reset}",
            logging.ERROR: f"{self.Magenta} {self.fmt} {self.reset}",
            logging.CRITICAL: f"{self.red} {self.fmt} {self.reset}"
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


formatter = CustomFormatter()
log_file = '{}.log'.format('Blind_Test')  # log filename
LOGGERS = {}
def get_logger(name:str='KKT_Mod', level:int=logging.INFO)->logging.Logger:
    if LOGGERS.get(name):
        logger = LOGGERS.get(name)
    else:
        logger = logging.getLogger(name)
        LOGGERS[name] = logger
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def enableFileHandler(logger:logging.Logger, enable=True, file_name=log_file, level=logging.INFO):
    handlers = logger.handlers
    for handler in handlers:
        if type(handler) == logging.FileHandler:
            handlers.remove(handler)

    if enable:
        file_handler = logging.FileHandler(file_name, 'w', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    return

def saveFileHandler(logger:logging.Logger):
    handlers = logger.handlers
    for handler in handlers:
        if type(handler) == logging.FileHandler:
            handler.close()
    pass

