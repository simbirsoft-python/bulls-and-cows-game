import dependency_injector.containers as di_cnt
import dependency_injector.providers as di_prv
import dramatiq
import itsdangerous
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from flask import Flask
from flask_collect import Collect
from flask_login import LoginManager
from flask_mail import Mail
from pika import PlainCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

import handlers
from config import get_config
from bulls_and_cows import routes as bulls_and_cows_route
from bulls_and_cows import tasks as bulls_and_cows_tasks
from bulls_and_cows.utils import account as bulls_and_cows_utils_account
from swagger import routes as swagger_route
from logger import init_logger
from utils.dramatiq_utils import LazyActor

config = get_config()
init_logger(config.LOGGER_LEVEL)

app = Flask(__name__)
app.config.from_object(config)

collect = Collect(app)

broker = RabbitmqBroker(
    host=config.RABBITMQ_HOST,
    port=config.RABBITMQ_PORT,
    credentials=PlainCredentials(
        config.RABBITMQ_USER, config.RABBITMQ_PASSWORD
    ),
    heartbeat=5,
    connection_attempts=5,
    blocked_connection_timeout=30,
)
broker.add_middleware(handlers.AppContextDramatiqMiddleware(app))
dramatiq.set_broker(broker)
LazyActor.init_all_actors()


# DB session config
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
db_session_manager = scoped_session(sessionmaker(bind=engine))

# flask-login
login_manager = LoginManager(app)
login_manager.login_view = '/account/login/'

mail = Mail(app)

# registration blueprint
app.register_blueprint(bulls_and_cows_route.bulls_and_cows_blueprint)
app.register_blueprint(swagger_route.swagger_blueprint)


# create providers
class DIServices(di_cnt.DeclarativeContainer):
    db_session_manager = di_prv.Object(db_session_manager)
    mail = di_prv.Object(mail)
    url_serializer = di_prv.Singleton(
        itsdangerous.URLSafeSerializer, secret_key=config.SECRET_KEY
    )


# injection
handlers.DIServices.override(DIServices)
bulls_and_cows_tasks.DIServices.override(DIServices)
bulls_and_cows_utils_account.DIServices.override(DIServices)

# add special handlers
login_manager.user_loader(handlers.load_user)
app.before_request(handlers.before_request)
app.teardown_appcontext(handlers.teardown_app_context)
app.errorhandler(404)(handlers.error_404)
app.errorhandler(Exception)(handlers.default_error_handler)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=config.DEBUG)
