import logging
import sys
FORMATTER = logging.Formatter("%(asctime)s - %(pathname)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s")

class LoggerFactory:

    @staticmethod
    def get_logger(logger_name):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.addHandler(LoggerFactory.__get_console_handler())
        return logger

    @staticmethod
    def __get_console_handler():
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(FORMATTER)
        return console_handler

def main(logger):
    logger.info("This is an info message")

if __name__ == "__main__":
    logger = LoggerFactory.get_logger("logger")
    main(logger)