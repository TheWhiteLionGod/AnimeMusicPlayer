import random

def watch_new_anime() -> bool:
    return random.randint(0, 2) >= 1

def watch_prev_anime() -> bool:
    return not watch_new_anime()

def choose_random(lst: list[int]) -> int:
    return random.choice(lst)
