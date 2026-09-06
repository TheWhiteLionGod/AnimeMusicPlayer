from dotenv import load_dotenv
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

is_playing: bool = False

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
    anime = data["search"]["anime"][0]

    urls: dict[str, str] = {
        video["filename"]: video["link"]
        for theme in anime['animethemes']
        for entry in theme['animethemeentries']
        for video in entry['videos']
    }
    return urls

def song_finished_callback(_: vlc.EventType):  # type: ignore
    global is_playing
    is_playing = False

def play_audio(url: str) -> vlc.MediaPlayer:  # type: ignore
    global is_playing
    vlc_instance = vlc.Instance(["--no-video", "--quiet"])  # type: ignore
    player = vlc_instance.media_player_new()  # type: ignore

    media = vlc_instance.media_new(url)  # type: ignore
    player.set_media(media)  # type: ignore

    event_manager = player.event_manager()  # type: ignore
    event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, song_finished_callback)  # type: ignore

    is_playing = True
    player.play()  # type: ignore
    return player  # type: ignore

def main():
    # animes = get_animes(USERNAME)
    urls = get_theme_urls("Tantei Wa Mou, Shindeiru")
    player = play_audio(urls["TanteiWaMouShindeiru-OP1"])  # type: ignore

    try:
        while is_playing:
            pass
    except KeyboardInterrupt:
        player.stop()  # type: ignore

if __name__ == "__main__":
    main()
