import logging

__all__ = ['lib_logger']

lib_logger = logging.getLogger(name='Lib')
lib_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()

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

handler.setFormatter(CustomFormatter())
lib_logger.addHandler(handler)



