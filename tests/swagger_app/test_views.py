from os.path import join, exists
from unittest import mock

from flask import url_for

from swagger.views import path_to_open_api_spec


def test_api(client):
    expected_data = 'openapi: "3.0.0"'
    with mock.patch('builtins.open', mock.mock_open(read_data=expected_data)):
        res = client.get(url_for('swagger_ui.SwaggerView:api'))

        assert 200 == res.status_code
        assert expected_data == res.data.decode('utf8')


def test_swagger_yaml_path(config):
    path = join(config.BASE_DIR, path_to_open_api_spec)
    assert True is exists(path)
