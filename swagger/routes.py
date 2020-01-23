from flask_swagger_ui import get_swaggerui_blueprint

from swagger import views

swagger_blueprint = get_swaggerui_blueprint(
        '/swagger',
        '/swagger/api/',
        config={'app_name': "bulls-and-cows-game"}
)
swagger_blueprint.url_prefix = '/swagger'

views.SwaggerView.register(swagger_blueprint, route_base='/')
