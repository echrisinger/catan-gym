from random import shuffle


def copy_and_shuffle[T](l: list[T]) -> list[T]:
    res = l.copy()
    shuffle(res)
    return res