import logging


class CustomFormatter(logging.Formatter):
    """Custom formatter class used to convert a logging.LogRecord instance to a text.
    """

    format = "[%(levelname)s]\t%(asctime)s\t%(message)s"

    FORMATS = {
        logging.INFO: format,
        logging.ERROR: format,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Formats the record as a text.

        :param record: An instance of logging.LogRecord to be formatted as a text
        :type record: logging.LogRecord
        :return: Formatted str object made of logging.LogRecord object
        :rtype: str
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger() -> logging.Logger:
    """Creates common logging.Logger instance for the whole application.

    :return: Instance of logging.Logger
    :rtype: logging.Logger
    """
    logger = logging.getLogger("web_crawler")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())
    if not logger.hasHandlers():
        logger.addHandler(ch)

    return logger
