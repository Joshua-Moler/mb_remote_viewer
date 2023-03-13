import random
from random import choice
import sys


def get_random_bool():
    return random.choice([True, False])


def pump_start(p=None):
    return (get_random_bool(), p)


def pump_stop(p=None):
    return (get_random_bool(), p)
