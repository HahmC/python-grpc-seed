import logging
import socket
from context_vars import correlation_id

class Logger(logging.LoggerAdapter):
    """
    Custom LoggerAdapter to inject extra context into log messages
    """
    def __init__(self, config, correlation_id):
        extra = {
            'server_name': socket.gethostname()
        }
        super().__init__(self.__get_logger(config), extra)

    # def process(self, msg: str, kwargs: dict):
    #     """
    #     Process the logging message and kwargs to inject the correlation_id
    #     """
    #     if 'extra' not in kwargs:
    #         kwargs['extra'] = {}
    #     kwargs['extra']['correlation_id'] = correlation_id.get()
    #     return msg, kwargs

    def __get_logger(self, config):
        """
        Returns a logger configured to the specifications of the config.ini file

        Date Format: %Y-%m-%d %H:%M:%S
        """
        logger = logging.getLogger(config['logging']['logger_name'])
        logger.setLevel(config['logging']['level'].upper())
        formatter = self.CorrelationIdFormatter(
            config['logging']['format'],
            datefmt="%Y-%m-%d %H:%M:%S",
            style='{'
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(config['logging']['level'].upper())
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addFilter(self.CorrelationIdFilter())

        return logger

    class CorrelationIdFormatter(logging.Formatter):
        """
        Custom Log Formatter to handle the correlation_id if it is present
        """
        def format(self, record):
            # Ensure correlation_id is always present
            if not hasattr(record, 'correlation_id') or record.correlation_id is None:
                record.correlation_id = ''
            return super().format(record)

    # Custom logger filter to add correlation ID to log records
    class CorrelationIdFilter(logging.Filter):
        """
        Custom log formatter to retrieve the correlation_id if it is present
        """
        def filter(self, record):
            test = correlation_id.get()
            record.correlation_id = correlation_id.get()
            return True