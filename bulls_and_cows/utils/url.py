from urllib.parse import urlparse, parse_qs, urljoin

from flask import url_for, redirect, request


def is_safe_url(target) -> bool:
    """
    Проверяет, что url из target ссылается на текущий сервер.
    Необходима для обеспечения безопасности, чтобы пользователь не был
    перенаправлен на вредоносный сайт.
    :param target: проверяемый url
    :return: результат проверки
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ('http', 'https') and
            ref_url.netloc == test_url.netloc)


def get_redirect_back(redirect_back_argument) -> str or None:
    """
    Извлекает из запроса url на который необходимо перенаправить
    пользователя
    :param redirect_back_argument:
    :return: url or None
    """
    referrer = parse_qs(urlparse(request.referrer).query).get(
        redirect_back_argument, [None]
    )[0]
    for target in request.values.get(redirect_back_argument), referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def redirect_back(redirect_back_argument, endpoint, **values):
    """
    Перенаправляет пользователя на страницу на которой он находился до того
    как его авторизация истекла
    :param redirect_back_argument:
    :param endpoint: точка куда будет перенаправлен пользователь, если
    back url не будет найден
    :param values: дополнительные аргументы для функции flask.url_for
    :return: редирект
    """
    target = get_redirect_back(redirect_back_argument)
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)
