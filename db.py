from const import SAVE_FILE

def get_watched_animes() -> list[str]:
    with open(SAVE_FILE, 'r') as file:
        animes = file.read()

    return animes.split()

def append_watched_animes(anime: str) -> None:
    with open(SAVE_FILE, 'a') as file:
        file.write(anime + "\n")