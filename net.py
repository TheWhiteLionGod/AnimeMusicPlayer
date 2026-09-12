from const import *
import requests

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
