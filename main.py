from dotenv import load_dotenv
from typing import Self
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
        self.vlc_instance = vlc.Instance(["--no-video", "--quiet", "--network-caching=2000"])  # type: ignore

        self.player = self.vlc_instance.media_player_new()  # type: ignore
        self.player.audio_set_volume(70)  # type: ignore

        event_manager = self.player.event_manager()  # type: ignore
        event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, AudioInstance.song_finished_callback)  # type: ignore

    def play_from_url(self, url: str) -> None:
        media = self.vlc_instance.media_new(url)  # type: ignore
        self.player.set_media(media)  # type: ignore

        AudioInstance.is_playing = True
        self.player.play()  # type: ignore

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
    
def main():
    # animes = get_animes(USERNAME)
    urls = get_theme_urls("My Teen Romantic Comedy SNAFU")
    AudioInstance().play_from_url(urls["OreGairu-OP1"])

    try:
        while AudioInstance.is_playing:
            pass
    except KeyboardInterrupt:
        AudioInstance().stop_audio()

if __name__ == "__main__":
    main()
