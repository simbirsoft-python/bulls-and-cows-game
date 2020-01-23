import pytest
from sqlalchemy_utils import create_database, database_exists, drop_database

from config import get_config
from tests.factories.user_factories import UserFactory
from tests.utils import apply_migrations


@pytest.yield_fixture(scope='session', autouse=True)
def init_db():
    """
    Выполняет инициализацию тестовой БД
    :return:
    """
    config = get_config()

    if database_exists(config.SQLALCHEMY_DATABASE_URI):
        drop_database(config.SQLALCHEMY_DATABASE_URI)

    create_database(config.SQLALCHEMY_DATABASE_URI)
    apply_migrations(config.BASE_DIR)
    yield
    drop_database(config.SQLALCHEMY_DATABASE_URI)


@pytest.fixture(scope="session")
def app():
    from app import app
    return app


@pytest.fixture(scope="session")
def di_services():
    from app import DIServices
    return DIServices


@pytest.fixture(scope="session")
def config():
    return get_config()


@pytest.yield_fixture(scope='function')
def db_session(di_services):
    """
    Инициализирует для каждого теста новую транзацию, а после выполнения теста
    откатывает все сделанные изменения
    """
    session = di_services.db_session_manager()
    session.begin_nested()
    yield session
    session.rollback()
    session.remove()


@pytest.fixture()
def user_factory(db_session):
    UserFactory._meta.sqlalchemy_session = db_session
    return UserFactory


@pytest.fixture()
def user1(user_factory):
    user = user_factory(is_active=True, password='123456')
    return user
