import dramatiq


class LazyActor:
    """
    Обертка над dramatiq.Actor, которая позволяет выполнять ленивую
    инициализацию, чтобы можно было объявлять задачи до создания инстанса
    брокера.
    """
    __slots__ = ('orig_func', 'dec_args', 'dec_kwargs', 'actor',)

    actors = []

    def __init__(self, orig_func, dec_args, dec_kwargs):
        self.orig_func = orig_func
        self.dec_args = tuple() if dec_args is None else dec_args
        self.dec_kwargs = {} if dec_kwargs is None else dec_kwargs
        self.actors.append(self)

        self.actor = None

    def __call__(self, *args, **kwargs):
        return self.orig_func(*args, **kwargs)

    def init_actor(self):
        """
        Инициализирует dramatiq actor
        """
        self.actor = dramatiq.actor(*self.dec_args, **self.dec_kwargs)(
            self.orig_func
        )

    def send(self, *args, **kwargs):
        """
        Выполняет асинхронную отправку сообщения, которое запустит выполнение
        задачи в воркере
        :param args: позиционные аргументы для вызываемой задачи
        :param kwargs: именованные аргументы для вызываемой задачи
        :return:
        """
        if self.actor is None:
            self.init_actor()

        return self.actor.send(*args, **kwargs)

    @classmethod
    def init_all_actors(cls):
        """
        Выполняет инициализацию всех actor, которые были продекорированны
        lazy_actor
        """
        for i in cls.actors:
            i.init_actor()


def lazy_actor(*args, **kwargs):
    """
    Декоратор, который позволяет лениво инициализировать задачи помеченные
    декоратором dramatiq.actor
    :param args: позиционные аргументы для декоратора
    :param kwargs: именованные аргументы для декоратора
    :return: декоратор
    """
    def decorator(orig_func):
        return LazyActor(orig_func, args, kwargs)
    return decorator
