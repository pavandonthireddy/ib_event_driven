import logging

existing_logger_name = None


logFormatter = logging.Formatter("%(asctime)s - [%(levelname)-5.5s] - [%(name)s]"
                                 " - [%(funcName)s:%(lineno)4d] - [%(message)s]")


def set_logger_name(logger_name):
    global existing_logger_name

    if existing_logger_name is not None:
        if logger_name == existing_logger_name:
            raise Exception(f'Logger {existing_logger_name} already exists')

    directory = './logs'

    logger = logging.getLogger()
    logger.handlers = []

    file_handler = logging.FileHandler("{0}/{1}.log".format(directory, logger_name))
    file_handler.setFormatter(logFormatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logFormatter)
    logger.addHandler(console_handler)
    logger.setLevel('INFO')

    logging.info(f"** LOGGER SET TO {logger_name}")

    existing_logger_name = logger_name
