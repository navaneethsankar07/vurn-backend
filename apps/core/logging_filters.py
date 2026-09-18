import logging


class RequireErrorLevelFilter(logging.Filter):

    def filter(self, record):
        return record.levelno >= logging.ERROR
