from sqlalchemy import Column, ForeignKey, Integer, Unicode, DateTime, Boolean
from sqlalchemy.orm import relationship, backref

from models.base import Base


class Game(Base):
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    secret = Column(Unicode(length=4))
    date = Column(DateTime())
    completed = Column(Boolean(), default=False)

    moves = relationship('Move', backref=backref('game'))

    def __str__(self):
        return '<Game: {}, {}>'.format(self.secret, self.completed)

    def __repr__(self):
        return '<Game: {}, {}>'.format(self.secret, self.completed)


class Move(Base):
    id = Column(Integer, primary_key=True)
    id_game = Column(Integer, ForeignKey('game.id', ondelete='CASCADE'))
    answer = Column(Unicode(length=4))

    def __str__(self):
        return '<Move: {}>'.format(self.answer)

    def __repr__(self):
        return '<Move: {}>'.format(self.answer)
