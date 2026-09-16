from const import SAVE_FILE, SKIP_FILE

def get_watched_animes() -> list[int]:
    with open(SAVE_FILE, 'r') as file:
        animes = file.read()

    return [int(id) for id in animes.split("\n")[:-1]]

def append_watched_animes(anime_id: int) -> None:
    with open(SAVE_FILE, 'a') as file:
        file.write(f"{anime_id}\n")

def get_skip_songs() -> list[str]:
    with open(SKIP_FILE, 'r') as file:
        songs = file.read()

    return songs.split("\n")[:-1]

def append_skip_song(song: str) -> None:
    with open(SKIP_FILE, 'a') as file:
        file.write(song + "\n")
