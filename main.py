from __future__ import annotations
from typing import Self, Callable, NoReturn, Any
from dotenv import load_dotenv
from datetime import timedelta
from tqdm import tqdm
import keyboard
import requests
import vlc  # type: ignore
import os

load_dotenv()
if (user := os.environ.get("username")) is None:
    raise ValueError("Username Environment Variable Not Set")
USERNAME: str = user

ANIMETHEMES_URL: str = "https://api.animethemes.moe/search"
ANILIST_URL: str = 'https://graphql.anilist.co'

QUERY: str = '''
query ($username: String) {
    MediaListCollection(userName: $username, type: ANIME, status: COMPLETED, sort: [SCORE_DESC]) {
        lists {
            entries {
                score(format: POINT_10_DECIMAL)
                media {
                    id
                    idMal
                    title {
                        english
                    }
                }
            }
        }
    }
}
'''

class AudioInstance:
    _instance: Self | None = None
    is_playing: bool = False

    def __new__(cls) -> Self:
        if cls._instance == None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "player"): 
            return

        self.vlc_instance = vlc.Instance(["--no-video", "--quiet", "--network-caching=2000"])  # type: ignore

        self.player = self.vlc_instance.media_player_new()  # type: ignore
        self.player.audio_set_volume(70)  # type: ignore

        self.attach_callback_to_event(vlc.EventType.MediaPlayerEndReached, AudioInstance.song_finished_callback)  # type: ignore

    def play_from_url(self, url: str) -> None:
        media = self.vlc_instance.media_new(url)  # type: ignore
        self.player.set_media(media)  # type: ignore

        AudioInstance.is_playing = True
        self.player.play()  # type: ignore

    def attach_callback_to_event(
            self, 
            event_type: vlc.EventType,  # type: ignore
            func: Callable[..., Any], 
            *args: tuple[Any, ...]
        ) -> None:
        self.player.event_manager().event_attach(event_type, func, *args)  # type: ignore

    type Miliseconds = int
    def get_media_duration(self, *, blocking: bool = False) -> Miliseconds:
        while blocking and self.player.get_length() <= 0:  # type: ignore
            pass
        return self.player.get_length()  # type: ignore

    def move_playhead(self, change: Miliseconds) -> None:
        new_time = self.player.get_time() + change  # type: ignore
        new_time = max(min(new_time, self.get_media_duration(blocking=True)), 0)  # type: ignore
        self.player.set_time(new_time)  # type: ignore

    def toggle_pause(self) -> None:
        self.player.pause()  # type: ignore

    def stop_audio(self) -> None:
        self.player.stop()  # type: ignore

    @staticmethod
    def song_finished_callback(_: vlc.EventType):  # type: ignore
        AudioInstance.is_playing = False

def get_animes(username: str) -> dict[str, float]:
    variables: dict[str, str] = {'username': username}
    response = requests.post(ANILIST_URL, json={'query': QUERY, 'variables': variables})
    response.raise_for_status()

    data = response.json()
    lists = data['data']['MediaListCollection']['lists']

    animes: dict[str, float] = {
        entry['media']['title']['english']: entry['score'] 
        for lst in lists 
        for entry in lst['entries']
    }
    return animes

def get_theme_urls(anime_name: str) -> dict[str, str]:
    query: dict[str, str] = {
        "q": anime_name,
        "include[anime]": "animethemes.animethemeentries.videos"
    }

    response = requests.get(ANIMETHEMES_URL, params=query)
    response.raise_for_status()

    data = response.json()
    animes = data["search"]["anime"][0:5]

    urls: dict[str, str] = {
        video["filename"]: video["link"]
        for anime in animes
        for theme in anime['animethemes']
        for entry in theme['animethemeentries']
        for video in entry['videos']
    }
    return urls

def update_timestamp_callback(event: vlc.EventType, pbar: tqdm) -> None:  # type: ignore
    cur_time: AudioInstance.Miliseconds = event.u.new_time  # type: ignore
    pbar.n = cur_time / 1000

    cur_ts = str(timedelta(milliseconds=cur_time)).split('.')[0][-5:] # type: ignore
    total_ts = str(timedelta(seconds=pbar.total)).split('.')[0][-5:] # type: ignore

    pbar.unit = f"{cur_ts}/{total_ts}"
    pbar.refresh()

def create_progress_bar(name: str) -> tqdm[NoReturn]:
    pbar = tqdm(
        total=round(AudioInstance().get_media_duration(blocking=True) / 1000), 
        unit="s", 
        desc=name,
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {unit}"
    )

    AudioInstance().attach_callback_to_event(vlc.EventType.MediaPlayerTimeChanged, update_timestamp_callback, pbar)  # type: ignore
    return pbar

def main():
    # animes = get_animes(USERNAME)
    urls = get_theme_urls("Agents Of The Four Seasons: Dance Of Spring")
    AudioInstance().play_from_url(urls["ShunkashuutouDaikoushaHaruNoMai-ED1"])

    pbar = create_progress_bar("ShunkashuutouDaikoushaHaruNoMai-ED1")

    keyboard.add_hotkey("ctrl+shift+j", AudioInstance().move_playhead, (-10_000,))
    keyboard.add_hotkey("ctrl+shift+k", AudioInstance().toggle_pause)
    keyboard.add_hotkey("ctrl+shift+l", AudioInstance().move_playhead, (10_000,))

    try: 
        while AudioInstance.is_playing: pass

    finally:
        AudioInstance().stop_audio()
        pbar.close()

if __name__ == "__main__":
    main()
