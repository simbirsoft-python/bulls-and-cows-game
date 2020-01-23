from flask import g
from flask_wtf import FlaskForm as _FlaskForm
from wtforms.fields import (StringField, PasswordField)
from wtforms.validators import (
    DataRequired as _DataRequired, ValidationError, Length as _Length,
    Email as _Email
)

from models import User

MAPPING_MESSAGES = {
    'The CSRF token has expired.': (
        'Токен безопасности устарел, обновите страницу и попробуйте снова'
    )
}


class DataRequired(_DataRequired):
    def __init__(self):
        super().__init__(message='Поле не может остаться пустым.')


class Length(_Length):
    def __init__(self, min, max):
        super().__init__(
            min, max, f'Поле должно содержать от {min} до {max} символов.'
        )


class Email(_Email):
    def __init__(self):
        super().__init__(message='Неверный email адерс')


class FlaskForm(_FlaskForm):
    def validate(self):
        is_valid = super().validate()
        self.translate_csrf_token_field_messages()
        return is_valid

    def translate_csrf_token_field_messages(self):
        csrf_token_field = self._fields.get('csrf_token')
        if csrf_token_field is None:
            return

        for i, msg in enumerate(csrf_token_field.errors):
            translate = MAPPING_MESSAGES.get(msg)
            if translate is not None:
                self._fields['csrf_token'].errors[i] = translate


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        # после успешного прохождения проверки тут будет объект пользователя
        self.user = None

    def validate(self):
        is_valid = super().validate()
        if not is_valid:
            return False

        return self._email(self.email) and self._password(self.password)

    def _email(self, field):
        self.user = g.db_session.query(User).filter_by(email=field.data).first()

        if not self.user:
            field.errors.append(
                'Пользователь с таким email не зарегистрирован'
            )
            return False

        if not self.user.is_active:
            field.errors.append(
                'Аккаунт не активирован, необходимо активировать аккаунт '
                'перейдя по ссылке из письма'
            )
            return False

        return True

    def _password(self, field):
        if not self.user.check_password(field.data):
            field.errors.append('Введен неверный пароль')
            return False

        return True


class RegistrationForm(FlaskForm):
    nick = StringField(
        'Ник', validators=[DataRequired(), Length(min=3, max=30)]
    )
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField(
        'Пароль', validators=[DataRequired(), Length(min=6, max=10)]
    )
    password_verification = PasswordField(
        'Подтверждение пароля',
        validators=[DataRequired(), Length(min=6, max=10)]
    )

    def validate_email(self, field):
        self.user = g.db_session.query(User).filter_by(email=field.data).first()

        if self.user:
            raise ValidationError(
                'Пользователь стаким email уже зарегистрирован'
            )

        return True

    def validate_password(self, field):
        if self.password.data != self.password_verification.data:
            raise ValidationError('Введеные пароли не совпадают')

    def get_fields(self):
        return {
            'nick': self.nick.data,
            'email': self.email.data,
            'password': self.password.data
        }


class ResendConfirmationToken(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

    def validate_email(self, field):
        self.user = g.db_session.query(User).filter_by(email=field.data).first()

        if not self.user:
            raise ValidationError(
                'Пользователь стаким email еще не зарегистрирован'
            )
        elif self.user.is_active:
            raise ValidationError(
                'Данный аккаунт уже активирован'
            )

        return True

    def get_fields(self):
        return {
            'email': self.email.data,
        }


class PasswordRestoreForm(FlaskForm):
    email = StringField(
        'email', validators=[DataRequired(), Email()]
    )

    def validate_email(self, field):
        self.user = g.db_session.query(User).filter(
            User.email == field.data
        ).first()

        if not self.user:
            raise ValidationError('Пользователя с таким email не существует')

        if self.user.token_confirmation:
            raise ValidationError(
                'Письмо с ссылкой для восстановления пароля уже было отправлено'
            )


class NewPasswordForm(FlaskForm):
    password = PasswordField(
        'Пароль', validators=[DataRequired(), Length(min=6, max=10)]
    )
    password_verification = PasswordField(
        'Подтверждение пароля',
        validators=[DataRequired(), Length(min=6, max=10)]
    )

    def validate_password(self, field):
        if self.password.data != self.password_verification.data:
            raise ValidationError('Введеные пароли не совпадают')
