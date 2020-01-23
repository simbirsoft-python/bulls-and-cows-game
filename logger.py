import logging

logging_level_for_modules = (
    ('pika', 'WARNING'),
    ('dramatiq', 'INFO'),
    ('watchdog.observers.inotify_buffer', 'INFO'),
)


def set_specific_logging_level():
    """
    Настраивает уровень логгирования у модулей, которые в лог пишут много не
    нужной информации
    :return:
    """
    for module, level in logging_level_for_modules:
        logging.getLogger(module).setLevel(level)


def init_logger(level: str):
    log = logging.getLogger()
    log.setLevel(level)

    console_formatter = logging.Formatter(
        '#%(levelname)-s, %(pathname)s, line %(lineno)d: %(message)s'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    log.addHandler(console_handler)

    set_specific_logging_level()

