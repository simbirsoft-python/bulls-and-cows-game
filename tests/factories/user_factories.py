import factory
from factory.alchemy import SQLAlchemyModelFactory

from models import User


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = 'commit'

    nick = factory.Faker('first_name')
    email = factory.Faker('email')
    is_active = factory.Faker('boolean')
    reg_date = factory.Faker('date_time')
