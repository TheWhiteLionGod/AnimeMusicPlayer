from const import *
import requests

def get_animes(username: str) -> dict[int, float]:
    variables: dict[str, str] = {'username': username}
    response = requests.post(ANILIST_URL, json={'query': ANILIST_QUERY, 'variables': variables})
    response.raise_for_status()

    data = response.json()
    lists = data['data']['MediaListCollection']['lists']

    animes: dict[int, float] = {
        entry['media']['id']: entry['score'] 
        for lst in lists 
        for entry in lst['entries']
    }
    return animes

def get_theme_urls(anime_id: int) -> dict[str, str]:
    variables: dict[str, int] = {"id": anime_id}
    response = requests.post(ANIMETHEMES_URL, json={'query': ANIMETHEMES_QUERY, 'variables': variables})
    response.raise_for_status()

    data = response.json()
    themes = data["data"]["findAnimeByExternalSite"][0]["animethemes"]

    return {
        video["filename"]: video["link"]
        for theme in themes
        for entry in theme["animethemeentries"]
        for video in entry["videos"]["nodes"]
    }
