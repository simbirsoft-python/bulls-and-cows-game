import logging
import time

import dependency_injector.containers as di_cnt
import dependency_injector.providers as di_prv
import itsdangerous
from flask import g

import config
from bulls_and_cows.forms import RegistrationForm
from models import User
from models.user import EmailNotify


conf = config.get_config()


class DIServices(di_cnt.DeclarativeContainer):
    mail = di_prv.Provider()
    url_serializer = di_prv.Provider()


def generate_token(email: str):
    return DIServices.url_serializer().dumps(
        f'{email},{time.strftime("%c")}', salt=conf.ACTIVATION_SALT
    )


def email_from_token(token):
    try:
        serializer = DIServices.url_serializer()
        email = serializer.loads(
            token, salt=conf.ACTIVATION_SALT
        ).split(',')[0]
    except (itsdangerous.BadSignature, IndexError):
        return None
    else:
        return email


def add_new_user(form: RegistrationForm, token: str):
    try:
        email_notify = EmailNotify(token=token)
        user = User(**form.get_fields())
        # Sa позволяет создавать отновшения до того, как primary key будет
        # ивестен
        user.token_confirmation = email_notify

        g.db_session.add(user)
        g.db_session.add(email_notify)

        g.db_session.commit()
        return True
    except Exception:
        logging.getLogger().exception(
            f'Ошибка при создании нового пользователя c email: '
            f'{form.email.data}'
        )
        g.db_session.rollback()
        return False


def add_token(id_user: int, token: str):
    try:
        email_notify = EmailNotify(id_user=id_user, token=token)
        g.db_session.add(email_notify)
        g.db_session.commit()
        return True
    except Exception:
        logging.getLogger().exception(
            f'Ошибка при записи в БД токена для пользователя с id: {id_user}'
        )
        g.db_session.rollback()
        return False


def activate_user(email):
    """
    Активирует выбранного пользователя и удаляет из базы токен для
    сброса/подтвержедния пароля
    :param email логин пользователя
    """
    try:
        user = g.db_session.query(User).filter(
            User.email == email
        ).first()
        user.is_active = True
        g.db_session.delete(user.token_confirmation)
        g.db_session.add(user)
        g.db_session.commit()
        return True
    except Exception:
        logging.getLogger().exception(
            f'Ошибка при активации аккаунта email: {email}'
        )
        g.db_session.rollback()
        return False


def set_new_password(email, new_password):
    try:
        user = g.db_session.query(User).filter(User.email == email).first()
        user.password = new_password
        g.db_session.delete(user.token_confirmation)
        g.db_session.add(user)
        g.db_session.commit()
        return True
    except Exception:
        logging.getLogger().exception(
            f'Возникла ошибка при попытке сменить пароль у пользователя'
            f'с email={email}'
        )
        g.db_session.rollback()
        return False
