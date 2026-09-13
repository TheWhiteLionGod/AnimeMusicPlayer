from datetime import timedelta
from tqdm import tqdm
import keyboard
import time
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
    pbar.n = cur_time

    cur_ts = str(timedelta(milliseconds=cur_time)).split('.')[0][-5:] # type: ignore
    total_ts = str(timedelta(milliseconds=pbar.total)).split('.')[0][-5:] # type: ignore

    pbar.unit = f"{cur_ts}/{total_ts}"
    pbar.refresh()

def mainloop(anime: str) -> None:
    urls = net.get_theme_urls(anime)
    for name, url in urls.items():
        AudioInstance().play_from_url(url)

        if not AudioInstance().wait_until_playing(timeout=10.0):
            print(f"TODO: Skipped {name}")
            continue

        pbar = menu.create_progress_bar(
            name, 
            AudioInstance().get_media_duration(blocking=True)
        )

        AudioInstance().attach_callback_to_event(  # type: ignore
            vlc.EventType.MediaPlayerTimeChanged,  # type: ignore
            update_timestamp_callback,  # type: ignore
            pbar  # type: ignore
        )

        try: 
            while AudioInstance().is_playing:
                time.sleep(0.1)

        finally:
            AudioInstance().detach_callback_from_event(  # type: ignore
                vlc.EventType.MediaPlayerTimeChanged  # type: ignore
            )
            AudioInstance().stop_audio()
            pbar.close()

def main():
    watchlist = db.get_watched_animes()
    animes = remove_watched_animes(
        net.get_animes(USERNAME), 
        watchlist
    )

    keyboard.add_hotkey("ctrl+shift+h", AudioInstance().set_playhead, (0,))
    keyboard.add_hotkey("ctrl+shift+j", AudioInstance().move_playhead, (-10_000,))
    keyboard.add_hotkey("ctrl+shift+k", AudioInstance().toggle_pause)
    keyboard.add_hotkey("ctrl+shift+l", AudioInstance().move_playhead, (10_000,))
    keyboard.add_hotkey("ctrl+shift+;", AudioInstance().stop_audio)

    try:
        while True: 
            anime = max(animes, key=lambda k: animes[k]) \
                if algorithm.watch_new_anime() else \
                algorithm.choose_random(watchlist)

            mainloop(anime)
            if anime not in watchlist: 
                db.append_watched_animes(anime)
                animes.pop(anime)

    except KeyboardInterrupt:
        # TODO: Handle Exit Program
        pass

if __name__ == "__main__":
    main()
