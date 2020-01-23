import logging
import os

from alembic.config import main as alembic_commands


def root_logger_cleaner():
    """
    Сбрасывает root логгер к настройкам, которые были у root логгера при
    инициализации коррутины
    """
    root = logging.getLogger()
    default_settings = {
        'level': root.level,
        'disabled': root.disabled,
        'propagate': root.propagate,
        'filters': root.filters[:],
        'handlers': root.handlers[:],
    }
    yield

    while True:
        for attr, attr_value in default_settings.items():
            setattr(root, attr, attr_value)
        yield


def apply_migrations(root_dir):
    """
    Применяет к текущей БД все миграции
    :param root_dir: корневая дирректория проекта (дирректория в которой
    располагается папка alembic, содержащая миграции)
    """
    cwd = os.getcwd()
    os.chdir(root_dir)
    logger_cleaner = root_logger_cleaner()
    next(logger_cleaner)

    try:
        alembic_commands(argv=('--raiseerr', 'upgrade', 'head',))
    except Exception as err:
        next(logger_cleaner)
        logging.getLogger('serial-notifier').error(
            f'Возникла ошибка при попытке применить миграции: {err}'
        )
        raise
    finally:
        os.chdir(cwd)

    next(logger_cleaner)
