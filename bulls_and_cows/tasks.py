import logging

import dependency_injector.containers as di_cnt
import dependency_injector.providers as di_prv
from flask_mail import Message

from utils.dramatiq_utils import lazy_actor


class DIServices(di_cnt.DeclarativeContainer):
    mail = di_prv.Provider()


@lazy_actor(
    queue_name='notification-tasks', max_retries=3, min_backoff=30000,
    time_limit=60000
)
def send_verification_email(url: str, email: str, action: str):
    subject_template = 'Быки и Коровы {}'
    subject_postfix = ''
    body = ''
    if action == 'registration':
        subject_postfix = ' - Регистрация'
        body = 'Для подтверждения регистрации перейдите по ссылке ' + url
    elif action == 'password_restore':
        subject_postfix = ' - Восстановление пароля'
        body = 'Для восстановления пароля перейдите по ссылке ' + url

    msg = Message(
        subject=subject_template.format(subject_postfix), recipients=[email]
    )

    if body:
        msg.body = body
        logging.getLogger().debug(body)
        try:
            DIServices.mail().send(msg)
        except Exception:
            logging.getLogger().exception(
                f'Вознишла ошибка при отправке email="{email}"'
            )
