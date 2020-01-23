import logging
import re
from datetime import datetime
from urllib.parse import urljoin

from flask import (
    g, jsonify, request, render_template, redirect, url_for, session
)
from flask_classy import FlaskView, route
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import Float, REAL, func, cast, distinct, desc
from sqlalchemy.sql import label

from bulls_and_cows.forms import (
    RegistrationForm, LoginForm, PasswordRestoreForm, NewPasswordForm,
    ResendConfirmationToken
)
from bulls_and_cows.game_core import generate_secret, count_bulls_cows
from bulls_and_cows.tasks import send_verification_email
from bulls_and_cows.utils.account import (
    email_from_token, activate_user, add_new_user, set_new_password,
    add_token, generate_token
)
from bulls_and_cows.utils.url import redirect_back
from models import User, Game, Move
from models.user import EmailNotify


class AccountView(FlaskView):
    """
    Класс представляющий views для работы с аккаунтом пользователя
    """
    TOKEN_LIFETIME = 60
    REDIRECT_BACK_ARGUMENT = 'next'

    def before_verify_email(self, token):
        email = email_from_token(token)

        g.db_data['email'] = email
        g.db_data['user'] = g.db_session.query(User).filter(
            User.email == email
        ).first()

    def before_reset_password(self, token=None):
        email = email_from_token(token)
        g.db_data['user'] = g.db_session.query(User).filter(
            User.email == email
        ).first()

    def verify_email(self, token):
        email = g.db_data['email']
        user = g.db_data['user']

        if email and user and user.token_confirmation is None and user.is_active:
            return redirect(url_for('bulls_and_cows.AccountView:login'))

        if email and user and user.token_confirmation.token == token:
            is_success = activate_user(email)
            if not is_success:
                return render_template(
                    'verify_email.html',
                    message=(
                        'Во время активации аккаунта возникли неприведнные '
                        'проблемы.'
                    )
                )
            return redirect(url_for('bulls_and_cows.AccountView:login'))
        else:
            return render_template(
                'verify_email.html',
                message=(
                    'Вы использовали невалидную ссылку для подтверждения '
                    'аккаунта.'
                )
            )

    @route('/login/', methods=['GET', 'POST'])
    def login(self):
        if current_user.is_authenticated:
            return redirect(
                url_for('bulls_and_cows.BullsAndCowsView:index')
            )

        form = LoginForm()
        if request.method == 'POST' and form.validate_on_submit():
            login_user(form.user)
            return redirect_back(
                self.REDIRECT_BACK_ARGUMENT,
                'bulls_and_cows.BullsAndCowsView:index'
            )
        else:
            return render_template('auth.html', form=form, user=current_user)

    @route('/registration/', methods=['GET', 'POST'])
    def registration(self):
        if current_user.is_authenticated:
            return redirect(
                url_for('bulls_and_cows.BullsAndCowsView:index')
            )

        form = RegistrationForm()

        if request.method == 'POST' and form.validate_on_submit():
            token = generate_token(form.email.data)
            is_success = add_new_user(form, token)

            if not is_success:
                return render_template(
                    'registration.html', form=form, is_success=is_success
                )

            send_verification_email.send(
                urljoin(
                    request.host_url,
                    url_for('bulls_and_cows.AccountView:verify_email',
                            token=token)
                ),
                form.email.data, 'registration'
            )
            return render_template(
                'registration.html', form=form, is_success=True, reg_done=True
            )
        else:
            return render_template(
                'registration.html', form=form, is_success=True
            )

    @route('/resend_confirmation_token/', methods=['GET', 'POST'])
    def resend_confirmation_token(self):
        form = ResendConfirmationToken()

        if request.method == 'POST' and form.validate_on_submit():
            if not form.user.token_confirmation:
                token = generate_token(form.email.data)
            else:
                token = form.user.token_confirmation.token

            is_success = add_token(form.user.id, token)
            if not is_success:
                return render_template(
                    'resend_confirmation_token.html', form=form,
                    error_massage=(
                        'При попытке отправить письмо возникла ошибка'
                    )
                )

            send_verification_email.send(
                urljoin(
                    request.host_url,
                    url_for('bulls_and_cows.AccountView:verify_email',
                            token=token)
                ),
                form.email.data, 'registration'
            )
            return render_template(
                'resend_confirmation_token.html', form=form,
                message=('Письмо с ссылкой для активации аккаунта отправлена '
                         'на указанную почту')
            )
        else:
            return render_template('resend_confirmation_token.html', form=form)

    @route('/password_restore/', methods=['GET', 'POST'])
    def password_restore(self):
        """
        Принимает от пользователя email и отправляет на него сообщение с
        ссылкой для смены пароля
        """
        form = PasswordRestoreForm()

        if request.method == 'POST' and form.validate_on_submit():
            token = generate_token(form.user.email)
            try:
                email_notify = EmailNotify(id_user=form.user.id, token=token)
                g.db_session.add(email_notify)
                g.db_session.commit()
            except Exception:
                g.db_session.rollback()
                logging.getLogger().exception(
                    f'Возникла непредвиденная ошибка при попытке '
                    f'сохранить токен используемый для сброса пароля у  '
                    f'пользователя email={form.email}'
                )
                return render_template(
                    'password_restore.html', form=form,
                    error_massage=(
                        'Во время восстановления пароля возникли неприведнные '
                        'проблемы.'
                    )
                )
            else:
                send_verification_email.send(
                    urljoin(
                        request.host_url,
                        url_for('bulls_and_cows.AccountView:reset_password',
                                token=token)
                    ),
                    form.user.email, 'password_restore'
                )
                return render_template(
                    'password_restore.html', form=form,
                    message=(
                        'Вам на почту было выслано письмо с дальнейшими '
                        'инструкциями.'
                    )
                )
        else:
            return render_template('password_restore.html', form=form)

    @route('/reset_password/<token>/', methods=['GET', 'POST'])
    def reset_password(self, token=None):
        """
        Проверяет токен и отображает страницу на которой пользователь может
        задать новый пароль
        """
        form = NewPasswordForm()
        email = email_from_token(token)
        user = g.db_data['user']

        if email and user and user.token_confirmation is None:
            return redirect(url_for('bulls_and_cows.AccountView:login'))

        if not (email and user and user.token_confirmation.token == token):
            return render_template(
                'reset_password.html', token=token, form=form,
                error_massage=(
                    'Вы использовали невалидную ссылку для сброса пароля.'
                )
            )

        if request.method == 'POST' and form.validate_on_submit():
            new_password = form.password.data
            is_success = set_new_password(email, new_password)
            if is_success:
                return redirect(
                    url_for('bulls_and_cows.AccountView:login')
                )
            else:
                return render_template(
                    'reset_password.html', token=token, form=form,
                    error_massage=(
                        'При попытке изменить пароль возникли неприведнные '
                        'проблемы.'
                    )
                )
        else:
            return render_template(
                'reset_password.html', token=token, form=form
            )

    @login_required
    def logout(self):
        logout_user()
        return redirect(url_for('bulls_and_cows.AccountView:login'))


class BullsAndCowsView(FlaskView):
    """
    Класс представляющий views для реализации игры "Быки и коровы"
    """
    decorators = [login_required]

    @classmethod
    def create_game(cls):
        secret = generate_secret()

        game = Game(
            id_user=current_user.id, secret=secret, date=datetime.now()
        )
        g.db_session.add(game)

        session['secret'] = secret

        try:
            g.db_session.commit()
            session['id_game'] = game.id
            return True
        except Exception:
            logging.getLogger().exception(
                f'Ошибка создания записи об игре '
                f'user_id={current_user.id}, email={current_user.email}'
            )
            g.db_session.rollback()
            return False

    @classmethod
    def add_move(cls, answer, completed):
        id_game = session.get('id_game', '')
        if not id_game:
            logging.getLogger().exception(
                f'Отсуствует id_game, похоже при старте игры база была не '
                f'доступна user_id={current_user.id}, '
                f'email={current_user.email}'
            )
            return True

        if completed:
            game = g.db_session.query(Game).filter_by(
                id=session.get('id_game', '')
            ).first()
            game.completed = True
            g.db_session.add(game)

        move = Move(id_game=session.get('id_game', ''), answer=answer)
        g.db_session.add(move)

        try:
            g.db_session.commit()
            return True
        except Exception:
            logging.getLogger().exception(
                f'Ошибка создания записи о ходе '
                f'user_id={current_user.id}, email={current_user.email}'
            )
            g.db_session.rollback()
            return False

    @classmethod
    def search_unfinished_game(cls):
        game = g.db_session.query(Game).filter_by(
            id_user=current_user.id, completed=False
        ).first()

        if game:
            session['secret'] = game.secret
            session['id_game'] = game.id

        return game

    def before_check_answer(self):
        answer = request.args.get('answer', '')
        if len(set(answer)) != 4 or len(answer) != 4:
            return jsonify(
                answer_error='Вы должны ввести четрех значное число '
                             '(цифры не должны повторяться)'
            )

        if not re.match('\\d{4}', answer):
            return jsonify(
                answer_error='Вы должны ввести четырех значное число.'
            )

        g.db_data['answer'] = answer

    def before_rating(self):
        g.db_data['rating'] = g.db_session.query(
            User.email,
            label(
                'rating',
                cast(
                    (1 / (cast(func.count(Move.id_game), REAL) /
                          cast(func.count(distinct(Game.id)), REAL))) * 10,
                    Float
                )
            )
        ).join(
            Game, Game.id_user == User.id
        ).join(
            Move, Game.id == Move.id_game
        ).group_by(
            User.email
        ).filter(
            Game.completed == True
        ).order_by(
            desc('rating')
        ).all()

    def index(self):
        unfinished_game = self.search_unfinished_game()

        is_success = True
        if not unfinished_game:
            is_success = self.create_game()

        return render_template('game.html', unfinished_game=unfinished_game,
                               count_bulls_cows=count_bulls_cows,
                               is_success=is_success, game_active='active')

    def new_game(self):
        is_success = self.create_game()
        return jsonify({'status': 'success' if is_success else 'error'})

    def check_answer(self):
        answer = g.db_data['answer']
        bulls, cows = count_bulls_cows(session['secret'], answer)
        completed = True if bulls == 4 else False
        is_success = self.add_move(answer, completed)
        return jsonify(
            bulls=bulls, cows=cows, status='success' if is_success else 'error'
        )

    def rating(self):
        return render_template(
            'rating.html', rating=g.db_data['rating'], rating_active='active'
        )
