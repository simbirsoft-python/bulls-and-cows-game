import random


def generate_secret():
    return ''.join(map(str, random.sample(range(9), 4)))


def count_bulls_cows(secret, number):
    """
    Считает количество быков и коров
    :param secret: число загаданное компьютером
    :param number: число введеное пользователем
    """
    cows, bulls = 0, 0
    for i in range(len(secret)):
        if secret[i] == number[i]:
            bulls += 1
        else:
            cows += 1 if number[i] in secret else 0
    return bulls, cows
