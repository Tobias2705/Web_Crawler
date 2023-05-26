import logging

class CustomFormatter(logging.Formatter):

    format = "[%(levelname)s] %(asctime)s - %(message)s"

    FORMATS = {
        logging.INFO: format,
        logging.ERROR: format,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def get_logger():
    logger = logging.getLogger("web_crawler")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())
    if not logger.hasHandlers():
        logger.addHandler(ch)

    return logger
