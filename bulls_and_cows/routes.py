from os.path import join

from flask import Blueprint

import config
from bulls_and_cows import views

conf = config.get_config()

bulls_and_cows_blueprint = Blueprint(
    'bulls_and_cows', __name__,
    template_folder=join(conf.BASE_DIR, 'bulls_and_cows/templates'),
    static_url_path='/static/bulls_and_cows', static_folder='static'
)

views.BullsAndCowsView.register(bulls_and_cows_blueprint, route_base='/')
views.AccountView.register(bulls_and_cows_blueprint)


