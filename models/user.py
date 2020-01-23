import datetime

import bcrypt

from sqlalchemy import Column, Unicode, Integer, Boolean, ForeignKey, Enum, \
    DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from models.base import Base


class User(Base):
    id = Column(Integer, primary_key=True)
    nick = Column(Unicode(length=30))
    email = Column(Unicode(length=40), unique=True, nullable=False)
    _password = Column('password', Unicode(length=60))
    is_active = Column(
        Boolean, server_default=expression.false(), default=False,
        nullable=False
    )
    reg_date = Column(DateTime(), default=datetime.datetime.now())

    token_confirmation = relationship(
        'EmailNotify', uselist=False, passive_deletes=True
    )
    games = relationship("Game")

    def to_json(self):
        return {
            'id': self.id,
            'nick': self.nick,
            'email': self.email,
            'is_active': self.is_active
        }

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password: str):
        self._password = self.generate_password(raw_password)

    @staticmethod
    def generate_password(raw_password: str):
        return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, inp_passwd: str):
        return bcrypt.checkpw(inp_passwd.encode(), self.password.encode())

    def is_authenticated(self):
        return True

    def get_id(self):
        return str(self.id)

    def __str__(self):
        return '<User: {}>'.format(self.nick)

    def __repr__(self):
        return '<User: {}>'.format(self.nick)


class EmailNotify(Base):
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    creation_date = Column(DateTime(), default=datetime.datetime.now())
    token = Column(Unicode(100))
    type = Column(
        Enum('confirmation_reg', 'reset_password', name='notify_type')
    )

    def __str__(self):
        return '<EmailNotify: id user {}, token {}>'.format(
            self.id_user, self.token
        )
