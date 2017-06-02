from time import sleep
from random import randint


def countdown():
    """
    Счетчик-имитатор длительной по времени задачи.
    """
    sleep(randint(0, 10))
