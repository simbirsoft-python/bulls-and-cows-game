from os.path import join

from flask_classy import FlaskView

import config


conf = config.get_config()
path_to_open_api_spec = 'swagger/static/swagger.yaml'


class SwaggerView(FlaskView):

    def api(self):
        with open(join(conf.BASE_DIR, path_to_open_api_spec)) as f:
            return f.read()
