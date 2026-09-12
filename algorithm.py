import random

def watch_new_anime() -> bool:
    return bool(random.randint(0, 1))

def watch_prev_anime() -> bool:
    return not watch_new_anime()

def choose_random(lst: list[str]) -> str:
    return random.choice(lst)
