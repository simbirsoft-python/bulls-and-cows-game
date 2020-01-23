def collect_filter(blueprints: tuple, excluded_blueprints: tuple):
    """
    Фильтрует blueprint в которых не нужно искать статику
    :param blueprints: список всех найденных в приложении blueprint
    :param excluded_blueprints: список имен blueprint, которые должны быть
    исключены
    :return: отфильрованный список
    """
    return filter(
        lambda i: False if i.name in excluded_blueprints else True, blueprints
    )
