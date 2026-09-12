from datetime import timedelta
from tqdm import tqdm
import keyboard
import vlc  # type: ignore

from const import USERNAME
from audio import AudioInstance
import algorithm
import menu
import net
import db

def remove_watched_animes(animes: dict[str, float], watchlist: list[str]) -> dict[str, float]:
    for anime in watchlist:
        animes.pop(anime, None)
    return animes

def update_timestamp_callback(event: vlc.EventType, pbar: tqdm) -> None:  # type: ignore
    cur_time: AudioInstance.Miliseconds = event.u.new_time  # type: ignore
    pbar.n = cur_time / 1000

    cur_ts = str(timedelta(milliseconds=cur_time)).split('.')[0][-5:] # type: ignore
    total_ts = str(timedelta(seconds=pbar.total)).split('.')[0][-5:] # type: ignore

    pbar.unit = f"{cur_ts}/{total_ts}"
    pbar.refresh()

def mainloop(anime: str) -> None:
    urls = net.get_theme_urls(anime)
    AudioInstance().play_from_url(urls["Watatabe-OP1"])  # TODO: Selector

    pbar = menu.create_progress_bar(
        "Watatabe-OP1", 
        round(AudioInstance().get_media_duration(blocking=True) / 1000)
    )

    AudioInstance().attach_callback_to_event(  # type: ignore
        vlc.EventType.MediaPlayerTimeChanged,  # type: ignore
        update_timestamp_callback,  # type: ignore
        pbar  # type: ignore
    )

    try: 
        while AudioInstance().is_playing: pass

    finally:
        AudioInstance().stop_audio()
        pbar.close()

def main():
    watchlist = db.get_watched_animes()
    animes = net.get_animes(USERNAME)

    animes = remove_watched_animes(animes, watchlist)
    print(animes)

    keyboard.add_hotkey("ctrl+shift+j", AudioInstance().move_playhead, (-10_000,))
    keyboard.add_hotkey("ctrl+shift+k", AudioInstance().toggle_pause)
    keyboard.add_hotkey("ctrl+shift+l", AudioInstance().move_playhead, (10_000,))

    try:
        while True: mainloop("This Monster Wants To Eat Me")
    except KeyboardInterrupt:
        # TODO: Handle Exit Program
        pass

if __name__ == "__main__":
    main()
